import pytest
from libansiscreen.screen import Screen
from libansiscreen.framebuffer import frameBuffer
from libansiscreen.color.rgb import Color
from libansiscreen.cell import Cell, ATTR_BOLD, ATTR_ITALIC
from libansiscreen.binary_cell import pack_cell, unpack_cell, CELL_SIZE
from libansiscreen.parser.ansi_parser import ANSIParser
from tests.helpers import save_output


def test_cls_row_trimming_and_space_fill():
    """
    Regression Test: CLS should trim down rows to the target height,
    reset cursor to (0,0), set current fg/bg, and fill each cell with space (' ').
    """
    screen = Screen(width=15, height=5)
    screen.put_text("0123456789\n" * 10)  # Grows buffer beyond initial height
    assert screen.height >= 10

    custom_fg = Color(255, 120, 40)
    custom_bg = Color(10, 20, 30)
    screen.set_foreground(custom_fg)
    screen.set_background(custom_bg)

    # Execute CLS
    screen.cls()

    # 1. Cursor reset to (0,0)
    assert screen.cursor.x == 0
    assert screen.cursor.y == 0

    # 2. Buffer trimmed down to old height (11)
    assert screen.height == 11

    # 3. Each cell is filled with space (' ') and active fg/bg
    for y in range(screen.height):
        for x in range(screen.width):
            cell = screen.get_cell(x, y)
            assert cell is not None
            assert cell.char == " "
            assert cell.fg == custom_fg
            assert cell.bg == custom_bg


def test_rows_proxy_in_place_mutations():
    """
    Regression Test: Modifying fb.rows[y][x] or cell properties directly
    (e.g., cell.char = 'Z', cell.fg = ...) must update the binary buffer in real time.
    """
    fb = frameBuffer(width=10, height=5)

    # 1. Attribute setters on CellProxy
    fb.rows[0][0].char = "Z"
    fb.rows[0][0].fg = Color(10, 20, 30)
    fb.rows[0][0].bg = Color(40, 50, 60)
    fb.rows[0][0].attrs = ATTR_BOLD | ATTR_ITALIC

    # Verify lookups from binary buffer match proxy mutations
    c00 = fb.get_cell(0, 0)
    assert c00 is not None
    assert c00.char == "Z"
    assert c00.fg == Color(10, 20, 30)
    assert c00.bg == Color(40, 50, 60)
    assert c00.attrs == (ATTR_BOLD | ATTR_ITALIC)

    # 2. Iterative mutation over rows
    for y, row in enumerate(fb.rows):
        for x, cell in enumerate(row):
            cell.char = chr(ord("A") + (x % 26))

    assert fb.get_cell(0, 1).char == "A"
    assert fb.get_cell(1, 1).char == "B"


def test_paste_color_preservation_when_source_is_none():
    """
    Regression Test: When pasting src onto dst, if src cell has fg=None or bg=None,
    destination colors MUST NOT be overwritten.
    """
    # Destination screen: White text on Blue background
    dst = Screen(width=10, height=3)
    dst.set_foreground(Color(255, 255, 255))
    dst.set_background(Color(0, 0, 255))
    dst.cls()
    dst.put_text("PANEL_BACKGROUND")

    # Source overlay 1: Red text with None (transparent) background
    src1 = Screen(width=5, height=1)
    src1.put_cell(0, 0, char="H", fg=Color(255, 0, 0), bg=None)

    dst.paste(src1, box=(0, 0, 5, 1))

    c00 = dst.get_cell(0, 0)
    assert c00.char == "H"
    assert c00.fg == Color(255, 0, 0)     # Updated to Red
    assert c00.bg == Color(0, 0, 255)     # Preserved Blue background!

    # Source overlay 2: Green background with None (transparent) foreground
    src2 = Screen(width=5, height=1)
    src2.put_cell(0, 0, char="K", fg=None, bg=Color(0, 255, 0))

    dst.paste(src2, box=(0, 0, 5, 1))

    c00_updated = dst.get_cell(0, 0)
    assert c00_updated.char == "K"
    assert c00_updated.fg == Color(255, 0, 0)  # Preserved Red foreground!
    assert c00_updated.bg == Color(0, 255, 0)  # Updated to Green background!


def test_space_character_binary_struct_packing():
    """
    Regression Test: Cell(char=' ') must pack to codepoint 32 and unpack as ' '.
    """
    space_cell = Cell(char=" ", fg=Color(128, 64, 32), bg=Color(16, 8, 4), attrs=ATTR_BOLD)
    buf = bytearray(CELL_SIZE)

    pack_cell(buf, 0, space_cell)
    unpacked = unpack_cell(buf, 0)

    assert unpacked is not None
    assert unpacked.char == " "
    assert unpacked.fg == Color(128, 64, 32)
    assert unpacked.bg == Color(16, 8, 4)
    assert unpacked.attrs == ATTR_BOLD


def test_ansi_parser_ed0_clear_screen():
    """
    Regression Test: ANSI ED 0 (\x1b[0J / \x1b[J) and ED 2 (\x1b[2J) must trigger
    clear_to_end_of_screen and cls without raising AttributeError.
    """
    screen = Screen(width=20, height=5)
    parser = ANSIParser(screen)

    parser.feed("First Line\nSecond Line\nThird Line")
    screen.cursor_goto(0, 1)

    # ED 0: Clear from cursor to end of screen
    parser.feed("\x1b[J")
    assert screen.get_cell(0, 0).char == "F"  # Line 0 untouched

    # ED 2: Clear full screen (cls)
    parser.feed("\x1b[2J")
    assert screen.cursor.x == 0
    assert screen.cursor.y == 0
    assert screen.get_cell(0, 0).char == " "


def test_binary_clip_copy_cut_paste_tile():
    """
    Regression Test: High-performance binary clip operations (copy, cut, paste, tile, clear).
    """
    src = Screen(width=20, height=4)
    src.put_text("ROW0_TEXT_HERE\nROW1_TEXT_HERE\nROW2_TEXT_HERE\nROW3_TEXT_HERE")

    # 1. Copy sub-region
    copied = src.copy((0, 0, 10, 2))
    assert copied.width == 10
    assert copied.height == 2
    assert copied.get_cell(0, 0).char == "R"

    # 2. Paste sub-region
    dst = Screen(width=20, height=4)
    dst.paste(copied, box=(5, 1, 10, 2))
    assert dst.get_cell(5, 1).char == "R"

    # 3. Tile
    small_tile = Screen(width=2, height=1)
    small_tile.put_cell(0, 0, char="X", fg=Color(255, 0, 0))
    small_tile.put_cell(1, 0, char="Y", fg=Color(0, 255, 0))

    dst.tile(small_tile)
    assert dst.get_cell(0, 0).char == "X"
    assert dst.get_cell(1, 0).char == "Y"
    assert dst.get_cell(2, 0).char == "X"


@pytest.mark.parametrize("use_binary", [True, False])
def test_clear_to_end_of_screen_space_fill(use_binary: bool):
    """
    Test that clear_to_end_of_screen fills all remaining screen cells with spaces
    and active graphics attributes.
    """
    screen = Screen(width=10, height=4, use_binary=use_binary)
    screen.put_text("0123456789\n1123456789\n2123456789\n3123456789")
    custom_fg = Color(100, 150, 200)
    screen.set_foreground(custom_fg)
    screen.cursor_goto(0, 1)

    screen.clear_to_end_of_screen()

    # Row 0 remains untouched
    assert screen.get_cell(0, 0).char == "0"
    # Rows 1..3 are filled with space ' ' and active fg
    for y in range(1, screen.height):
        for x in range(screen.width):
            cell = screen.get_cell(x, y)
            assert cell is not None
            assert cell.char == " "
            assert cell.fg == custom_fg


@pytest.mark.parametrize("use_binary", [True, False])
def test_row_created_during_print_or_feed_is_filled_with_spaces(use_binary: bool):
    """
    Test that when a row is created during a print or feed operation,
    unwritten cells on that newly allocated row are filled with spaces.
    """
    screen = Screen(width=10, height=1, use_binary=use_binary)

    # Print short text followed by newline, creating row 1
    screen.put_text("A\nB")
    assert screen.height == 2

    # Row 0: 'A' at (0, 0)
    assert screen.get_cell(0, 0).char == "A"
    # Row 1: 'B' at (0, 1), and remaining columns (1..9) filled with spaces ' '
    assert screen.get_cell(0, 1).char == "B"
    for x in range(1, screen.width):
        cell = screen.get_cell(x, 1)
        assert cell is not None
        assert cell.char == " "

    # Feed operation via ANSIParser
    parser = ANSIParser(screen)
    parser.feed("C\nD")
    assert screen.height >= 3

    # Newly created row 2 should also be filled with spaces
    assert screen.get_cell(0, 2).char == "D"
    for x in range(1, screen.width):
        cell = screen.get_cell(x, 2)
        assert cell is not None
        assert cell.char == " "


