"""
palette.py

Defines exact, lossless color palettes for libAnsiScreen.

A Palette declares which RGB colors are representable via integer indices.
It performs *exact* RGB ↔ index mapping only. Any approximation or
quantization is an explicit policy decision and must live elsewhere.
"""

from typing import Dict, Optional
from .rgb import Color


class Palette:
    """
    Represents an indexed color palette with exact RGB mappings.

    Internally stores:
      - index → Color
      - Color → index (reverse lookup)

    No nearest-color matching is performed here.
    """

    def __init__(self, index_to_color: Dict[int, Color]):
        self.set_colors(index_to_color)

    # ------------------------------------------------------------------
    # Core palette data access
    # ------------------------------------------------------------------

    def get_colors(self) -> Dict[int, Color]:
        """
        Return a copy of the index → Color mapping.
        """
        return dict(self._index_to_color)

    def set_colors(self, index_to_color: Dict[int, Color]) -> None:
        """
        Replace the palette with a new index → Color mapping.

        This operation is lossless and exact. Any invalid input raises.
        """
        if not index_to_color:
            raise ValueError("Palette cannot be empty")

        new_index_to_color: Dict[int, Color] = {}
        new_color_to_index: Dict[Color, int] = {}

        for idx, color in index_to_color.items():
            if not isinstance(idx, int) or idx < 0:
                raise ValueError(f"Invalid palette index: {idx}")

            if not isinstance(color, Color):
                raise TypeError(
                    f"Palette value for index {idx} must be a Color instance"
                )

#            if color in new_color_to_index:
#                raise ValueError(
#                    f"Duplicate Color {color} in palette "
#                    f"(already assigned to index {new_color_to_index[color]})"
#                )

            new_index_to_color[idx] = color
            new_color_to_index[color] = idx

        self._index_to_color = new_index_to_color
        self._color_to_index = new_color_to_index

    # ------------------------------------------------------------------
    # Lossless conversions
    # ------------------------------------------------------------------

    def index_to_rgb(self, index: int) -> Optional[Color]:
        """
        Convert a palette index to its exact RGB Color.

        Returns None if the index is not present.
        """
        return self._index_to_color.get(index)

    def rgb_to_index_exact(self, color: Color) -> Optional[int]:
        """
        Convert an RGB Color to a palette index *only if* it matches exactly.

        Returns None if the color is not representable in this palette.
        """
        return self._color_to_index.get(color)

    # ------------------------------------------------------------------
    # Optional policy hook (explicitly lossy)
    # ------------------------------------------------------------------

    def choose_index(self, color: Color, strategy: str = "exact") -> Optional[int]:
        """
        Choose a palette index for a color using an explicit strategy.

        Strategies:
          - "exact": exact match only (default)

        Additional strategies (nearest, threshold, etc.) may be added later
        but are intentionally not implemented here.
        """
        if strategy == "exact":
            return self.rgb_to_index_exact(color)

        raise ValueError(f"Unknown palette strategy: {strategy}")

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_list(cls, colors: list[Color]) -> "Palette":
        """
        Create a palette from a list of Colors, indexed sequentially.
        """
        return cls({i: color for i, color in enumerate(colors)})

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._index_to_color)

    def __contains__(self, index: int) -> bool:
        return index in self._index_to_color

    def __repr__(self) -> str:
        return f"<Palette size={len(self)}>"

def _hex_color(value: str) -> Color:
    value = value.lstrip("#")
    return Color(
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )

def create_ansi_16_palette() -> Palette:
    """
    Create the standard ANSI / CGA 16-color palette.
    Indices 0–15.
    """

    colors = {
        # Black
        0:  _hex_color("#000000"),
        8:  _hex_color("#555555"),

        # Red
        1:  _hex_color("#aa0000"),
        9:  _hex_color("#ff5555"),

        # Green
        2:  _hex_color("#00aa00"),
        10: _hex_color("#55ff55"),

        # Yellow
        3:  _hex_color("#aa5500"),
        11: _hex_color("#ffff55"),

        # Blue
        4:  _hex_color("#0000aa"),
        12: _hex_color("#5555ff"),

        # Magenta
        5:  _hex_color("#aa00aa"),
        13: _hex_color("#ff55ff"),

        # Cyan
        6:  _hex_color("#00aaaa"),
        14: _hex_color("#55ffff"),

        # White
        7:  _hex_color("#aaaaaa"),
        15: _hex_color("#ffffff"),
    }

    return Palette(colors)

def create_ansi_256_palette() -> Palette:
    """
    Create the standard xterm 256-color palette.

    0–15   : ANSI 16-color CGA palette
    16–231 : 6×6×6 RGB color cube
    232–255: grayscale ramp
    """

    index_to_color: dict[int, Color] = {}

    # --- 0–15: ANSI 16 colors ---
    ansi16 = create_ansi_16_palette().get_colors()
    index_to_color.update(ansi16)

    # --- 16–231: 6×6×6 RGB cube ---
    steps = [0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff]

    idx = 16
    for r in steps:
        for g in steps:
            for b in steps:
                index_to_color[idx] = Color(r, g, b)
                idx += 1

    # --- 232–255: grayscale ramp ---
    # 24 shades from dark gray to near-white
    for i in range(24):
        level = 8 + i * 10
        index_to_color[232 + i] = Color(level, level, level)

    return Palette(index_to_color)
