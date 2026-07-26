import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TerminalCapabilities:
    """
    Represents detected or overridden terminal color depth and graphics capabilities.
    """

    color_depth: str = "truecolor"  # "truecolor", "ansi256", "ansi16"
    graphics_protocol: str = "block"  # "kitty", "sixel", "iterm2", "block"
    override_color_depth: Optional[str] = None
    override_graphics_protocol: Optional[str] = None

    @property
    def active_color_depth(self) -> str:
        return self.override_color_depth or self.color_depth

    @property
    def active_graphics_protocol(self) -> str:
        return self.override_graphics_protocol or self.graphics_protocol


def detect_terminal_capabilities(env: Optional[Dict[str, str]] = None) -> TerminalCapabilities:
    """
    Inspects environment variables (TERM, COLORTERM, KITTY_WINDOW_ID, TERM_PROGRAM, etc.)
    to detect supported terminal color depth and graphics protocol.
    """
    if env is None:
        env = dict(os.environ)

    term = env.get("TERM", "").lower()
    colorterm = env.get("COLORTERM", "").lower()
    term_program = env.get("TERM_PROGRAM", "")
    kitty_window = env.get("KITTY_WINDOW_ID", "")
    lc_terminal = env.get("LC_TERMINAL", "")

    # 1. Color Depth Detection
    if colorterm in ("truecolor", "24bit"):
        color_depth = "truecolor"
    elif "256color" in term:
        color_depth = "ansi256"
    elif term == "dumb":
        color_depth = "ansi16"
    else:
        color_depth = "truecolor"

    # 2. Terminal Graphics Protocol Detection
    if kitty_window or term == "xterm-kitty" or term_program == "kitty":
        graphics_protocol = "kitty"
    elif term_program in ("iTerm.app", "WezTerm") or lc_terminal == "iTerm2":
        graphics_protocol = "iterm2"
    elif term in ("mlterm", "foot", "xterm-vt340") or "XTERM_VERSION" in env:
        graphics_protocol = "sixel"
    else:
        graphics_protocol = "block"

    return TerminalCapabilities(color_depth=color_depth, graphics_protocol=graphics_protocol)
