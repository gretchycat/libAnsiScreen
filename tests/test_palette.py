import pytest
from libansiscreen.color.rgb import Color
from libansiscreen.color.palette import (
    Palette,
    create_ansi_16_palette,
    create_ansi_256_palette,
)


def test_palette_creation_and_lookups():
    red = Color(255, 0, 0)
    blue = Color(0, 0, 255)
    pal = Palette({0: red, 1: blue})

    assert pal.index_to_rgb(0) == red
    assert pal.index_to_rgb(1) == blue
    assert pal.index_to_rgb(2) is None

    assert pal.rgb_to_index_exact(red) == 0
    assert pal.rgb_to_index_exact(blue) == 1
    assert pal.rgb_to_index_exact(Color(100, 100, 100)) is None

    assert pal.choose_index(red, strategy="exact") == 0


def test_palette_validation_and_from_list():
    colors = [Color(0, 0, 0), Color(255, 255, 255)]
    pal = Palette.from_list(colors)

    assert pal.index_to_rgb(0) == Color(0, 0, 0)
    assert pal.index_to_rgb(1) == Color(255, 255, 255)

    with pytest.raises(ValueError):
        Palette({})

    with pytest.raises(TypeError):
        Palette({0: "not a color"})


def test_builtin_ansi_palettes():
    p16 = create_ansi_16_palette()
    colors16 = p16.get_colors()
    assert len(colors16) == 16
    assert 0 in colors16
    assert 15 in colors16

    p256 = create_ansi_256_palette()
    colors256 = p256.get_colors()
    assert len(colors256) == 256
    assert 0 in colors256
    assert 255 in colors256
