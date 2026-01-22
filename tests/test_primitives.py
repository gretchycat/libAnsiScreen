from pathlib import Path

from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# Primitives
from libansiscreen.screen_ops.prim import (
    hline,
    vline,
    box,
    stamp_from_screen,
    char_flood_fill,
    char_rectangle,
    char_ellipse
)

# Glyph definitions (as you currently use them)
from libansiscreen.screen_ops.glyph_defs import (
    LINE_SINGLE_HORIZONTAL,
    LINE_SINGLE_VERTICAL,
    BOX_SINGLE,
    BOX_BLOCK,
)

from libansiscreen.renderer.ansi_emitter import ANSIEmitter


# ------------------------------------------------------------
# Output directory for visual inspection
# ------------------------------------------------------------

OUT = Path("out")
OUT.mkdir(exist_ok=True)


def emit(screen: Screen, name: str):
    ansi = ANSIEmitter().emit(screen)
    path = OUT / name
    path.write_text(ansi)
    print(f"Wrote {path}")


# ------------------------------------------------------------
# Builders (return Screen, reusable)
# ------------------------------------------------------------

def build_primitives_basic_composition() -> Screen:
    screen = Screen(10)

    box(
        8, 4,
        glyphs=BOX_SINGLE,
        screen=screen,
    )

    hline(
        1, 6,
        y=2,
        glyphs=LINE_SINGLE_HORIZONTAL,
        screen=screen,
        merge=True,
    )

    vline(
        1, 3,
        x=4,
        glyphs=LINE_SINGLE_VERTICAL,
        screen=screen,
        merge=True,
    )

    return screen


def build_block_box_and_stamp() -> Screen:
    src = box(
        8, 4,
        glyphs=BOX_BLOCK,
    )

    clr = Color(0, 0, 0)

    stamp = stamp_from_screen(
        src,
        transparent_chars=("█",),
        border_bg=clr,
    )

    return stamp

def build_ellipse() -> Screen:
    screen=Screen(width=40)
    screen.char_ellipse(20,12,8,8,Color(255,0,128))
    return screen

def build_rectangle() -> Screen:
    screen=Screen(width=40)
    screen.char_rectangle(5,2,30,8,Color(0,255,128))
    return screen

def build_flood_fill() -> Screen:
    screen=Screen(width=40)
    cyan=Color(0,255,192)
    yellow=Color(255,192,0)
    screen.regular_polygon(10, 10, 7, 12, cyan)
    screen.char_flood_fill(10,5, fill=yellow) 
    return screen

# ------------------------------------------------------------
# Tests (pytest-facing, return None)
# ------------------------------------------------------------

def test_primitives_basic_composition():
    screen = build_primitives_basic_composition()

    # Structural assertions
    assert screen.get_cell(4, 2).char == "┼"
    assert screen.get_cell(0, 0).char == "┌"
    assert screen.get_cell(7, 3).char == "┘"

    # Interior should remain transparent
    assert screen.get_cell(1, 1).char is None


def test_block_box_and_stamp():
    stamp = build_block_box_and_stamp()

    # Interior transparent
    assert stamp.get_cell(1, 1).char is None

    # Border cell has space + bg
    c = stamp.get_cell(0, 0)
    assert c.char == " "
    assert c.bg == Color(0, 0, 0)


# ------------------------------------------------------------
# Manual / visual execution
# ------------------------------------------------------------

def main():
    print("Running primitives visual tests…")

    emit(build_primitives_basic_composition(), "primitives_basic.ans")
    emit(build_block_box_and_stamp(), "primitives_stamp.ans")
    emit(build_ellipse(), "primitives_ellipse.ans")
    emit(build_rectangle(), "primitives_rectangle.ans")
    emit(build_flood_fill(), "primitives_flood_fillt.ans")

    print("Done.")


if __name__ == "__main__":
    main()
