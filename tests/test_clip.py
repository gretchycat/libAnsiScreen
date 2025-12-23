from pathlib import Path

import sys
from libansiscreen.screen import Screen
from libansiscreen.parser.ansi_parser import ANSIParser
from libansiscreen.renderer.ansi_emitter import ANSIEmitter

from libansiscreen.screen_ops.copy import copy as screen_copy
from libansiscreen.screen_ops.clear import clear as screen_clear
from libansiscreen.screen_ops.paste import paste as screen_paste


def load_screen(path: Path) -> Screen:
    screen = Screen(width=80)
    parser = ANSIParser(screen)
    parser.feed(path.read_bytes())
    return screen


def middle_box(screen: Screen):
    """
    Return the middle 50% box of the screen as (x, y, w, h).
    """
    x = screen.width // 4
    y = screen.height // 4
    w = screen.width // 2
    h = screen.height // 2
    return (x, y, w, h)


def lower_right_origin(screen: Screen):
    """
    Return (x, y) for the lower-right quadrant origin.
    """
    x = screen.width // 2
    y = screen.height // 2
    return x, y


def emit(screen: Screen, out_path: Path):
    emitter = ANSIEmitter()
    ansi = emitter.emit(screen)
    out_path.write_text(ansi, encoding="utf-8")


def test_clip_pipeline():
    src_path = Path(sys.argv[1])
    assert src_path.exists(), "Missing input ANSI file"

    # Load original screen
    screen = load_screen(src_path)

    # Compute regions
    box = middle_box(screen)
    dst_x, dst_y = lower_right_origin(screen)

    # --- COPY ---
    buf = screen_copy(screen, box)
    emit(buf, Path("test_clip_copy_truecolor.ans"))

    # --- CLEAR ---
    screen_clear(screen, box)
    emit(screen, Path("test_clip_cleared.ans"))

    # --- PASTE ---
    screen_paste(
        screen,
        buf,
        box=(dst_x, dst_y, None, None),
    )
    emit(screen, Path("test_clip_pasted.ans"))


if __name__ == "__main__":
    test_clip_pipeline()
    print("test_clip_pipeline completed")
