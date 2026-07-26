import pytest
from libansiscreen.cursor import Cursor


def test_cursor_init_and_set():
    cur = Cursor()
    assert cur.x == 0
    assert cur.y == 0

    cur.set(15, 25)
    assert cur.x == 15
    assert cur.y == 25


def test_cursor_move():
    cur = Cursor(10, 10)
    cur.move(dx=5, dy=-3)
    assert cur.x == 15
    assert cur.y == 7

    cur.move(dx=-20, dy=-20)
    assert cur.x == -5
    assert cur.y == -13


def test_cursor_save_restore_reset():
    cur = Cursor(5, 5)
    cur.save()

    cur.set(100, 200)
    assert cur.x == 100
    assert cur.y == 200

    cur.restore()
    assert cur.x == 5
    assert cur.y == 5

    cur.reset()
    assert cur.x == 0
    assert cur.y == 0

    # Restoring after reset restores to (0, 0)
    cur.restore()
    assert cur.x == 0
    assert cur.y == 0
