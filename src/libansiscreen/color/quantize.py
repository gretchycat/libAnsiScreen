"""
quantize.py

Explicit, lossy RGB → palette index conversion strategies.

Quantization is never implicit. Callers must choose a strategy.
"""

from typing import Optional
from math import sqrt
from .rgb import Color
from .palette import Palette


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def _rgb_distance(a: Color, b: Color) -> float:
    """
    Euclidean distance in RGB space.
    """
    dr = a.r - b.r
    dg = a.g - b.g
    db = a.b - b.b
    return sqrt(dr * dr + dg * dg + db * db)


def _luminance(c: Color) -> float:
    """
    Perceived luminance (ITU-R BT.709).
    """
    return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b


# ----------------------------------------------------------------------
# Quantization strategies
# ----------------------------------------------------------------------

def quantize_exact(color: Color, palette: Palette) -> Optional[int]:
    """
    Exact RGB → index match only.
    """
    return palette.rgb_to_index_exact(color)


def quantize_nearest_rgb(color: Color, palette: Palette) -> Optional[int]:
    """
    Choose the nearest palette color by Euclidean RGB distance.
    """
    best_index: Optional[int] = None
    best_distance: float = float("inf")

    for idx, pal_color in palette.get_colors().items():
        d = _rgb_distance(color, pal_color)
        if d < best_distance:
            best_distance = d
            best_index = idx

    return best_index


def quantize_nearest_hsv(color: Color, palette: Palette,
                         weight_h: float = 3.0,
                         weight_s: float = 1.0,
                         weight_v: float = 1.0) -> Optional[int]:
    """
    Choose the nearest palette color in HSV space.
    Hue differences are weighted more heavily by default.
    """
    h1, s1, v1 = color.to_hsv()

    best_index: Optional[int] = None
    best_distance: float = float("inf")

    for idx, pal_color in palette.get_colors().items():
        h2, s2, v2 = pal_color.to_hsv()

        dh = min(abs(h1 - h2), 360.0 - abs(h1 - h2)) / 180.0
        ds = abs(s1 - s2)
        dv = abs(v1 - v2)

        d = (
            weight_h * dh * dh +
            weight_s * ds * ds +
            weight_v * dv * dv
        )

        if d < best_distance:
            best_distance = d
            best_index = idx

    return best_index


def quantize_monochrome(color: Color, palette: Palette,
                        threshold: float = 127.5) -> Optional[int]:
    """
    Quantize to a monochrome palette using luminance thresholding.

    Assumes the palette has exactly two colors (black / white).
    """
    colors = palette.get_colors()
    if len(colors) != 2:
        raise ValueError("Monochrome quantization requires a 2-color palette")

    lum = _luminance(color)
    return min(colors.keys()) if lum < threshold else max(colors.keys())


# ----------------------------------------------------------------------
# Dispatcher
# ----------------------------------------------------------------------

def quantize(color: Color,
             palette: Palette,
             strategy: str = "exact",
             **options) -> Optional[int]:
    """
    Dispatch quantization based on strategy name.

    Strategies:
      - exact
      - nearest_rgb
      - nearest_hsv
      - monochrome
    """
    if strategy == "exact":
        return quantize_exact(color, palette)

    if strategy == "nearest_rgb":
        return quantize_nearest_rgb(color, palette)

    if strategy == "nearest_hsv":
        return quantize_nearest_hsv(color, palette, **options)

    if strategy == "monochrome":
        return quantize_monochrome(color, palette, **options)

    raise ValueError(f"Unknown quantization strategy: {strategy}")

