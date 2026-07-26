import pytest
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from tests.helpers import save_output


def test_screen_init_repr_and_defaults():
    scr = Screen(width=40, height=10)
    assert scr.width == 40
    assert scr.height >= 10
    assert scr.parser is not None
    assert scr.emitter is not None


def test_screen_feed_and_print():
    scr = Screen(width=30)
    scr.feed("Feed text\n")
    scr.print("Print text")

    assert scr.get_cell(0, 0).char == "F"
    assert scr.get_cell(0, 1).char == "P"
    save_output(scr, "screen_feed_print.ans")


def test_screen_emit_and_emit_diff():
    scr1 = Screen(width=20)
    scr1.put_text("Original text")

    scr2 = Screen(width=20)
    scr2.put_text("Modified text")

    ansi1 = scr1.emit()
    diff = scr2.emit_diff(scr1)

    assert isinstance(ansi1, str)
    assert isinstance(diff, str)
    save_output(scr1, "screen_emit.ans")


def test_screen_universal_dispatchers():
    scr = Screen(width=40)
    red = Color(255, 0, 0)
    green = Color(0, 255, 0)

    # Universal plot & line in half-block mode
    scr.plot(5, 5, red, mode="half")
    scr.line(0, 0, 10, 10, green, mode="half")

    # Subpixel braille mode line
    scr.line(0, 0, 30, 15, state=True, mode="braille")

    # Shapes
    scr.rectangle(2, 2, 8, 8, state=red, mode="half")
    scr.ellipse(20, 10, 5, 5, state=green, mode="half")

    save_output(scr, "screen_universal_dispatchers.ans")


def test_screen_char_primitives():
    scr = Screen(width=40)
    blue = Color(0, 0, 255)
    yellow = Color(255, 255, 0)

    scr.char_rectangle(2, 2, 12, 6, fill=blue)
    scr.char_ellipse(25, 8, 6, 4, fill=yellow)
    scr.char_tile("AB\nCD\n")

    save_output(scr, "screen_char_primitives.ans")
