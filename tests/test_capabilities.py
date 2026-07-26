import pytest
from libansiscreen.screen import Screen
from libansiscreen.capabilities import detect_terminal_capabilities, TerminalCapabilities


def test_terminal_capabilities_environment_detection():
    # 1. Kitty Terminal Detection
    env_kitty = {"TERM": "xterm-kitty", "COLORTERM": "truecolor"}
    caps_kitty = detect_terminal_capabilities(env_kitty)
    assert caps_kitty.active_color_depth == "truecolor"
    assert caps_kitty.active_graphics_protocol == "kitty"

    # 2. iTerm2 / WezTerm Detection
    env_iterm = {"TERM_PROGRAM": "iTerm.app", "COLORTERM": "truecolor"}
    caps_iterm = detect_terminal_capabilities(env_iterm)
    assert caps_iterm.active_graphics_protocol == "iterm2"

    # 3. Sixel Terminal Detection
    env_sixel = {"TERM": "xterm-vt340"}
    caps_sixel = detect_terminal_capabilities(env_sixel)
    assert caps_sixel.active_graphics_protocol == "sixel"

    # 4. ANSI 256 Color Depth
    env_256 = {"TERM": "xterm-256color"}
    caps_256 = detect_terminal_capabilities(env_256)
    assert caps_256.active_color_depth == "ansi256"

    # 5. Dumb Terminal (ANSI 16)
    env_dumb = {"TERM": "dumb"}
    caps_dumb = detect_terminal_capabilities(env_dumb)
    assert caps_dumb.active_color_depth == "ansi16"


def test_screen_capability_methods_and_overrides():
    screen = Screen(width=20)

    # Detect from custom env
    screen.detect_capabilities({"KITTY_WINDOW_ID": "12345", "COLORTERM": "truecolor"})
    assert screen.get_graphics_protocol() == "kitty"
    assert screen.get_color_depth() == "truecolor"

    # Force overrides
    screen.force_graphics_protocol("sixel")
    assert screen.get_graphics_protocol() == "sixel"

    screen.force_color_depth("ansi256")
    assert screen.get_color_depth() == "ansi256"

    # Clear overrides
    screen.force_graphics_protocol(None)
    assert screen.get_graphics_protocol() == "kitty"

    screen.force_color_depth(None)
    assert screen.get_color_depth() == "truecolor"
