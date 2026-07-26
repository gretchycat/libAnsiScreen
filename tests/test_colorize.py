import pytest
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops.colorize import Colorize
from libansiscreen.screen_ops.prim import box
from libansiscreen.screen_ops.clip import clear
from libansiscreen.renderer.ansi_emitter import Box
from libansiscreen.screen_ops.glyph_defs import BOX_BLOCK
from tests.helpers import save_output


def build_solid_block_screen(width: int = 20, height: int = 10) -> Screen:
    screen = box(width, height, glyphs=BOX_BLOCK)
    center_box = Box(width // 4, height // 4, width // 2, height // 2)
    clear(screen, box=center_box)
    return Colorize.extend(screen)


def build_gradient() -> list[Color]:
    return [
        Color(255, 0, 0),     # red
        Color(255, 255, 0),   # yellow
        Color(0, 255, 0),     # green
        Color(0, 255, 255),   # cyan
        Color(0, 0, 255),     # blue
        Color(255, 0, 255),   # magenta
    ]


def test_colorize_horizontal_fg_only_if_set():
    screen = build_solid_block_screen()
    grad = build_gradient()

    screen.colorize(gradient=grad, mode="horizontal", only_if_set=True)

    # Solid block cells have fg color assigned
    assert screen.get_cell(0, 0).fg is not None

    # Cleared central box remains None
    cx, cy = screen.width // 2, screen.height // 2
    assert screen.get_cell(cx, cy).fg is None

    save_output(screen, "colorize_horizontal_fg.ans")


def test_colorize_vertical_bg():
    screen = build_solid_block_screen()
    grad = build_gradient()

    screen.colorize(gradient=grad, mode="vertical", background=True, foreground=False)

    assert screen.get_cell(0, 0).bg is not None
    assert screen.get_cell(screen.width - 1, 0).bg is not None

    save_output(screen, "colorize_vertical_bg.ans")


def test_colorize_diagonal_and_tint():
    screen = build_solid_block_screen()
    grad = build_gradient()

    screen.colorize(gradient=grad, mode="diagonal", direction="tlbr")
    assert screen.get_cell(0, 0).fg is not None

    save_output(screen, "colorize_diag_tint.ans")


def test_colorize_words():
    screen = Screen(width=30)
    text = "Hello world from ANSI"
    for i, ch in enumerate(text):
        screen.put_cell(i, 0, char=ch)

    grad = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]
    screen.colorize(gradient=grad, mode="words")

    # Sequential letters in word get distinct colors
    assert screen.get_cell(0, 0).fg != screen.get_cell(1, 0).fg
    assert screen.get_cell(1, 0).fg != screen.get_cell(2, 0).fg

    # Spaces reset word sequence
    assert screen.get_cell(5, 0).char == " "

    save_output(screen, "colorize_words.ans")


def test_colorize_unknown_mode_raises():
    screen = Screen(width=10)
    with pytest.raises(ValueError):
        screen.colorize(gradient=build_gradient(), mode="invalid_mode")
