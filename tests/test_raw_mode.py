import pytest
from libansiscreen.framebuffer import frameBuffer, CP437_LOW_GRAPHICS
from libansiscreen.screen import Screen
from libansiscreen.cell import Cell, ATTR_BOLD, ATTR_ITALIC, ATTR_UNDERLINE
from libansiscreen.color.rgb import Color


def test_cp437_control_character_mapping():
    """
    Verify that all ASCII control characters (0-31) map to their CP437 low graphics
    counterparts and ASCII 127 maps to '⌂' in raw mode.
    """
    for use_bin in (False, True):
        fb = frameBuffer(width=33, height=2, use_binary=use_bin)
        
        # Write ASCII 0 to 31 in raw mode
        for i in range(32):
            fb.put_char(chr(i), raw=True)

        for i in range(32):
            cell = fb.get_cell(i, 0)
            assert cell is not None
            assert cell.char == CP437_LOW_GRAPHICS[i]

        # Write ASCII 127 in raw mode
        fb.cursor_goto(0, 1)
        fb.put_char(chr(127), raw=True)
        assert fb.get_cell(0, 1).char == "⌂"


def test_raw_mode_multiline_text():
    """
    Verify put_text(..., raw=True) writes \n and \r as literal characters ('◙' and '♪')
    without triggering line feeds or carriage returns.
    """
    for use_bin in (False, True):
        scr = Screen(width=10, height=2, use_binary=use_bin)
        scr.put_text("LINE1\nLINE2\rEND", raw=True)

        # Expected string: "LINE1◙LINE2♪END" (14 chars wrapped onto 10-col screen)
        expected = "LINE1\u25d9LINE2\u266aEND"
        for idx, expected_ch in enumerate(expected[:10]):
            assert scr.get_cell(idx, 0).char == expected_ch

        for idx, expected_ch in enumerate(expected[10:]):
            assert scr.get_cell(idx, 1).char == expected_ch


def test_raw_mode_color_and_attribute_preservation():
    """
    Verify that raw mode writes ONLY update character content and NEVER overwrite
    existing cell colors or text attributes.
    """
    for use_bin in (False, True):
        fb = frameBuffer(width=4, height=1, use_binary=use_bin)

        # Pre-populate cells with distinct colors and attributes
        colors = [
            (Color(255, 0, 0), Color(0, 0, 0), ATTR_BOLD),
            (Color(0, 255, 0), Color(20, 20, 20), ATTR_ITALIC),
            (Color(0, 0, 255), Color(40, 40, 40), ATTR_UNDERLINE),
            (Color(255, 255, 0), Color(60, 60, 60), ATTR_BOLD | ATTR_ITALIC),
        ]

        for x, (fg, bg, attrs) in enumerate(colors):
            fb.put_cell(x, 0, char="O", fg=fg, bg=bg, attrs=attrs)

        # Set current active graphics state to completely different colors
        fb.set_foreground(Color(255, 255, 255))
        fb.set_background(Color(128, 128, 128))
        fb.set_attrs(0)

        # Overwrite all cells in raw mode
        fb.cursor_goto(0, 0)
        fb.put_text("\x01\x02\x03\x04", raw=True)

        # Verify characters changed to CP437 glyphs while fg, bg, and attrs remain untouched
        expected_chars = ["☺", "☻", "♥", "♦"]
        for x, (orig_fg, orig_bg, orig_attrs) in enumerate(colors):
            cell = fb.get_cell(x, 0)
            assert cell.char == expected_chars[x]
            assert cell.fg == orig_fg
            assert cell.bg == orig_bg
            assert cell.attrs == orig_attrs


def test_raw_mode_cursor_wrapping():
    """
    Verify cursor wrapping behavior when writing long text in raw mode.
    """
    for use_bin in (False, True):
        fb = frameBuffer(width=5, height=3, use_binary=use_bin)
        raw_input = "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a"
        fb.put_text(raw_input, raw=True)

        # First row (5 chars)
        assert fb.get_cell(0, 0).char == CP437_LOW_GRAPHICS[1]
        assert fb.get_cell(4, 0).char == CP437_LOW_GRAPHICS[5]

        # Second row (5 chars)
        assert fb.get_cell(0, 1).char == CP437_LOW_GRAPHICS[6]
        assert fb.get_cell(4, 1).char == CP437_LOW_GRAPHICS[10]

        assert fb.cursor.x == 4
        assert fb.cursor.y == 1
