#!/usr/bin/env python3

import sys
from pathlib import Path

from linansiscreen.screen import Screen
from linansiscreen.parser.ansi_parser import ANSIParser
from linansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
from linansiscreen.color.palette import (
    create_ansi_16_palette,
    create_ansi_256_palette,
)

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

OUTPUT_BASE = "emitter_out_mode"
DEFAULT_WIDTH = 80

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def parse_ansi(path: Path, *, width=DEFAULT_WIDTH, box=None) -> Screen:
    screen = Screen(width=width)
    parser = ANSIParser(screen)
    parser.feed(path.read_bytes())
    return screen


def write(name: str, data: str):
    path = Path(name)
    path.write_text(data, encoding="utf-8")
    print(f"Wrote {path}")

# ------------------------------------------------------------
# Rendering modes
# ------------------------------------------------------------

def render_all(screen: Screen):
    # Modern (auto / truecolor where needed)
    emitter = ANSIEmitter()
    write(f"{OUTPUT_BASE}.modern.ans", emitter.emit(screen))

    # ANSI 256
    emitter = ANSIEmitter(palette=create_ansi_256_palette())
    write(f"{OUTPUT_BASE}.ansi256.ans", emitter.emit(screen))

    # ANSI 16
    emitter = ANSIEmitter(palette=create_ansi_16_palette())
    write(f"{OUTPUT_BASE}.ansi16.ans", emitter.emit(screen))

    # DOS
    emitter = ANSIEmitter(dos_mode=True)
    write(f"{OUTPUT_BASE}.dos.ans", emitter.emit(screen))

    # DOS + ICE
    emitter = ANSIEmitter(dos_mode=True, ice_mode=True)
    write(f"{OUTPUT_BASE}.dos_ice.ans", emitter.emit(screen))

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: test_emitter.py <ansi-file>")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    print(f"\n=== Processing {input_path} ===")

    screen = parse_ansi(input_path)
    render_all(screen)


if __name__ == "__main__":
    main()
