# =========================
# Block glyphs
# =========================

BLOCK_FULL = "█"
BLOCK_TOP = "▀"
BLOCK_BOTTOM = "▄"
BLOCK_LEFT="▌"
BLOCK_RIGHT="▐"

# =========================
# Single-line box glyphs
# =========================

LINE_SINGLE_H = "─"
LINE_SINGLE_V = "│"

LINE_SINGLE_TL = "┌"
LINE_SINGLE_TR = "┐"
LINE_SINGLE_BL = "└"
LINE_SINGLE_BR = "┘"

# =========================
# Double-line box glyphs
# =========================

LINE_DOUBLE_H = "═"
LINE_DOUBLE_V = "║"

LINE_DOUBLE_TL = "╔"
LINE_DOUBLE_TR = "╗"
LINE_DOUBLE_BL = "╚"
LINE_DOUBLE_BR = "╝"

# =========================
# ASCII fallback glyphs
# =========================

ASCII_H = "-"
ASCII_V = "|"
ASCII_CORNER = "+"

BOX_SINGLE = {
    "tl": LINE_SINGLE_TL,
    "tr": LINE_SINGLE_TR,
    "bl": LINE_SINGLE_BL,
    "br": LINE_SINGLE_BR,
    "h":  LINE_SINGLE_H,
    "v":  LINE_SINGLE_V,
    "fill": None,

    # No half-block support
    "top": None,
    "bottom": None,
}

BOX_DOUBLE = {
    "tl": LINE_DOUBLE_TL,
    "tr": LINE_DOUBLE_TR,
    "bl": LINE_DOUBLE_BL,
    "br": LINE_DOUBLE_BR,
    "h":  LINE_DOUBLE_H,
    "v":  LINE_DOUBLE_V,
    "fill": None,

    "top": None,
    "bottom": None,
}

LINE_SINGLE_HORIZONTAL = {
    "start": LINE_SINGLE_H,
    "segment": LINE_SINGLE_H,
    "end": LINE_SINGLE_H,
}
LINE_SINGLE_VERTICAL = {
    "start": LINE_SINGLE_V,
    "segment": LINE_SINGLE_V,
    "end": LINE_SINGLE_V,
}
LINE_BLOCK_VERTICAL = {
    "start": BLOCK_FULL,
    "segment": BLOCK_FULL,
    "end": BLOCK_FULL,

    "top": BLOCK_TOP,
    "bottom": BLOCK_BOTTOM,
}

BOX_BLOCK = {
    "tl": BLOCK_FULL,
    "tr": BLOCK_FULL,
    "bl": BLOCK_FULL,
    "br": BLOCK_FULL,
    "h":  BLOCK_FULL,
    "v":  BLOCK_FULL,
    "fill": BLOCK_FULL,

    # Optional vertical-resolution hints
    "top": BLOCK_TOP,
    "bottom": BLOCK_BOTTOM,
}
