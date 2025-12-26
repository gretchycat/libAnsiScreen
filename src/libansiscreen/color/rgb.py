from __future__ import annotations
from dataclasses import dataclass
import colorsys
from typing import Tuple


@dataclass(frozen=True, slots=True)
class Color:
    """
    Immutable RGB color.

    - Components are integers in range 0–255
    - Hashable and safe as dict keys
    - Value equality semantics
    """

    r: int
    g: int
    b: int

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    def __post_init__(self):
        if not (0 <= self.r <= 255):
            raise ValueError(f"Invalid r value: {self.r}")
        if not (0 <= self.g <= 255):
            raise ValueError(f"Invalid g value: {self.g}")
        if not (0 <= self.b <= 255):
            raise ValueError(f"Invalid b value: {self.b}")

    def __eq__(self, other: object) -> bool:
        if other==None:
            other=Color(0,0,0)
        if not isinstance(other, Color):
            return NotImplemented
        return (self.r == other.r
            and self.g == other.g
            and self.b == other.b)

    def luminance(self):
        return (
            0.2126 * self.r +
            0.7152 * self.g +
            0.0722 * self.b
        )

    def __gt__(self, other: object) -> bool:
        if other==None:
            other=Color(0,0,0)
        if not isinstance(other, Color):
            return NotImplemented
        return self.luminance()>other.luminance()

    def __lt__(self, other: object) -> bool:
        if other==None:
            other=Color(0,0,0) 
        if not isinstance(other, Color):
            return NotImplemented
        return self.luminance()<other.luminance()

    # ------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_float_tuple(self) -> Tuple[float, float, float]:
        """RGB as floats in range 0.0–1.0"""
        return (self.r / 255.0, self.g / 255.0, self.b / 255.0)

    def to_hsv(self) -> Tuple[float, float, float]:
        """
        HSV representation.

        Returns:
            (h, s, v) where:
            - h ∈ [0.0, 1.0)
            - s ∈ [0.0, 1.0]
            - v ∈ [0.0, 1.0]
        """
        return colorsys.rgb_to_hsv(*self.to_float_tuple())

    # ------------------------------------------------------------
    # Distance metrics
    # ------------------------------------------------------------

    def distance_rgb(self, other: Color) -> int:
        """
        Squared Euclidean distance in RGB space.
        Fast and good enough for exact match checks.
        """
        dr = self.r - other.r
        dg = self.g - other.g
        db = self.b - other.b
        return dr * dr + dg * dg + db * db

    def distance_hsv(self, other: Color) -> float:
        """
        Distance in HSV space.

        Hue is circular; saturation/value are linear.
        """
        h1, s1, v1 = self.to_hsv()
        h2, s2, v2 = other.to_hsv()

        dh = min(abs(h1 - h2), 1.0 - abs(h1 - h2))
        ds = s1 - s2
        dv = v1 - v2

        return dh * dh + ds * ds + dv * dv

    def blend(self, other: "Color", amount: float) -> "Color":
        """
        Blend this color toward `other` by amount [0..1].
        """
        if not other or amount==0.0:
            return self
        a = max(0.0, min(1.0, amount))
        return Color(
            int(self.r + (other.r - self.r) * a),
            int(self.g + (other.g - self.g) * a),
            int(self.b + (other.b - self.b) * a),
        )

# ------------------------------------------------------------
    # Stringification
    # ------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b})"
