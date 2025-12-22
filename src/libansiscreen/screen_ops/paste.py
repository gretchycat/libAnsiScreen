from __future__ import annotations

from typing import Optional, Tuple, Set

from libansiscreen.screen import Screen
from libansiscreen.cell import Cell


Box = Tuple[int, int, Optional[int], Optional[int]]


def paste(
    dst: Screen,
    src: Screen,
    *,
    box: Optional[Box] = None,
    transparent_char: Optional[Set[str]] = None,
    transparent_fg: bool = False,
    transparent_bg: bool = False,
    transparent_attrs: bool = False,
) -> None:
    """
    Paste src screen into dst screen with transparency rules.
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
            dst.ensure_height(dy + 1)

        for sx in range(max_w):
            dx = dst_x + sx
            if dx < 0 or dx >= dst.width:
                continue

            src_cell = src.get_cell(sx, sy)
            dst_cell = dst.get_cell(dx, dy)

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
