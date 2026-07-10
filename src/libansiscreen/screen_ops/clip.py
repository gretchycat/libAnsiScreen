from __future__ import annotations
from typing import Optional, Iterable, Union, Tuple, Set
from ..cell import Cell
from ..color.rgb import Color
from ..framebuffer import frameBuffer
# Box is (x, y, width, height)
Box = Tuple[int, int, int, int]

# ------------------------------------------------------------
# Internal helper: normalize legacy tuples to Box
# ------------------------------------------------------------
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

    Clearing means:
      - char = None
      - fg   = None
      - bg   = color 0,0,0
      - attrs = 0

    If box is None, clears the entire fb.
    """

    if box is None:
        x0, y0 = 0, 0
        w, h = fb.width, fb.height
    else:
        if type(box)==tuple:
            x0, y0, w, h = box #box.x, box.y, box.width, box.height
        else:
            x0, y0, w, h = box.x, box.y, box.width, box.height

    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if fb.get_cell(x, y) is not None:
                fb.set_cell(
                    x, y,
                    Cell(
                        char=None,
                        fg=None,
                        bg=None,
                        attrs=0,
                    )
                )

def copy(fb, box: Optional[Box] = None) -> frameBuffer:
    """
    Copy a region of a fb into a new fb.
    If box is None, returns a full deep copy of the fb.
    Box is defined as (x, y, width, height).
    """
    if box is None:
        box=(0,0,fb.width,fb.height)
    x0, y0, w, h = box
    if w <= 0 and h <= 0:
        raise ValueError("Box width and height must be positive")
    if w <= 0:
        raise ValueError("Box width must be positive")
    new_fb = frameBuffer(w)
    for dy in range(h):
        sy = y0 + dy
        if sy < 0 or sy >= fb.height:
            continue
        for dx in range(w):
            sx = x0 + dx
            if sx < 0 or sx >= fb.width:
                continue
            cell = fb.get_cell(sx, sy)
            new_fb.set_cell(dx, dy, cell.copy())
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

    for sy in range(max_h):
        dy = dst_y + sy

        # Grow destination vertically if needed
        if dy >= dst.height:
            dst._ensure_row(dy + 1)

        for sx in range(max_w):
            dx = dst_x + sx
            if dx < 0 or dx >= dst.width:
                continue

            src_cell = src.get_cell(sx, sy)
            dst_cell = dst.get_cell(dx, dy)
            if not dst_cell:
                dst_cell=Cell()
                dst.set_cell(dx,dy,dst_cell)
            if src_cell:
                # Character
                if (
                    src_cell.char is not None
                    and src_cell.char not in transparent_char
                ):
                    dst_cell.char = src_cell.char

                # Foreground
                if (
                    not transparent_fg
                    and src_cell.fg is not None
                ):
                    dst_cell.fg = src_cell.fg

                # Background
                if (
                    not transparent_bg
                    and src_cell.bg is not None
                ):
                    dst_cell.bg = src_cell.bg

                # Attributes
                if (
                    not transparent_attrs
                    and src_cell.attrs is not None
                ):
                    dst_cell.attrs = src_cell.attrs
