from __future__ import annotations
import copy as copy_module
from typing import Optional, Iterable, Union, Tuple, Set
from ..cell import Cell
from ..color.rgb import Color
from ..framebuffer import frameBuffer
from ..binary_cell import CELL_SIZE, CELL_STRUCT, FLAG_COLOR_SET, FLAG_CELL_NULL

# Box is (x, y, width, height)
Box = Tuple[int, int, int, int]


def _coerce_box(box: Optional[Union[Box, Iterable[int]]]) -> Optional[Box]:
    if box is None:
        return None
    if isinstance(box, Box):
        return box
    if isinstance(box, (tuple, list)) and len(box) == 4:
        return Box(*box)
    raise TypeError(f"Invalid box type: {type(box)}")


def clear(fb: frameBuffer, box: Optional[Union[Box, tuple]] = None) -> None:
    """
    Clear cells in `fb` inside `box`.
    If box is None, clears the entire fb.
    """
    if box is None:
        fb.cls()
        return

    if type(box) == tuple:
        x0, y0, w, h = box
    else:
        x0, y0, w, h = box.x, box.y, box.width, box.height

    if w <= 0 or h <= 0:
        return

    if x0 <= 0 and y0 <= 0 and w >= fb.width and h >= fb.height:
        fb.cls()
        return

    if fb.use_binary:
        empty_cell_bytes = bytes(CELL_SIZE)
        for dy in range(h):
            sy = y0 + dy
            if 0 <= sy < fb.height and 0 <= x0 < fb.width:
                copy_cols = min(w, fb.width - x0)
                offset = fb._cell_offset(x0, sy)
                fb._buffer[offset : offset + copy_cols * CELL_SIZE] = empty_cell_bytes * copy_cols
    else:
        for dy in range(h):
            sy = y0 + dy
            if 0 <= sy < len(fb._rows) and 0 <= x0 < fb.width:
                row = fb._rows[sy]
                for dx in range(min(w, fb.width - x0)):
                    row[x0 + dx] = Cell()


def copy(fb: frameBuffer, box: Optional[Box] = None) -> frameBuffer:
    """
    Copy a region of a fb into a new fb.
    If box is None, returns a full deep copy of the fb.
    Box is defined as (x, y, width, height).
    """
    if box is None:
        new_fb = frameBuffer(fb.width, height=fb.height, use_binary=fb.use_binary)
        if fb.use_binary:
            new_fb._buffer = bytearray(fb._buffer)
        else:
            new_fb._rows = [[c.copy() if c is not None else None for c in row] for row in fb._rows]
        new_fb.image_registry = copy_module.copy(fb.image_registry)
        return new_fb

    x0, y0, w, h = box
    if w <= 0 and h <= 0:
        raise ValueError("Box width and height must be positive")
    if w <= 0:
        raise ValueError("Box width must be positive")
    if h <= 0:
        raise ValueError("Box height must be positive")

    new_fb = frameBuffer(w, height=h, use_binary=fb.use_binary)
    new_fb.image_registry = copy_module.copy(fb.image_registry)
    if x0 >= fb.width or y0 >= fb.height:
        return new_fb

    if fb.use_binary:
        copy_cols = min(w, fb.width - x0) if x0 >= 0 else 0
        if copy_cols <= 0:
            return new_fb

        copy_bytes = copy_cols * CELL_SIZE
        for dy in range(h):
            sy = y0 + dy
            if 0 <= sy < fb.height and 0 <= dy < h:
                src_off = (sy * fb.width + max(0, x0)) * CELL_SIZE
                dst_off = (dy * w) * CELL_SIZE
                new_fb._buffer[dst_off : dst_off + copy_bytes] = fb._buffer[src_off : src_off + copy_bytes]
    else:
        for dy in range(h):
            sy = y0 + dy
            if 0 <= sy < len(fb._rows):
                src_row = fb._rows[sy]
                dst_row = new_fb._rows[dy]
                for dx in range(w):
                    sx = x0 + dx
                    if 0 <= sx < fb.width:
                        c = src_row[sx]
                        dst_row[dx] = c.copy() if c is not None else None

    return new_fb


def cut(fb: frameBuffer, box: Optional[Box] = None) -> frameBuffer:
    """
    Cut a region from a fb: copy it, then clear the original region.
    If box is None, cuts the entire fb.
    """
    buf = copy(fb, box)
    clear(fb, box)
    return buf


def paste(
    dst: frameBuffer,
    src: frameBuffer,
    *,
    box: Optional[Box] = None,
    transparent_char: Optional[Set[str]] = None,
    transparent_fg: bool = False,
    transparent_bg: bool = False,
    transparent_attrs: bool = False,
) -> None:
    """
    Paste src fb into dst fb with transparency rules.
    When src cell has fg=None or bg=None, destination colors are preserved.
    """
    if transparent_char is None:
        transparent_char = set()

    # Destination origin and limits
    if box is None:
        dst_x = 0
        dst_y = 0
        max_w = min(src.width, dst.width)
        max_h = src.height
    else:
        dst_x, dst_y, w, h = box
        max_w = (
            min(src.width, dst.width - dst_x)
            if w is None
            else min(w, src.width)
        )
        max_h = src.height if h is None else min(h, src.height)

    if max_w <= 0 or max_h <= 0:
        return

    # Sync image registry entries from src to dst
    for img_id, entry in src.image_registry._images.items():
        if dst.image_registry.get(img_id) is None:
            dst.image_registry._images[img_id] = entry

    if dst.use_binary and src.use_binary:
        transparent_cps = {ord(c) for c in transparent_char if len(c) == 1}
        has_transparency = bool(transparent_cps or transparent_fg or transparent_bg or transparent_attrs)

        min_sx = max(0, -dst_x)
        min_dx = max(0, dst_x)
        cols_to_copy = min(max_w - min_sx, dst.width - min_dx)

        if cols_to_copy > 0:
            end_y = dst_y + max_h - 1
            if end_y >= 0:
                dst._ensure_row(end_y)

                if not has_transparency:
                    src_buf = src._buffer
                    # Fast C-level validation of full fg/bg color presence and non-null status
                    if 0 not in src_buf[7::CELL_SIZE] and 0 not in src_buf[11::CELL_SIZE] and 0x80 not in src_buf[15::CELL_SIZE]:
                        # Ultra-fast single contiguous block copy (when pasting full row widths)
                        if min_sx == 0 and min_dx == 0 and cols_to_copy == src.width and cols_to_copy == dst.width and dst_y >= 0:
                            dst_start = (dst_y * dst.width) * CELL_SIZE
                            total_bytes = max_h * src.width * CELL_SIZE
                            dst._buffer[dst_start : dst_start + total_bytes] = src_buf[0 : total_bytes]
                            return

                        # Fast row-by-row slice copy
                        row_bytes = cols_to_copy * CELL_SIZE
                        for sy in range(max_h):
                            dy = dst_y + sy
                            if dy < 0:
                                continue
                            src_start = (sy * src.width + min_sx) * CELL_SIZE
                            dst_start = (dy * dst.width + min_dx) * CELL_SIZE
                            dst._buffer[dst_start : dst_start + row_bytes] = src_buf[src_start : src_start + row_bytes]
                        return

        for sy in range(max_h):
            dy = dst_y + sy
            if dy < 0:
                continue
            dst._ensure_row(dy)

            if cols_to_copy <= 0:
                continue

            if not has_transparency:
                src_start = (sy * src.width + min_sx) * CELL_SIZE
                dst_start = (dy * dst.width + min_dx) * CELL_SIZE
                row_bytes = cols_to_copy * CELL_SIZE
                src_chunk = src._buffer[src_start : src_start + row_bytes]

                can_fast_copy = True
                b = memoryview(src_chunk)
                for i in range(0, row_bytes, CELL_SIZE):
                    if not (b[i + 7] & FLAG_COLOR_SET and b[i + 11] & FLAG_COLOR_SET and not (b[i + 15] & 0x80)):
                        can_fast_copy = False
                        break

                if can_fast_copy:
                    dst._buffer[dst_start : dst_start + row_bytes] = src_chunk
                    continue

            for dx_idx in range(cols_to_copy):
                sx = min_sx + dx_idx
                dx = min_dx + dx_idx

                src_off = (sy * src.width + sx) * CELL_SIZE
                dst_off = (dy * dst.width + dx) * CELL_SIZE

                (
                    s_cp, s_fr, s_fg, s_fb, s_ff,
                    s_br, s_bg, s_bb, s_bf,
                    s_attrs, s_tile
                ) = CELL_STRUCT.unpack_from(src._buffer, src_off)

                if s_tile == FLAG_CELL_NULL:
                    continue

                (
                    d_cp, d_fr, d_fg, d_fb, d_ff,
                    d_br, d_bg, d_bb, d_bf,
                    d_attrs, d_tile
                ) = CELL_STRUCT.unpack_from(dst._buffer, dst_off)

                # Character update
                if s_cp != 0 and s_cp not in transparent_cps:
                    d_cp = s_cp

                # Foreground update (only copy if src foreground is set, i.e. not None)
                if not transparent_fg and (s_ff & FLAG_COLOR_SET):
                    d_fr, d_fg, d_fb, d_ff = s_fr, s_fg, s_fb, s_ff

                # Background update (only copy if src background is set, i.e. not None)
                if not transparent_bg and (s_bf & FLAG_COLOR_SET):
                    d_br, d_bg, d_bb, d_bf = s_br, s_bg, s_bb, s_bf

                # Attributes update
                if not transparent_attrs:
                    d_attrs = s_attrs

                d_tile = 0  # Clear null flag

                CELL_STRUCT.pack_into(
                    dst._buffer, dst_off,
                    d_cp, d_fr, d_fg, d_fb, d_ff,
                    d_br, d_bg, d_bb, d_bf,
                    d_attrs, d_tile
                )
    elif not dst.use_binary and not src.use_binary:
        for sy in range(max_h):
            dy = dst_y + sy
            if dy < 0:
                continue
            dst._ensure_row(dy)

            src_row = src._rows[sy] if sy < len(src._rows) else None
            dst_row = dst._rows[dy]

            if src_row is None:
                continue

            for sx in range(max_w):
                dx = dst_x + sx
                if dx < 0 or dx >= dst.width:
                    continue

                sc = src_row[sx]
                if sc is None:
                    continue

                dc = dst_row[dx] or Cell()

                new_char = dc.char
                if sc.char is not None and sc.char not in transparent_char:
                    new_char = sc.char

                new_fg = dc.fg
                if not transparent_fg and sc.fg is not None:
                    new_fg = sc.fg

                new_bg = dc.bg
                if not transparent_bg and sc.bg is not None:
                    new_bg = sc.bg

                new_attrs = dc.attrs
                if not transparent_attrs:
                    new_attrs = sc.attrs

                new_img = sc.image if sc.image is not None else dc.image

                dst_row[dx] = Cell(
                    char=new_char,
                    fg=new_fg,
                    bg=new_bg,
                    attrs=new_attrs,
                    image=new_img,
                    tile_x=sc.tile_x,
                    tile_y=sc.tile_y,
                )
    else:
        for sy in range(max_h):
            dy = dst_y + sy
            if dy < 0:
                continue
            dst._ensure_row(dy)

            for sx in range(max_w):
                dx = dst_x + sx
                if dx < 0 or dx >= dst.width:
                    continue

                sc = src.get_cell(sx, sy)
                if sc is None:
                    continue

                dc = dst.get_cell(dx, dy) or Cell()

                new_char = dc.char
                if sc.char is not None and sc.char not in transparent_char:
                    new_char = sc.char

                new_fg = dc.fg
                if not transparent_fg and sc.fg is not None:
                    new_fg = sc.fg

                new_bg = dc.bg
                if not transparent_bg and sc.bg is not None:
                    new_bg = sc.bg

                new_attrs = dc.attrs
                if not transparent_attrs:
                    new_attrs = sc.attrs

                new_img = sc.image if sc.image is not None else dc.image

                dst.set_cell(
                    dx,
                    dy,
                    Cell(
                        char=new_char,
                        fg=new_fg,
                        bg=new_bg,
                        attrs=new_attrs,
                        image=new_img,
                        tile_x=sc.tile_x,
                        tile_y=sc.tile_y,
                    ),
                )


def tile(fb: frameBuffer, tl: frameBuffer) -> None:
    """
    Tile a sub-frameBuffer (tl) across fb.
    """
    for y in range(0, fb.height, tl.height):
        for x in range(0, fb.width, tl.width):
            paste(fb, tl, box=(x, y, tl.width, tl.height))

