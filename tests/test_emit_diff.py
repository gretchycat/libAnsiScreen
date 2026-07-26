import pytest
from libansiscreen.screen import Screen
from libansiscreen.renderer.ansi_emitter import ANSIEmitter
from libansiscreen.parser.ansi_parser import ANSIParser
from tests.helpers import save_output


def test_emit_diff():
    s1 = Screen(width=20, height=5)
    s1.put_text("Hello World!")
    s1.put_text("\nThis is row 2")

    s2 = s1.copy()
    s2.cursor_goto(6, 0)
    s2.put_text("Earth")  # "Hello Earth!"
    s2.cursor_goto(0, 2)
    s2.put_text("Row 3 added")

    emitter = ANSIEmitter()
    diff = emitter.emit_diff(s2, s1)

    assert isinstance(diff, str)

    # Verification: Applying diff to s1 should result in s2
    s_verify = s1.copy()
    parser = ANSIParser(s_verify)
    parser.feed(diff)

    # Compare s_verify and s2
    for y in range(s2.height):
        for x in range(s2.width):
            c2 = s2.get_cell(x, y)
            cv = s_verify.get_cell(x, y)
            assert cv == c2, f"Mismatch at {x},{y}: expected {c2}, got {cv}"

    save_output(s2, "test_emit_diff_result.ans")
