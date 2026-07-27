"""
Sextant Character Grid Test Program

Displays all 64 sextant characters (0x00 - 0x3F) on a grid with:
- Pure black background for actual character cells so subpixel shapes stand out against pure black.
- Semi-solid background for headers, cell spacing, and inter-row spacer lines.
- Precise 1-to-1 character column count matching between horizontal headers and data rows.
"""

import os
import sys

# Ensure current script directory and workspace root are in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

try:
    from sextants import get_sextant_array
except ImportError:
    from octant_investigation.sextants import get_sextant_array

# ANSI Color formatting for terminal display
BG_SEMISOLID = "\033[48;2;35;45;65m"
BG_BLACK = "\033[48;2;0;0;0m"
FG_BRIGHT = "\033[38;2;255;230;100m"
HEADER_COLOR = "\033[1;36m"  # Bold Cyan
RESET = "\033[0m"

HEX_DIGITS = [f"{i:x}" for i in range(16)]


def make_header(cols):
    hdr_cells = "".join(f" {HEADER_COLOR}{c}{RESET}{BG_SEMISOLID} " for c in cols)
    return f"{BG_SEMISOLID}    {hdr_cells} {RESET}"


def make_spacer_row(num_cols):
    total_len = 4 + num_cols * 3 + 1
    return f"{BG_SEMISOLID}" + " " * total_len + f"{RESET}"


def make_data_row(r_label, chars_slice):
    row_str = f"{BG_SEMISOLID} {HEADER_COLOR}{r_label}{RESET}{BG_SEMISOLID} |{RESET}"
    for ch in chars_slice:
        row_str += f"{BG_SEMISOLID} {RESET}{BG_BLACK}{FG_BRIGHT}{ch}{RESET}{BG_SEMISOLID} {RESET}"
    row_str += f"{BG_SEMISOLID} {RESET}"
    return row_str


def render_8x8_sextant_grid(sextant_chars):
    lines = []
    cols = HEX_DIGITS[:8]
    lines.append("=== 8x8 SEXTANT CHARACTER GRID (0x00 - 0x3F) ===")
    lines.append(f"Characters render on pure black cells against a semi-solid background grid ({BG_SEMISOLID}   {RESET}).\n")

    lines.append(make_header(cols))
    lines.append(make_spacer_row(8))

    for r in range(8):
        chars_slice = sextant_chars[r * 8 : (r + 1) * 8]
        lines.append(make_data_row(HEX_DIGITS[r], chars_slice))
        lines.append(make_spacer_row(8))

    return "\n".join(lines)


def render_16x4_sextant_grid(sextant_chars):
    lines = []
    lines.append("=== 16x4 SEXTANT CHARACTER GRID (0x00 - 0x3F) ===")

    lines.append(make_header(HEX_DIGITS))
    lines.append(make_spacer_row(16))

    for r in range(4):
        chars_slice = sextant_chars[r * 16 : (r + 1) * 16]
        lines.append(make_data_row(HEX_DIGITS[r], chars_slice))
        lines.append(make_spacer_row(16))

    return "\n".join(lines)


def test_sextant_character_grid_integrity():
    chars = get_sextant_array()
    assert len(chars) == 64, "Sextant character array must contain 64 elements"
    grid_output = render_8x8_sextant_grid(chars)
    assert "8x8 SEXTANT CHARACTER GRID" in grid_output
    assert "7 |" in grid_output
    print("\nSextant grid test passed successfully!")


if __name__ == "__main__":
    chars = get_sextant_array()
    print(render_8x8_sextant_grid(chars))
    print("\n" + "=" * 53 + "\n")
    print(render_16x4_sextant_grid(chars))
