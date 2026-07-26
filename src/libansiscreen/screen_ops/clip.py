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
    Clear cells in `fb` inside `box` using high-performance binary memory slicing.
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

    empty_cell_bytes = bytes(CELL_SIZE)
    for dy in range(h):
        sy = y0 + dy
        if 0 <= sy < fb.height and 0 <= x0 < fb.width:
            copy_cols = min(w, fb.width - x0)
            offset = fb._cell_offset(x0, sy)
            fb.buffer[offset : offset + copy_cols * CELL_SIZE] = empty_cell_bytes * copy_cols


def copy(fb: frameBuffer, box: Optional[Box] = None) -> frameBuffer:
    """
    Copy a region of a fb into a new fb using binary memory buffer slicing.
    If box is None, returns a full deep copy of the fb.
    Box is defined as (x, y, width, height).
    """
    if box is None:
        new_fb = frameBuffer(fb.width, height=fb.height)
        new_fb.buffer = bytearray(fb.buffer)
        new_fb.image_registry = copy_module.copy(fb.image_registry)
        return new_fb

    x0, y0, w, h = box
    if w <= 0 and h <= 0:
        raise ValueError("Box width and height must be positive")
    if w <= 0:
        raise ValueError("Box width must be positive")
    if h <= 0:
        raise ValueError("Box height must be positive")

    new_fb = frameBuffer(w, height=h)
    if x0 >= fb.width or y0 >= fb.height:
        return new_fb

    copy_cols = min(w, fb.width - x0) if x0 >= 0 else 0
    if copy_cols <= 0:
        return new_fb

    copy_bytes = copy_cols * CELL_SIZE
    for dy in range(h):
        sy = y0 + dy
        if 0 <= sy < fb.height and 0 <= dy < h:
            src_off = (sy * fb.width + max(0, x0)) * CELL_SIZE
            dst_off = (dy * w) * CELL_SIZE
            new_fb.buffer[dst_off : dst_off + copy_bytes] = fb.buffer[src_off : src_off + copy_bytes]

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
    Paste src fb into dst fb with transparency rules directly in binary buffer.
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

    # Selective field copy with transparency rules directly in binary buffer
    transparent_cps = {ord(c) for c in transparent_char if len(c) == 1}

    for sy in range(max_h):
        dy = dst_y + sy
        if dy < 0:
            continue
        dst._ensure_row(dy)

        for sx in range(max_w):
            dx = dst_x + sx
            if dx < 0 or dx >= dst.width:
                continue

            src_off = (sy * src.width + sx) * CELL_SIZE
            dst_off = (dy * dst.width + dx) * CELL_SIZE

            (
                s_cp, s_fr, s_fg, s_fb, s_ff,
                s_br, s_bg, s_bb, s_bf,
                s_attrs, s_tile
            ) = CELL_STRUCT.unpack_from(src.buffer, src_off)

            if s_tile == FLAG_CELL_NULL:
                continue

            (
                d_cp, d_fr, d_fg, d_fb, d_ff,
                d_br, d_bg, d_bb, d_bf,
                d_attrs, d_tile
            ) = CELL_STRUCT.unpack_from(dst.buffer, dst_off)

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
                dst.buffer, dst_off,
                d_cp, d_fr, d_fg, d_fb, d_ff,
                d_br, d_bg, d_bb, d_bf,
                d_attrs, d_tile
            )


def tile(fb: frameBuffer, tl: frameBuffer) -> None:
    """
    Tile a sub-frameBuffer (tl) across fb.
    """
    for y in range(0, fb.height, tl.height):
        for x in range(0, fb.width, tl.width):
            paste(fb, tl, box=(x, y, tl.width, tl.height))
