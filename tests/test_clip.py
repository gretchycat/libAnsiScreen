import pytest
from pathlib import Path
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.screen_ops.clip import copy, clear, cut, paste, tile
from tests.helpers import save_output

THETIS_FILE = Path(__file__).parent / "thetis.ans"


def test_clip_copy_clear_cut_paste():
    scr = Screen(width=40)
    scr.set_foreground(Color(255, 0, 0))
    scr.set_background(Color(0, 0, 100))
    scr.put_text("0123456789\n" * 4)

    # Box (x=2, y=1, w=5, h=2)
    box_region = (2, 1, 5, 2)

    # Copy
    copied_fb = scr.copy(box_region)
    assert copied_fb.width == 5
    assert copied_fb.height == 2
    assert copied_fb.get_cell(0, 0).char == "2"

    # Paste copied onto destination
    dst = Screen(width=40)
    dst.paste(copied_fb, box=(10, 0, 5, 2))
    assert dst.get_cell(10, 0).char == "2"
    save_output(dst, "test_clip_pasted.ans")

    # Clear
    scr.clear(box_region)
    assert scr.get_cell(2, 1).char is None
    save_output(scr, "test_clip_cleared.ans")

    # Cut
    cut_fb = scr.cut((0, 0, 5, 1))
    assert cut_fb.get_cell(0, 0).char == "0"
    assert scr.get_cell(0, 0).char is None


def test_clip_paste_transparency_modes():
    src = Screen(width=5)
    src.put_cell(0, 0, char="X", fg=Color(255, 0, 0), bg=Color(0, 255, 0))
    src.put_cell(1, 0, char=" ", fg=Color(255, 0, 0), bg=Color(0, 255, 0))

    dst = Screen(width=10)
    dst.put_cell(0, 0, char="A", fg=Color(255, 255, 255), bg=Color(10, 10, 10))
    dst.put_cell(1, 0, char="B", fg=Color(255, 255, 255), bg=Color(10, 10, 10))

    # Paste with transparent space character
    dst.paste(src, transparent_char={" "})
    assert dst.get_cell(0, 0).char == "X"
    assert dst.get_cell(1, 0).char == "B"  # Space was skipped!
    save_output(dst, "test_clip_transparent_paste.ans")


def test_clip_paste_none_color_preservation():
    # Destination with white text on blue background
    dst = Screen(width=5)
    dst.put_cell(0, 0, char="A", fg=Color(255, 255, 255), bg=Color(0, 0, 255))

    # Source with red text and None background
    src = Screen(width=5)
    src.put_cell(0, 0, char="B", fg=Color(255, 0, 0), bg=None)

    # Paste src onto dst
    dst.paste(src)

    # Destination cell gets character "B", red foreground, and preserves blue background
    assert dst.get_cell(0, 0).char == "B"
    assert dst.get_cell(0, 0).fg == Color(255, 0, 0)
    assert dst.get_cell(0, 0).bg == Color(0, 0, 255)


def test_clip_tiling():
    tile_fb = Screen(width=2)
    tile_fb.put_cell(0, 0, char="#", fg=Color(255, 255, 0))
    tile_fb.put_cell(1, 0, char=".", fg=Color(0, 255, 255))

    screen = Screen(width=8, height=2)
    screen.tile(tile_fb)

    assert screen.get_cell(0, 0).char == "#"
    assert screen.get_cell(1, 0).char == "."
    assert screen.get_cell(2, 0).char == "#"
    assert screen.get_cell(3, 0).char == "."
    save_output(screen, "test_clip_tiled.ans")


def test_clip_with_sample_ans_file():
    if not THETIS_FILE.exists():
        pytest.skip("thetis.ans sample file missing")

    screen = Screen(width=80)
    screen.print(THETIS_FILE.read_bytes())

    box_region = (20, 5, 40, 10)
    copied = screen.copy(box_region)
    save_output(copied, "test_clip_copy_truecolor.ans")

    full_copy = screen.copy()
    save_output(full_copy, "test_clip_fullcopy_truecolor.ans")

    screen.clear(box_region)
    save_output(screen, "test_clip_cleared_thetis.ans")


def test_clip_performance_parity():
    for use_bin in (False, True):
        # Large 200x100 screen buffer
        src = Screen(width=200, height=100, use_binary=use_bin)
        src.set_foreground(Color(100, 200, 50))
        src.set_background(Color(20, 30, 40))
        src.put_text("BINARY_CELL_" * 1500)

        # 1. Full copy
        copied = src.copy()
        assert copied.width == 200
        assert copied.height == 100

        # 2. Fast paste onto destination
        dst = Screen(width=200, height=100, use_binary=use_bin)
        dst.paste(copied)
        assert dst.get_cell(0, 0).char == src.get_cell(0, 0).char

        # 3. Slice clear
        dst.clear((50, 20, 100, 50))
        assert dst.get_cell(50, 20).char is None

        # 4. Fast tile
        tile_src = Screen(width=10, height=5, use_binary=use_bin)
        tile_src.put_text("TILE" * 10)
        dst.tile(tile_src)
        assert dst.get_cell(0, 0).char == "T"

