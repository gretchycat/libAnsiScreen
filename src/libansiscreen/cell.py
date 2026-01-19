from dataclasses import dataclass
from typing import Optional

from .color.rgb import Color
from .color.palette import create_ansi_16_palette

# ----------------------------------------------------------------------
# ANSI attributes (bitmask)
# ----------------------------------------------------------------------

ATTR_BOLD       = 0b00000001
ATTR_FAINT      = 0b00000010
ATTR_ITALIC     = 0b00000100
ATTR_UNDERLINE  = 0b00001000
ATTR_BLINK      = 0b00010000
ATTR_INVERSE    = 0b00100000
ATTR_CONCEAL    = 0b01000000
ATTR_STRIKE     = 0b10000000

# ----------------------------------------------------------------------
# Default ANSI colors
# ----------------------------------------------------------------------

_ANSI16 = create_ansi_16_palette()
DEFAULT_FG = _ANSI16.index_to_rgb(7)   # light gray
DEFAULT_BG = _ANSI16.index_to_rgb(0)   # black


# ----------------------------------------------------------------------
# Cell
# ----------------------------------------------------------------------

@dataclass(slots=True)
class Cell:
    """
    Represents a single terminal cell.

    fg/bg are concrete Colors by default (ANSI reset state).
    Use fg=None or bg=None explicitly to indicate inheritance.
    """

    char: str = None
    fg: Optional[Color] = None #DEFAULT_FG
    bg: Optional[Color] = DEFAULT_BG
    attrs: int = 0

    # --------------------------------------------------------------
    # Comparison helpers
    # --------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return NotImplemented
        return (
            self.char == other.char
            and self.fg == other.fg
            and self.bg == other.bg
            and self.attrs == other.attrs
        )

    def diff(self, other: "Cell") -> int:
        """
        Return a bitmask indicating which fields differ.

        Bit 0: character
        Bit 1: foreground color
        Bit 2: background color
        Bit 3: attributes
        """
        mask = 0

        if self.char != other.char:
            mask |= 0b0001
        if self.fg != other.fg:
            mask |= 0b0010
        if self.bg != other.bg:
            mask |= 0b0100
        if self.attrs != other.attrs:
            mask |= 0b1000

        return mask

    # --------------------------------------------------------------
    # Convenience predicates
    # --------------------------------------------------------------

    def char_changed(self, other: "Cell") -> bool:
        return self.char != other.char

    def fg_changed(self, other: "Cell") -> bool:
        return self.fg != other.fg

    def bg_changed(self, other: "Cell") -> bool:
        return self.bg != other.bg

    def attrs_changed(self, other: "Cell") -> bool:
        return self.attrs != other.attrs

    def copy(self) -> "Cell":
        return Cell(
            char=self.char,
            fg=self.fg,
            bg=self.bg,
            attrs=self.attrs,
        )
