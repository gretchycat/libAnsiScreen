# libansiscreen/ansi/parser.py

from typing import List

from ..screen import Screen
from ..cell import (
    ATTR_BOLD,
    ATTR_FAINT,
    ATTR_UNDERLINE,
    ATTR_BLINK,
    ATTR_INVERSE,
    ATTR_CONCEAL,
    ATTR_ITALIC,
    ATTR_STRIKE,
)
from ..color.rgb import Color
from ..color.palette import (
    create_ansi_16_palette,
    create_ansi_256_palette,
)

# ----------------------------------------------------------------------
# Palettes (facts, not policy)
# ----------------------------------------------------------------------

ANSI16 = create_ansi_16_palette()
ANSI256 = create_ansi_256_palette()


class ANSIParser:
    """
    Streaming ANSI parser that mutates a Screen.

    This is a document parser, not a terminal emulator.
    """

    TEXT = 0
    ESC = 1
    CSI = 2

    def __init__(self, screen: Screen):
        self.screen = screen
        self.state = self.TEXT
        self.params: List[int] = []
        self.param_buf: str = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def feed(self, data, encoding='utf-8') -> None:
        if isinstance(data, (bytes, bytearray)):
            data = data.decode(encoding, errors="surrogateescape")

        for ch in data:
            self._process_char(ch)

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def _process_char(self, ch: str) -> None:
        if self.state == self.TEXT:
            self._state_text(ch)
        elif self.state == self.ESC:
            self._state_esc(ch)
        elif self.state == self.CSI:
            self._state_csi(ch)

    # ------------------------------------------------------------------
    # TEXT
    # ------------------------------------------------------------------

    def _state_text(self, ch: str) -> None:
        if ch == "\x1b":
            self.state = self.ESC
        elif ch == "\n":
            self.screen.newline()
        elif ch == "\r":
            self.screen.carriage_return()
        else:
            self.screen.put_char(ch)

    # ------------------------------------------------------------------
    # ESC
    # ------------------------------------------------------------------

    def _state_esc(self, ch: str) -> None:
        if ch == "[":
            self.state = self.CSI
            self.params.clear()
            self.param_buf = ""
        elif ch == "7":  # DECSC
            self.screen.cursor_save()
            self.state = self.TEXT
        elif ch == "8":  # DECRC
            self.screen.cursor_restore()
            self.state = self.TEXT
        else:
            # Unsupported ESC sequence
            self.state = self.TEXT

    # ------------------------------------------------------------------
    # CSI
    # ------------------------------------------------------------------

    def _state_csi(self, ch: str) -> None:
        if ch.isdigit():
            self.param_buf += ch
        elif ch == ";":
            self._flush_param()
        else:
            self._flush_param()
            self._dispatch_csi(ch)
            self.state = self.TEXT

    def _flush_param(self) -> None:
        if self.param_buf:
            self.params.append(int(self.param_buf))
            self.param_buf = ""
        else:
            self.params.append(0)

    # ------------------------------------------------------------------
    # CSI dispatch
    # ------------------------------------------------------------------

    def _dispatch_csi(self, final: str) -> None:
        p = self.params or [0]

        if final == "A":  # CUU
            self.screen.cursor_up(p[0] or 1)

        elif final == "B":  # CUD
            self.screen.cursor_down(p[0] or 1)

        elif final == "C":  # CUF
            self.screen.cursor_forward(p[0] or 1)

        elif final == "D":  # CUB
            self.screen.cursor_back(p[0] or 1)

        elif final in ("H", "f"):  # CUP / HVP
            y = (p[0] - 1) if len(p) > 0 else 0
            x = (p[1] - 1) if len(p) > 1 else 0
            self.screen.cursor_goto(x, y)

        elif final == "J":  # ED
            if p[0] == 0:
                self.screen.clear_to_end_of_screen()
            elif p[0] == 2:
                self.screen.clear()

        elif final == "K":  # EL
            self.screen.clear_to_end_of_line()

        elif final == "m":  # SGR
            self._handle_sgr(p)

    # ------------------------------------------------------------------
    # SGR handling
    # ------------------------------------------------------------------

    def _handle_sgr(self, params: List[int]) -> None:
        if not params:
            params = [0]

        i = 0
        while i < len(params):
            code = params[i]

            # ----------------------------
            # Reset
            # ----------------------------

            if code == 0:
                self.screen.reset_graphics()

            # ----------------------------
            # Attributes
            # ----------------------------

            elif code == 1:
                self.screen.add_attrs(ATTR_BOLD)

            elif code == 2:
                self.screen.add_attrs(ATTR_FAINT)

            elif code == 3:
                self.screen.add_attrs(ATTR_ITALIC)

            elif code == 4:
                self.screen.add_attrs(ATTR_UNDERLINE)

            elif code == 5:
                self.screen.add_attrs(ATTR_BLINK)

            elif code == 7:
                self.screen.add_attrs(ATTR_INVERSE)

            elif code == 8:
                self.screen.add_attrs(ATTR_CONCEAL)

            elif code == 9:
                self.screen.add_attrs(ATTR_STRIKE)

            elif code == 22:
                self.screen.clear_attrs(ATTR_BOLD | ATTR_FAINT)

            elif code == 23:
                self.screen.clear_attrs(ATTR_ITALIC)

            elif code == 24:
                self.screen.clear_attrs(ATTR_UNDERLINE)

            elif code == 25:
                self.screen.clear_attrs(ATTR_BLINK)

            elif code == 27:
                self.screen.clear_attrs(ATTR_INVERSE)

            elif code == 28:
                self.screen.clear_attrs(ATTR_CONCEAL)

            elif code == 29:
                self.screen.clear_attrs(ATTR_STRIKE)

            # ----------------------------
            # ANSI16 colors
            # ----------------------------

            elif 30 <= code <= 37:
                self.screen.set_foreground(ANSI16.index_to_rgb(code - 30))

            elif 40 <= code <= 47:
                self.screen.set_background(ANSI16.index_to_rgb(code - 40))

            elif 90 <= code <= 97:
                self.screen.set_foreground(
                    ANSI16.index_to_rgb(code - 90 + 8)
                )

            elif 100 <= code <= 107:
                self.screen.set_background(
                    ANSI16.index_to_rgb(code - 100 + 8)
                )

            elif code == 39:
                self.screen.set_foreground(ANSI16.index_to_rgb(7))

            elif code == 49:
                self.screen.set_background(ANSI16.index_to_rgb(0))

            # ----------------------------
            # ANSI256 colors
            # ----------------------------

            elif code == 38 and i + 2 < len(params) and params[i + 1] == 5:
                idx = params[i + 2]
                self.screen.set_foreground(ANSI256.index_to_rgb(idx))
                i += 2

            elif code == 48 and i + 2 < len(params) and params[i + 1] == 5:
                idx = params[i + 2]
                self.screen.set_background(ANSI256.index_to_rgb(idx))
                i += 2

            # ----------------------------
            # Truecolor
            # ----------------------------

            elif code == 38 and i + 4 < len(params) and params[i + 1] == 2:
                r, g, b = params[i + 2:i + 5]
                self.screen.set_foreground(Color(r, g, b))
                i += 4

            elif code == 48 and i + 4 < len(params) and params[i + 1] == 2:
                r, g, b = params[i + 2:i + 5]
                self.screen.set_background(Color(r, g, b))
                i += 4

            # ----------------------------
            # Unknown / ignored
            # ----------------------------

            i += 1
