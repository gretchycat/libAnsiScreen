from pathlib import Path

from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.renderer.ansi_emitter import ANSIEmitter

from libansiscreen.screen_ops.colorize import colorize

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
# Builders
# ------------------------------------------------------------

from libansiscreen.screen_ops.prim import box
from libansiscreen.screen_ops.clear import clear
from libansiscreen.renderer.ansi_emitter import Box
from libansiscreen.screen_ops.glyph_defs import BOX_BLOCK


def build_solid_block_screen(
    width: int = 20,
    height: int = 10,
) -> Screen:
    """
    Create a solid block screen using the box primitive,
    then clear a central region using the clear operation.
    """
    # Create a solid block screen
    screen = box(
        width,
        height,
        glyphs=BOX_BLOCK,
    )

    # Define a central box (middle 50%)
    cx0 = width // 4
    cy0 = height // 4
    cx1 = width * 3 // 4
    cy1 = height * 3 // 4

    center_box = Box(
        cx0,
        cy0,
        cx1 - cx0,
        cy1 - cy0,
    )

    # Clear the central region (sets char/fg/bg to None)
    clear(screen, box=center_box)

    return screen

def build_gradient() -> list[Color]:
    """
    Simple RGB gradient for testing.
    """
    return [
        Color(255, 0, 0),     # red
        Color(255, 255, 0),   # yellow
        Color(0, 255, 0),     # green
        Color(0, 255, 255),   # cyan
        Color(0, 0, 255),     # blue
        Color(255, 0, 255),   # magenta
    ]


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def colorize_horizontal_fg_only_if_set():
    screen = build_solid_block_screen()
    grad = build_gradient()
    colorize(
        screen,
        gradient=grad,
        mode="horizontal",
        only_if_set=True,
    )
    return screen

def test_colorize_horizontal_fg_only_if_set():
    screen= colorize_horizontal_fg_only_if_set()
    # Solid area should be colored
    assert screen.get_cell(0, 0).fg is not None
    # Cleared center should remain untouched
    cx = screen.width // 2
    cy = screen.height // 2
    assert screen.get_cell(cx, cy).fg is None


def colorize_vertical_bg_replace():
    screen = build_solid_block_screen()
    grad = build_gradient()

    colorize(
        screen,
        gradient=grad,
        mode="vertical",
        background=True,
        foreground=False,
    )
    return screen

def test_colorize_vertical_bg_replace():
    screen=colorize_vertical_bg_replace()
    assert screen.get_cell(0, 0).bg is not None
    assert screen.get_cell(screen.width - 1, 0).bg is not None


def colorize_diag_tint():
    screen = build_solid_block_screen()
    grad = build_gradient()
    # First pass: hard foreground
    colorize(
        screen,
        gradient=grad,
        mode="diag",
    )
    return screen

def test_colorize_diag_tint():
    screen=colorize_diag_tint()
    fg_after = screen.get_cell(0, 0).fg
    assert fg_after is not None
    #assert fg_after != fg_before


def colorize_words():
    screen = Screen(30)

    text = "Hello world from ANSI"
    for i, ch in enumerate(text):
        screen.put_cell(i, 0, char=ch)

    grad = [
        Color(255, 0, 0),
        Color(0, 255, 0),
        Color(0, 0, 255),
    ]

    colorize(
        screen,
        gradient=grad,
        mode="words",
    )
    return screen

def test_colorize_words():
    screen=colorize_words()
    # H, e, l should differ
    assert screen.get_cell(0, 0).fg != screen.get_cell(1, 0).fg
    assert screen.get_cell(1, 0).fg != screen.get_cell(2, 0).fg

    # Space resets word
    assert screen.get_cell(5, 0).char == " "


# ------------------------------------------------------------
# Manual / visual execution
# ------------------------------------------------------------

def main():
    emit(colorize_horizontal_fg_only_if_set(), "colorize_hotizontal_fg.ans")
    emit(colorize_vertical_bg_replace(), "colorize_vertical_bg.ans")
    emit(colorize_diag_tint(), "colorize_diag_tint.ans")
    emit(colorize_words(), "colorize_words.ans")

    print("Colorize visual tests complete.")


if __name__ == "__main__":
    main()
