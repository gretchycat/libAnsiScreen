import pytest
from libansiscreen.framebuffer import frameBuffer
from libansiscreen.cell import Cell, ATTR_BOLD, ATTR_ITALIC
from libansiscreen.color.rgb import Color


def test_framebuffer_init_and_validation():
    fb = frameBuffer(width=20, height=5)
    assert fb.width == 20
    assert fb.height >= 5

    with pytest.raises(ValueError):
        frameBuffer(width=0)

    with pytest.raises(ValueError):
        frameBuffer(width=-10)


def test_cell_get_set_put():
    fb = frameBuffer(width=10, height=2)
    
    fb.put_cell(0, 0, char="A", fg=Color(255, 0, 0), bg=Color(0, 0, 0), attrs=ATTR_BOLD)
    c0 = fb.get_cell(0, 0)
    assert c0 is not None
    assert c0.char == "A"
    assert c0.fg == Color(255, 0, 0)
    assert c0.attrs == ATTR_BOLD

    assert fb.get_cell(-1, 0) is None
    assert fb.get_cell(100, 0) is None

    fb.set_cell(1, 0, Cell("B"))
    assert fb.get_cell(1, 0).char == "B"

    fb.set_cell(1, 0, None)
    assert fb.get_cell(1, 0) is None


def test_rows_proxy_direct_mutations():
    fb = frameBuffer(width=10, height=5)
    
    # Direct element assignment via rows
    fb.rows[0][0] = Cell(char="X", fg=Color(255, 0, 0))
    assert fb.get_cell(0, 0).char == "X"
    assert fb.get_cell(0, 0).fg == Color(255, 0, 0)

    # In-place attribute mutation on cell proxy
    fb.rows[0][0].char = "Y"
    assert fb.get_cell(0, 0).char == "Y"
    assert fb.rows[0][0].char == "Y"

    # Row assignment
    fb.rows[1] = [Cell(char="A"), Cell(char="B")]
    assert fb.get_cell(0, 1).char == "A"
    assert fb.get_cell(1, 1).char == "B"


def test_cursor_movements_in_framebuffer():
    fb = frameBuffer(width=10, height=5)
    
    fb.cursor_goto(5, 2)
    assert fb.cursor.x == 5
    assert fb.cursor.y == 2

    fb.cursor_up(1)
    assert fb.cursor.y == 1

    fb.cursor_down(2)
    assert fb.cursor.y == 3

    fb.cursor_forward(3)
    assert fb.cursor.x == 8

    fb.cursor_back(4)
    assert fb.cursor.x == 4

    fb.cursor_next_line(1)
    assert fb.cursor.x == 0
    assert fb.cursor.y == 4

    fb.cursor_prev_line(2)
    assert fb.cursor.x == 0
    assert fb.cursor.y == 2

    fb.cursor_set_column(7)
    assert fb.cursor.x == 7

    fb.cursor_save()
    fb.cursor_goto(0, 0)
    fb.cursor_restore()
    assert fb.cursor.x == 7
    assert fb.cursor.y == 2

    fb.carriage_return()
    assert fb.cursor.x == 0

    fb.line_feed()
    assert fb.cursor.y == 3

    fb.new_line()
    assert fb.cursor.x == 0
    assert fb.cursor.y == 4


def test_graphics_state_management():
    fb = frameBuffer(width=10)
    
    red = Color(255, 0, 0)
    green = Color(0, 255, 0)
    fb.set_foreground(red)
    fb.set_background(green)
    fb.set_attrs(ATTR_BOLD)
    fb.add_attrs(ATTR_ITALIC)

    assert fb.current_fg == red
    assert fb.current_bg == green
    assert fb.current_attrs == (ATTR_BOLD | ATTR_ITALIC)

    fb.clear_attrs(ATTR_BOLD)
    assert fb.current_attrs == ATTR_ITALIC

    fb.reset_graphics()
    assert fb.current_attrs == 0


def test_writing_and_wrapping():
    fb = frameBuffer(width=5)
    fb.put_text("1234567\n89")

    # 12345 wrapped to row 0, 67 wrapped to row 1, \n advanced to row 2, 89 on row 2
    assert fb.get_cell(0, 0).char == "1"
    assert fb.get_cell(4, 0).char == "5"
    assert fb.get_cell(0, 1).char == "6"
    assert fb.get_cell(1, 1).char == "7"
    assert fb.get_cell(0, 2).char == "8"
    assert fb.get_cell(1, 2).char == "9"


def test_clearing_operations():
    fb = frameBuffer(width=10, height=3)
    fb.put_text("ABCDE\nFGHIJ")

    fb.cursor_goto(2, 0)
    fb.clear_to_end_of_line()
    assert fb.get_cell(1, 0).char == "B"
    assert fb.get_cell(2, 0).char == " "
    assert fb.get_cell(9, 0).char == " "

    fb.cursor_goto(2, 1)
    fb.clear_to_end_of_screen()
    assert fb.get_cell(1, 1).char == "G"
    assert fb.get_cell(2, 1).char == " "

    fb.clear_row(0)
    assert fb.get_cell(0, 0).char is None

    fb.set_foreground(Color(255, 0, 0))
    fb.set_background(Color(0, 0, 255))
    fb.cls()
    assert fb.cursor.x == 0
    assert fb.cursor.y == 0
    assert fb.get_cell(0, 0).char == " "
    assert fb.get_cell(0, 0).fg == Color(255, 0, 0)
    assert fb.get_cell(0, 0).bg == Color(0, 0, 255)


def test_resize():
    fb = frameBuffer(width=10, height=5)
    fb.put_text("0123456789")
    fb.resize(width=5, height=2)

    assert fb.width == 5
    assert fb.height >= 2
    assert len(fb.rows[0]) == 5
