from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..cell import (
    Cell,
    ATTR_BOLD,
    ATTR_FAINT,
    ATTR_ITALIC,
    ATTR_UNDERLINE,
    ATTR_BLINK,
    ATTR_INVERSE,
    ATTR_CONCEAL,
    ATTR_STRIKE,
)
from ..color.rgb import Color
from ..color.palette import create_ansi_16_palette, create_ansi_256_palette
from ..color.quantize import quantize_exact, quantize_nearest_hsv
from ..screen import Screen


ANSI16 = create_ansi_16_palette()
ANSI256 = create_ansi_256_palette()


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    def contains(self, x: int, y: int) -> bool:
        return (self.x <= x < self.x + self.width) and (self.y <= y < self.y + self.height)


# -------------------------
# ANSI-space state tracking
# -------------------------

@dataclass(frozen=True)
class AnsiColorState:
    """
    How a color is represented in ANSI space.
    """
    kind: str  # "default" | "ansi16" | "ansi256" | "truecolor" | "dos"
    value: Tuple[int, ...]  # ansi16: (idx,) ansi256: (idx,) truecolor: (r,g,b) dos: (base, bright_flag, ice_bg_flag)


@dataclass(frozen=True)
class TerminalState:
    fg: AnsiColorState
    bg: AnsiColorState
    attrs: int  # ANSI attrs bitmask as *intended* (after DOS/ICE normalization)


class ANSIEmitter:
    """
    Emitter that diffs terminal *intent* in ANSI space.
    - Compile each cell into desired ANSI encoding (attrs + fg + bg)
    - Diff against previous terminal state
    - Emit only what changes (1 SGR max per cell; DOS may force reset + SGR)
    """

    def __init__(
        self,
        *,
        palette=None,                 # if set, quantize to this palette (index space)
        dos_mode: bool = False,       # CP437-ish / DOS SGR semantics
        ice_mode: bool = False,       # in DOS mode, use blink bit for bright background
    ):
        self.palette = palette
        self.dos_mode = dos_mode
        self.ice_mode = ice_mode

    # -------------------------
    # Public API
    # -------------------------

    def emit(self, screen: Screen, box: Optional[Box] = None) -> str:
        out: List[str] = []
        if box is None:
            start_x, start_y = 0, 0
            width, height = screen.width, screen.height
        else:
            start_x, start_y = box.x, box.y
            width, height = box.width, box.height
        # hard reset + home
        out.append("\x1b[0m")
        # Terminal starts in ANSI reset defaults: fg=7 bg=0 attrs=0
        prev = TerminalState(
            fg=AnsiColorState("ansi16", (7,)),
            bg=AnsiColorState("ansi16", (0,)),
            attrs=0,
        )
        for row in range(height):
            y = start_y + row
            for col in range(width):
                x = start_x + col
                cell = screen.get_cell(x, y) or Cell()
                desired = self._compile_cell(prev, cell)
                seq, prev = self._emit_transition(prev, desired)
                if seq:
                    out.append(seq)
                ch = cell.char
                if self._dos_colors_match(prev.fg, prev.bg):
                    ch = "█"
                out.append(ch or ' ')
            out.append("\x1b[0m")
            out.append("\n")
            prev = TerminalState(
                fg=AnsiColorState("ansi16", (7,0)),
                bg=AnsiColorState("ansi16", (0,0)),
                attrs=0,
            )
        return "".join(out)

        # -------------------------
        # Compile: Cell -> Desired TerminalState
        # -------------------------

    def _compile_cell(self, prev: TerminalState, cell: Cell) -> TerminalState:
        # None means "inherit / no change"
        fg_color = cell.fg
        bg_color = cell.bg
        # Normalize attrs for DOS rules:
        # - FAINT has no meaning in DOS
        # - BLINK is suppressed in ICE mode (bit is used for bg intensity)
        attrs = cell.attrs
        if self.dos_mode:
            attrs &= ~ATTR_FAINT
            if self.ice_mode:
                attrs &= ~ATTR_BLINK
        fg_state = prev.fg if fg_color is None else self._encode_color(fg_color, fg=True)
        bg_state = prev.bg if bg_color is None else self._encode_color(bg_color, fg=False)
        return TerminalState(fg=fg_state, bg=bg_state, attrs=attrs)

    def _dos_colors_match(self, fg: AnsiColorState, bg: AnsiColorState) -> bool:
        if fg.kind in [ 'dos' ] or bg.kind in [ 'dos' ]:
            fg_base, fg_bright = fg.value
            bg_base, bg_bright = bg.value
            return (fg_base == bg_base) and (fg_bright == bg_bright)
        return False

    # -------------------------
    # Encode RGB -> ANSI-space representation + implied SGR
    # -------------------------

    def _encode_color(self, color: Color, *, fg: bool) -> AnsiColorState:
        if self.dos_mode:
            # DOS: map to ANSI16 via HSV; represent as base(0-7) + bright flag
            idx = quantize_nearest_hsv(color, ANSI16)
            base = idx & 0x07
            bright = 1 if idx >= 8 else 0
            return AnsiColorState("dos", (base, bright))
        # Forced palette: always encode in that palette’s index space (ansi256 SGR form)
        if self.palette is not None:
            idx = quantize_nearest_hsv(color, self.palette)
            if idx<16:
                return AnsiColorState("ansi16", (idx,))
            return AnsiColorState("ansi256", (idx,))
        # Exact-match minimization: prefer ansi16 then ansi256 then truecolor
        idx16 = quantize_exact(color, ANSI16)
        if idx16 is not None:
            return AnsiColorState("ansi16", (idx16,))
        idx256 = quantize_exact(color, ANSI256)
        if idx256 is not None:
            return AnsiColorState("ansi256", (idx256,))
        return AnsiColorState("truecolor", (color.r, color.g, color.b))

    # -------------------------
    # Emit: diff prev->desired in ANSI-space
    # -------------------------

    def _emit_transition(self, prev: TerminalState, desired: TerminalState) -> Tuple[str, TerminalState]:
        # DOS brightness OFF edge case:
        # If previously bright FG and new FG is not bright, safest is reset + reapply.
        # (Because “22” behavior is inconsistent across DOS-ish terminals.)
        needs_reset = False
        if self.dos_mode and prev.fg.kind == "dos" and desired.fg.kind == "dos":
            prev_base, prev_bright = prev.fg.value
            _, new_bright = desired.fg.value
            if prev_bright == 1 and new_bright == 0:
                needs_reset = True
        if needs_reset:
            # After reset, terminal is at defaults:
            reset_state = TerminalState(
                fg=AnsiColorState("ansi16", (7,)),
                bg=AnsiColorState("ansi16", (0,)),
                attrs=0,
            )
            # Now emit transition from reset_state to desired
            sgr = self._build_sgr(reset_state, desired)
            if sgr:
                return "\x1b[0m" + sgr, desired
            return "\x1b[0m", desired
        sgr = self._build_sgr(prev, desired)
        return (sgr, desired) if sgr else ("", desired)

    def _build_sgr(self, prev: TerminalState, desired: TerminalState) -> str:
        codes: List[str] = []
        # Attributes: if changed, emit full intended set (simple + deterministic)
        reset=False
        if desired.attrs != prev.attrs:
            # If attrs becomes 0, a single 0 is correct/minimal
            if desired.attrs == 0:
                codes.append("0")
                reset = True
            else:
                if desired.attrs & ATTR_BOLD: codes.append("1")
                if (not self.dos_mode) and (desired.attrs & ATTR_FAINT): codes.append("2")
                if desired.attrs & ATTR_ITALIC: codes.append("3")
                if desired.attrs & ATTR_UNDERLINE: codes.append("4")
                if desired.attrs & ATTR_BLINK: codes.append("5")  # already suppressed under ICE compile
                if desired.attrs & ATTR_INVERSE: codes.append("7")
                if desired.attrs & ATTR_CONCEAL: codes.append("8")
                if desired.attrs & ATTR_STRIKE: codes.append("9")
        # Foreground / Background: compare ANSI-space representation
        if desired.fg != prev.fg or reset:
            codes.extend(self._color_state_to_sgr(desired.fg, fg=True))
        if desired.bg != prev.bg or reset:
            codes.extend(self._color_state_to_sgr(desired.bg, fg=False))
        if not codes:
            return ""
        return "\x1b[" + ";".join(codes) + "m"

    def _color_state_to_sgr(self, st: AnsiColorState, *, fg: bool) -> List[str]:
        if st.kind == "ansi16":
            (idx,) = st.value
            if idx < 8:
                return [str((30 if fg else 40) + idx)]
            return [str((90 if fg else 100) + (idx - 8))]
        if st.kind == "ansi256":
            (idx,) = st.value
            return [f"{38 if fg else 48};5;{idx}"]
        if st.kind == "truecolor":
            r, g, b = st.value
            return [f"{38 if fg else 48};2;{r};{g};{b}"]
        if st.kind == "dos":
            base, bright = st.value
            seq: List[str] = []
            # In DOS: bright FG is achieved via bold (1)
            # In ICE: bright BG achieved via blink (5)
            if fg:
                if bright:
                    seq.append("1")
                seq.append(str(30 + base))
            else:
                if bright and self.ice_mode:
                    seq.append("5")
                seq.append(str(40 + base))
            return seq
        # "default" isn't used in this implementation, but keep it sane
        return ["39"] if fg else ["49"]
