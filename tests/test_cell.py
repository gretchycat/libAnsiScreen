import pytest
from libansiscreen.cell import (
    Cell,
    ATTR_BOLD,
    ATTR_FAINT,
    ATTR_ITALIC,
    ATTR_UNDERLINE,
    ATTR_BLINK,
    ATTR_INVERSE,
    ATTR_CONCEAL,
    ATTR_STRIKE,
)
from libansiscreen.color.rgb import Color


def test_cell_defaults():
    cell = Cell()
    assert cell.char is None
    assert cell.fg is None
    assert cell.bg is None
    assert cell.attrs == 0


def test_cell_equality_and_copy():
    red = Color(255, 0, 0)
    blue = Color(0, 0, 255)
    c1 = Cell(char="A", fg=red, bg=blue, attrs=ATTR_BOLD)
    c2 = Cell(char="A", fg=red, bg=blue, attrs=ATTR_BOLD)
    c3 = Cell(char="B", fg=red, bg=blue, attrs=ATTR_BOLD)

    assert c1 == c2
    assert c1 != c3
    assert c1 != "not a cell"

    c_copy = c1.copy()
    assert c_copy == c1
    assert c_copy is not c1


def test_cell_diff_methods():
    c1 = Cell(char="A", fg=Color(255, 0, 0), bg=Color(0, 0, 0), attrs=ATTR_BOLD)
    c2 = Cell(char="A", fg=Color(255, 0, 0), bg=Color(0, 0, 0), attrs=ATTR_BOLD)
    c3 = Cell(char="B", fg=Color(0, 255, 0), bg=Color(255, 255, 255), attrs=ATTR_ITALIC)

    assert c1.diff(c2) == 0
    assert not c1.char_changed(c2)
    assert not c1.fg_changed(c2)
    assert not c1.bg_changed(c2)
    assert not c1.attrs_changed(c2)

    diff_mask = c1.diff(c3)
    assert diff_mask & 1  # char changed
    assert diff_mask & 2  # fg changed
    assert diff_mask & 4  # bg changed
    assert diff_mask & 8  # attrs changed

    assert c1.char_changed(c3)
    assert c1.fg_changed(c3)
    assert c1.bg_changed(c3)
    assert c1.attrs_changed(c3)


def test_cell_color_shifts():
    c = Cell(char="X", fg=Color(100, 100, 100), bg=Color(50, 50, 50))
    
    # shift RGB
    c.shift_rgb(10, -10, 20)
    assert c.fg == Color(110, 90, 120)
    assert c.bg == Color(60, 40, 70)

    # shift HSV
    c.shift_hsv(0.1, 0.0, 0.0)
    assert c.fg is not None
    assert c.bg is not None


def test_attribute_flags():
    attrs = ATTR_BOLD | ATTR_UNDERLINE | ATTR_ITALIC
    cell = Cell("Z", attrs=attrs)

    assert cell.attrs & ATTR_BOLD
    assert cell.attrs & ATTR_UNDERLINE
    assert cell.attrs & ATTR_ITALIC
    assert not (cell.attrs & ATTR_BLINK)
    assert not (cell.attrs & ATTR_INVERSE)
