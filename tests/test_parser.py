import pytest
from libansiscreen.screen import Screen
from libansiscreen.parser.ansi_parser import ANSIParser
from libansiscreen.color.rgb import Color
from libansiscreen.cell import ATTR_BOLD, ATTR_ITALIC
from tests.helpers import save_output


def test_parser_plain_text():
    screen = Screen(width=20)
    parser = ANSIParser(screen)
    parser.feed("Hello World!")

    assert screen.get_cell(0, 0).char == "H"
    assert screen.get_cell(11, 0).char == "!"
    save_output(screen, "parser_plain_text.ans")


def test_parser_cursor_movement_sequences():
    screen = Screen(width=20, height=5)
    parser = ANSIParser(screen)
    
    # CSI 3;5 H moves to row 3, column 5 (1-based ANSI indexing)
    parser.feed("\x1b[3;5HPositioned")
    assert screen.get_cell(4, 2).char == "P"  # x=4, y=2
    save_output(screen, "parser_cursor_moves.ans")


def test_parser_sgr_colors_and_attributes():
    screen = Screen(width=30)
    parser = ANSIParser(screen)

    # 1=Bold, 31=Red FG, 42=Green BG
    parser.feed("\x1b[1;31;42mStyled\x1b[0m Plain")

    c_styled = screen.get_cell(0, 0)
    assert c_styled.char == "S"
    assert c_styled.attrs & ATTR_BOLD
    assert c_styled.fg is not None
    assert c_styled.bg is not None

    c_plain = screen.get_cell(7, 0)
    assert c_plain.char == "P"
    assert c_plain.attrs == 0
    save_output(screen, "parser_sgr.ans")


def test_parser_truecolor_and_256_color():
    screen = Screen(width=30)
    parser = ANSIParser(screen)

    # 256 color: \x1b[38;5;196m (red)
    # Truecolor: \x1b[48;2;0;128;255m (blueish bg)
    parser.feed("\x1b[38;5;196m256-fg\x1b[0m \x1b[48;2;0;128;255mtrue-bg\x1b[0m")

    c_256 = screen.get_cell(0, 0)
    assert c_256.fg is not None

    c_true = screen.get_cell(7, 0)
    assert c_true.bg == Color(0, 128, 255)

    save_output(screen, "parser_color_depths.ans")
