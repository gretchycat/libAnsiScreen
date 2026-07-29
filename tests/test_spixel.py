import pytest
from libansiscreen.screen import Screen
from libansiscreen.screen_ops.spixel import (
    spixel_plot,
    spixel_get,
    spixel_line,
    spixel_polyline,
    spixel_regular_polygon,
    spixel_regular_star,
    spixel_flood_fill,
    spixel_rectangle,
    spixel_ellipse,
    MODE_OCTANT,
    MODE_BRAILLE,
    MODE_QUADRANT,
    MODE_SEXTANT,
)
from tests.helpers import save_output


def test_spixel_modes_plot_and_get():
    for mode in [MODE_OCTANT, MODE_BRAILLE, MODE_QUADRANT, MODE_SEXTANT]:
        scr = Screen(width=20)
        spixel_plot(scr, 2, 2, state=True, mode=mode)
        assert spixel_get(scr, 2, 2, mode=mode)

        vy = 1 if mode == MODE_QUADRANT else 0
        cell = scr.get_cell(1, vy)
        assert cell is not None
        assert cell.char is not None
        save_output(scr, f"spixel_plot_{mode}.ans")


def test_spixel_line_and_polyline():
    for mode in [MODE_OCTANT, MODE_BRAILLE, MODE_QUADRANT, MODE_SEXTANT]:
        scr = Screen(width=40)
        spixel_line(scr, 0, 0, 20, 10, state=True, mode=mode)
        spixel_polyline(scr, [(0, 10), (10, 0), (20, 10)], state=True, mode=mode)
        save_output(scr, f"spixel_lines_{mode}.ans")


def test_spixel_shapes_and_fill():
    for mode in [MODE_OCTANT, MODE_BRAILLE, MODE_QUADRANT, MODE_SEXTANT]:
        scr = Screen(width=40)
        spixel_rectangle(scr, 2, 2, 14, 10, state=True, mode=mode)
        spixel_ellipse(scr, 25, 10, 8, 6, state=True, mode=mode)
        spixel_regular_polygon(scr, 15, 15, 6, 5, state=True, mode=mode)
        spixel_regular_star(scr, 30, 20, 6, 5, 2, state=True, mode=mode)
        save_output(scr, f"spixel_shapes_{mode}.ans")

        scr_fill = Screen(width=40)
        spixel_regular_polygon(scr_fill, 10, 10, 8, 6, state=True, mode=mode)
        spixel_flood_fill(scr_fill, 10, 10, state=True, mode=mode)
        save_output(scr_fill, f"spixel_floodfill_{mode}.ans")


def test_octant_bitmask_exact_mappings():
    from libansiscreen.screen_ops.spixel import OCTANT_CHARS, OCTANT_MAP

    assert OCTANT_CHARS[0x0F] == "▀"
    assert OCTANT_CHARS[0xF0] == "▄"
    assert OCTANT_CHARS[0x55] == "▌"
    assert OCTANT_CHARS[0xAA] == "▐"
    assert OCTANT_CHARS[0xFF] == "█"

    assert OCTANT_MAP["▀"] == 0x0F
    assert OCTANT_MAP["▄"] == 0xF0
    assert OCTANT_MAP["▌"] == 0x55
    assert OCTANT_MAP["▐"] == 0xAA
    assert OCTANT_MAP["█"] == 0xFF

    # Plot all 8 subpixels in cell (x=0..1, y=0..3)
    scr = Screen(width=10)
    for sub_y in range(4):
        for sub_x in range(2):
            spixel_plot(scr, sub_x, sub_y, state=True, mode=MODE_OCTANT)

    assert scr.get_cell(0, 0).char == "█"


def test_sextant_bitmask_exact_mappings():
    from libansiscreen.screen_ops.spixel import SEXTANT_CHARS, SEXTANT_MAP

    assert SEXTANT_CHARS[0] == " "
    assert SEXTANT_CHARS[63] == "█"
    assert SEXTANT_CHARS[0x01] == chr(0x1FB00)
    assert SEXTANT_CHARS[0x05] == "🬄"

    assert SEXTANT_MAP[" "] == 0
    assert SEXTANT_MAP["█"] == 63
    assert SEXTANT_MAP[chr(0x1FB00)] == 0x01
   

    # Plot all 6 subpixels in cell (x=0..1, y=0..2)
    scr = Screen(width=10)
    for sub_y in range(3):
        for sub_x in range(2):
            spixel_plot(scr, sub_x, sub_y, state=True, mode=MODE_SEXTANT)

    assert scr.get_cell(0, 0).char == "█"


def test_octant_flood_fill_boundary_containment():
    """
    Verify that octant flood fill stays strictly within an enclosed boundary
    and does not leak to surrounding subpixels or cause character grid corruption.
    """
    for mode in [MODE_OCTANT, MODE_QUADRANT, MODE_SEXTANT, MODE_BRAILLE]:
        scr = Screen(width=10, height=10)
        scr.cls()

        # Draw an enclosed subpixel rectangle boundary
        spixel_rectangle(scr, 2, 2, 8, 8, state=True, fill=False, mode=mode)

        # Flood fill inside the boundary at seed (5, 5)
        spixel_flood_fill(scr, 5, 5, state=True, mode=mode)

        # Assert subpixels inside the boundary are True
        for y in range(3, 8):
            for x in range(3, 8):
                assert spixel_get(scr, x, y, mode=mode) is True

        # Assert boundary subpixels are True
        for x in range(2, 9):
            assert spixel_get(scr, x, 2, mode=mode) is True
            assert spixel_get(scr, x, 8, mode=mode) is True

        # Assert subpixels outside the boundary remain False (no leakage!)
        assert spixel_get(scr, 0, 0, mode=mode) is False
        assert spixel_get(scr, 1, 1, mode=mode) is False
        assert spixel_get(scr, 9, 9, mode=mode) is False


def test_octant_all_256_unique_mappings():
    """
    Verify that all 256 octant character bitmasks map to 256 unique characters,
    preventing lookup collisions during subpixel plotting.
    """
    from libansiscreen.screen_ops.spixel import OCTANT_CHARS, OCTANT_MAP

    assert len(OCTANT_CHARS) == 256
    assert len(set(OCTANT_CHARS)) == 256
    assert len(OCTANT_MAP) == 256

