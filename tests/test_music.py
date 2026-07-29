import pytest
from libansiscreen.framebuffer import frameBuffer
from libansiscreen.screen import Screen


def test_framebuffer_music_queue_direct_api():
    """
    Verify direct API for adding, retrieving, popping, and clearing music commands.
    """
    for use_bin in (False, True):
        fb = frameBuffer(width=10, height=2, use_binary=use_bin)
        assert fb.music_queue == []

        fb.add_music("T120 O3 L4 C D E F G")
        fb.add_music("T180 O4 L8 A B C")

        assert len(fb.music_queue) == 2
        assert fb.music_queue[0] == "T120 O3 L4 C D E F G"

        popped = fb.pop_music_queue()
        assert popped == ["T120 O3 L4 C D E F G", "T180 O4 L8 A B C"]
        assert fb.music_queue == []

        fb.add_music("T150 O2 C E G")
        fb.clear_music_queue()
        assert fb.music_queue == []


def test_ansi_parser_music_sequences():
    """
    Verify that ANSI Music escape sequences (\x1b[M...\x0e and \x1bN...\x0e)
    are automatically captured by ANSIParser and queued into the screen music_queue.
    """
    for use_bin in (False, True):
        scr = Screen(width=20, height=2, use_binary=use_bin)

        # ESC [ M <music_string> \x0e
        scr.feed("\x1b[M T120 O3 L4 C D E F G A B C\x0eText After Music")

        # ESC N <music_string> \x0e
        scr.feed("\x1bN T180 O4 L8 C# D# E#\x0eMore Text")

        music_cmds = scr.pop_music_queue()
        assert len(music_cmds) == 2
        assert music_cmds[0] == "T120 O3 L4 C D E F G A B C"
        assert music_cmds[1] == "T180 O4 L8 C# D# E#"

        # Ensure text surrounding music commands rendered into screen cells
        assert scr.get_cell(0, 0).char == "T"
        assert scr.get_cell(1, 0).char == "e"


def test_ansi_parser_numeric_music_sequences():
    """
    Verify CSI music sequence parameter parsing (e.g. \x1b[100;200;300M).
    """
    for use_bin in (False, True):
        scr = Screen(width=10, height=2, use_binary=use_bin)
        scr.feed("\x1b[440;880M")

        cmds = scr.pop_music_queue()
        assert cmds == ["440;880"]


def test_screen_feed_and_print_auto_music_parsing():
    """
    Verify that screen.feed() and screen.print() both automatically parse embedded ANSI music
    escape sequences directly into screen.music_queue while rendering surrounding text.
    """
    for use_bin in (False, True):
        scr = Screen(width=40, height=5, use_binary=use_bin)

        # Test screen.feed()
        scr.feed("\x1b[M T120 O3 L4 C D E F G A B C\x0eWELCOME TO THE BBS!\r\n")
        assert len(scr.music_queue) == 1
        assert scr.music_queue[0] == "T120 O3 L4 C D E F G A B C"

        # Pop music queue
        popped = scr.pop_music_queue()
        assert popped == ["T120 O3 L4 C D E F G A B C"]
        assert scr.music_queue == []

        # Verify surrounding text rendered into screen buffer
        assert scr.get_cell(0, 0).char == "W"
        assert scr.get_cell(1, 0).char == "E"

        # Test screen.print() alias
        scr.print("\x1bN T180 O4 L8 C# D# E#\x0ePLAYING MUSIC NOW\r\n")
        assert len(scr.music_queue) == 1
        assert scr.music_queue[0] == "T180 O4 L8 C# D# E#"

        popped_2 = scr.pop_music_queue()
        assert popped_2 == ["T180 O4 L8 C# D# E#"]
        assert scr.music_queue == []
        assert scr.get_cell(0, 1).char == "P"

