import pytest
from libansiscreen.color.rgb import Color


def test_color_constructors():
    c1 = Color(255, 128, 64)
    assert c1.r == 255
    assert c1.g == 128
    assert c1.b == 64
    assert c1.a == 255

    c_rgb = Color.rgb(10, 20, 30)
    assert c_rgb == Color(10, 20, 30)

    c_hex = Color.hex("#FF0000")
    assert c_hex == Color(255, 0, 0)

    c_hex_short = Color.hex("0F0")
    assert c_hex_short == Color(0, 255, 0)

    c_hsv = Color.hsv(0.0, 1.0, 1.0)
    assert c_hsv.r == 255
    assert c_hsv.g == 0
    assert c_hsv.b == 0


def test_color_polymorphic_set():
    assert Color.set(None) == Color(0, 0, 0)
    assert Color.set(Color(10, 20, 30)) == Color(10, 20, 30)
    assert Color.set((50, 60, 70)) == Color(50, 60, 70)
    assert Color.set({"r": 1, "g": 2, "b": 3}) == Color(1, 2, 3)
    assert Color.set("#0000FF") == Color(0, 0, 255)
    
    # ANSI 256 index
    c_idx = Color.set(1)
    assert isinstance(c_idx, Color)


def test_color_conversions_and_metrics():
    c = Color(255, 0, 0)
    assert c.to_tuple() == (255, 0, 0)
    assert c.to_float_tuple() == (1.0, 0.0, 0.0)

    h, s, v = c.to_hsv()
    assert pytest.approx(h, 0.01) == 0.0
    assert pytest.approx(s, 0.01) == 1.0
    assert pytest.approx(v, 0.01) == 1.0

    lum = c.luminance()
    assert lum > 0.0

    d_rgb = Color(255, 0, 0).distance_rgb(Color(0, 0, 0))
    assert d_rgb == 255 * 255

    d_hsv = Color(255, 0, 0).distance_hsv(Color(0, 255, 0))
    assert d_hsv > 0.0


def test_color_blending_and_shifting():
    red = Color(255, 0, 0)
    blue = Color(0, 0, 255)
    mid = red.blend(blue, 0.5)

    assert mid.r == 127
    assert mid.b == 127

    c_shifted_rgb = red.shift_rgb(-50, 100, 200)
    assert c_shifted_rgb == Color(205, 100, 200)

    c_shifted_hsv = red.shift_hsv(0.5, 0.0, 0.0)
    assert isinstance(c_shifted_hsv, Color)
