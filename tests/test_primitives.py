from pathlib import Path

from linansiscreen.screen import Screen
from linansiscreen.color.rgb import Color

# Primitives
from linansiscreen.screen_ops.prim import (
    hline,
    vline,
    box,
    stamp_from_screen,
)

# Glyph definitions (as you currently use them)
from linansiscreen.screen_ops.glyph_defs import (
    LINE_SINGLE_HORIZONTAL,
    LINE_SINGLE_VERTICAL,
    BOX_SINGLE,
    BOX_BLOCK,
)

from linansiscreen.renderer.ansi_emitter import ANSIEmitter


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
        add_border=True,
        border_bg=clr,
    )

    return stamp


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

    print("Done.")


if __name__ == "__main__":
    main()
