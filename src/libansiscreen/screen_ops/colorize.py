from typing import Iterable, Optional

from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# ------------------------------------------------------------
# Horizontal gradient (left → right)
# ------------------------------------------------------------

def apply_hgrad(
    screen: Screen,
    gradient: list[Color],
    *,
    foreground: bool = True,
    background: bool = False,
    only_if_set: bool = True,
    tint: Optional[float] = None,
) -> None:
    width = screen.width
    height = screen.height
    if width <= 1 or not gradient:
        return
    n = len(gradient)
    for y in range(height):
        for x in range(width):
            cell = screen.get_cell(x, y)
            if cell is None:
                continue
            if only_if_set and cell.char is None:
                continue
            idx = int(x * (n - 1) / (width - 1))
            color = gradient[idx]
            if foreground:
                cell.fg = color if tint is None else color.blend(cell.fg,tint
            if background:
                cell.bg = color if tint is None else color.blend(cell.bg,tint)

# ------------------------------------------------------------
# Vertical gradient (top → bottom)
# ------------------------------------------------------------

def apply_vgrad(
    screen: Screen,
    gradient: list[Color],
    *,
    foreground: bool = True,
    background: bool = False,
    only_if_set: bool = True,
    tint: Optional[float] = None,
) -> None:
    width = screen.width
    height = screen.height
    if height <= 1 or not gradient:
        return
    n = len(gradient)
    for y in range(height):
        idx = int(y * (n - 1) / (height - 1))
        color = gradient[idx]
        for x in range(width):
            cell = screen.get_cell(x, y)
            if cell is None:
                continue
            if only_if_set and cell.char is None:
                continue
            if foreground:
                cell.fg = color if tint is None else color.blend(cell.fg,tint
            if background:
                cell.bg = color if tint is None else color.blend(cell.bg,tint)

# ------------------------------------------------------------
# Diagonal gradient (top-left → bottom-right)
# ------------------------------------------------------------

def apply_dgrad(
    screen: Screen,
    gradient: list[Color],
    *,
    foreground: bool = True,
    background: bool = False,
    only_if_set: bool = True,
    tint: Optional[float] = None,
    direction: str = "tlbr",
) -> None:
    width = screen.width
    height = screen.height
    if width <= 1 or height <= 1 or not gradient:
        return
    n = len(gradient)
    denom = (width - 1) + (height - 1)
    if denom <= 0:
        return
    for y in range(height):
        for x in range(width):
            cell = screen.get_cell(x, y)
            if cell is None:
                continue
            if only_if_set and cell.char is None:
                continue
            if direction == "trbl":
                d = (width - 1 - x) + y
            else:
                d = x + y
            idx = int(d * (n - 1) / denom)
            color = gradient[idx]
            if foreground:
                cell.fg = color if tint is None else color.blend(cell.fg,tint)
            if background:
                cell.bg = color if tint is None else color.blend(cell.bg,tint)


# ------------------------------------------------------------
# Words / sequential gradient
# ------------------------------------------------------------

def apply_words(
    screen: Screen,
    gradient: list[Color],
    *,
    foreground: bool = True,
    background: bool = False,
    tint: Optional[float] = None,
) -> None:
    if not gradient:
        return
    n = len(gradient)
    idx = 0
    for y in range(screen.height):
        for x in range(screen.width):
            cell = screen.get_cell(x, y)
            if cell is None or cell.char is None:
                continue
            if cell.char==' ':
                idx=0
                continue
            color = gradient[min(idx, n - 1)]
            if foreground:
                cell.fg = color if tint is None else color.blend(cell.fg,tint)
            if background:
                cell.bg = color if tint is None else color.blend(cell.bg,tint)
            idx += 1

# ------------------------------------------------------------
# Dispatcher
# ------------------------------------------------------------

def colorize(
    screen: Screen,
    gradient: Iterable[Color],
    *,
    mode: str = "hgrad",
    foreground: bool = True,
    background: bool = False,
    only_if_set: bool = True,
    tint: Optional[float] = None,
    direction: str = "tlbr",
) -> None:
    """
    Apply a color gradient to the screen.
    """

    gradient = list(gradient)
    mode = mode.lower().strip()

    if mode in ("hgrad", "horizontal"):
        apply_hgrad(
            screen,
            gradient,
            foreground=foreground,
            background=background,
            only_if_set=only_if_set,
            tint=tint,
        )

    elif mode in ("vgrad", "vertical"):
        apply_vgrad(
            screen,
            gradient,
            foreground=foreground,
            background=background,
            only_if_set=only_if_set,
            tint=tint,
        )

    elif mode in ("dgrad", "diag", "diagonal"):
        apply_dgrad(
            screen,
            gradient,
            foreground=foreground,
            background=background,
            only_if_set=only_if_set,
            tint=tint,
            direction=direction,
        )

    elif mode in ("words",):
        apply_words(
            screen,
            gradient,
            foreground=foreground,
            background=background,
            tint=tint,
        )

    else:
        raise ValueError(f"Unknown colorize mode: {mode}")

#2522039396
#yfu4qp

