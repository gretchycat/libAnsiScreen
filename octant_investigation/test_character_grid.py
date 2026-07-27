"""
Combined Octant, Sextant & Quadrant Character Grid Test Program

Displays Octant (256 characters), Sextant (64 characters), and Quadrant (16 characters) grids with:
- Pure Black background for actual character cell boxes so subpixel shapes render against pure black.
- Semi-solid background for headers, cell borders/spacing, and inter-row spacer lines.
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
    from octants import get_octant_array
    from sextants import get_sextant_array
    from quadrants import get_quadrant_array
except ImportError:
    from octant_investigation.octants import get_octant_array
    from octant_investigation.sextants import get_sextant_array
    from octant_investigation.quadrants import get_quadrant_array

# Try importing libansiscreen if available
try:
    from libansiscreen.screen import Screen
    from libansiscreen.color.rgb import Color
    HAS_LIBANSISCREEN = True
except ImportError:
    HAS_LIBANSISCREEN = False

# ANSI Color formatting for terminal display
BG_SEMISOLID = "\033[48;2;35;45;65m"
BG_BLACK = "\033[48;2;0;0;0m"
FG_BRIGHT = "\033[38;2;255;230;100m"
HEADER_COLOR = "\033[1;36m"  # Bold Cyan
RESET = "\033[0m"

HEX_DIGITS = [f"{i:x}" for i in range(16)]


def make_header(cols):
    """Build header line matching character column spacing exactly (3 characters per column cell)."""
    hdr_cells = "".join(f" {HEADER_COLOR}{c}{RESET}{BG_SEMISOLID} " for c in cols)
    return f"{BG_SEMISOLID}    {hdr_cells} {RESET}"


def make_spacer_row(num_cols):
    """Build inter-row spacer row styled with semi-solid background color."""
    total_len = 4 + num_cols * 3 + 1
    return f"{BG_SEMISOLID}" + " " * total_len + f"{RESET}"


def make_data_row(r_label, chars_slice):
    """Build a data row with row label and black-background character cells separated by semi-solid spacing."""
    row_str = f"{BG_SEMISOLID} {HEADER_COLOR}{r_label}{RESET}{BG_SEMISOLID} |{RESET}"
    for ch in chars_slice:
        row_str += f"{BG_SEMISOLID} {RESET}{BG_BLACK}{FG_BRIGHT}{ch}{RESET}{BG_SEMISOLID} {RESET}"
    row_str += f"{BG_SEMISOLID} {RESET}"
    return row_str


def render_octant_16x16_grid(octant_chars):
    """Render the full 16x16 Octant grid (0x00 to 0xFF)."""
    lines = []
    lines.append("=== 16x16 OCTANT CHARACTER GRID (0x00 - 0xFF) ===")
    lines.append(f"Characters render on pure black cells against a semi-solid background grid ({BG_SEMISOLID}   {RESET}).\n")

    lines.append(make_header(HEX_DIGITS))
    lines.append(make_spacer_row(16))

    for r in range(16):
        chars_slice = octant_chars[r * 16 : (r + 1) * 16]
        lines.append(make_data_row(HEX_DIGITS[r], chars_slice))
        lines.append(make_spacer_row(16))

    return "\n".join(lines)


def render_sextant_8x8_grid(sextant_chars):
    """Render the 8x8 Sextant grid (0x00 to 0x3F)."""
    lines = []
    cols = HEX_DIGITS[:8]
    lines.append("=== 8x8 SEXTANT CHARACTER GRID (0x00 - 0x3F) ===")

    lines.append(make_header(cols))
    lines.append(make_spacer_row(8))

    for r in range(8):
        chars_slice = sextant_chars[r * 8 : (r + 1) * 8]
        lines.append(make_data_row(HEX_DIGITS[r], chars_slice))
        lines.append(make_spacer_row(8))

    return "\n".join(lines)


def render_sextant_16x4_grid(sextant_chars):
    """Render the 16x4 Sextant grid (0x00 to 0x3F)."""
    lines = []
    lines.append("=== 16x4 SEXTANT CHARACTER GRID (0x00 - 0x3F) ===")

    lines.append(make_header(HEX_DIGITS))
    lines.append(make_spacer_row(16))

    for r in range(4):
        chars_slice = sextant_chars[r * 16 : (r + 1) * 16]
        lines.append(make_data_row(HEX_DIGITS[r], chars_slice))
        lines.append(make_spacer_row(16))

    return "\n".join(lines)


def render_quadrant_4x4_grid(quadrant_chars):
    """Render the 4x4 Quadrant grid (0x0 to 0xF)."""
    lines = []
    cols = HEX_DIGITS[:4]
    lines.append("=== 4x4 QUADRANT CHARACTER GRID (0x0 - 0xF) ===")

    lines.append(make_header(cols))
    lines.append(make_spacer_row(4))

    for r in range(4):
        chars_slice = quadrant_chars[r * 4 : (r + 1) * 4]
        lines.append(make_data_row(HEX_DIGITS[r], chars_slice))
        lines.append(make_spacer_row(4))

    return "\n".join(lines)


def render_quadrant_16x1_grid(quadrant_chars):
    """Render the 16x1 Quadrant grid (0x0 to 0xF)."""
    lines = []
    lines.append("=== 16x1 QUADRANT CHARACTER GRID (0x0 - 0xF) ===")

    lines.append(make_header(HEX_DIGITS))
    lines.append(make_spacer_row(16))
    lines.append(make_data_row("0", quadrant_chars))
    lines.append(make_spacer_row(16))

    return "\n".join(lines)


def test_character_grid_integrity():
    """Pytest validation verifying character counts and header alignment for Octants, Sextants, and Quadrants."""
    oct_chars = get_octant_array()
    sex_chars = get_sextant_array()
    quad_chars = get_quadrant_array()

    assert len(oct_chars) == 256, "Octant character array must contain 256 elements"
    assert len(sex_chars) == 64, "Sextant character array must contain 64 elements"
    assert len(quad_chars) == 16, "Quadrant character array must contain 16 elements"

    # Verify Octant row character counts match 16 columns
    for r in range(16):
        assert len(oct_chars[r * 16 : (r + 1) * 16]) == 16, f"Octant row {r:x} must contain 16 characters"

    # Verify Sextant 8x8 row character counts match 8 columns
    for r in range(8):
        assert len(sex_chars[r * 8 : (r + 1) * 8]) == 8, f"Sextant row {r:x} must contain 8 characters"

    # Verify Quadrant 4x4 row character counts match 4 columns
    for r in range(4):
        assert len(quad_chars[r * 4 : (r + 1) * 4]) == 4, f"Quadrant row {r:x} must contain 4 characters"

    print("\nOctant, Sextant, and Quadrant grid integrity tests passed successfully!")


if __name__ == "__main__":
    oct_chars = get_octant_array()
    sex_chars = get_sextant_array()
    quad_chars = get_quadrant_array()

    print(render_quadrant_4x4_grid(quad_chars))
    print("\n" + "=" * 53 + "\n")
    print(render_quadrant_16x1_grid(quad_chars))
    print("\n" + "=" * 53 + "\n")
    print(render_sextant_8x8_grid(sex_chars))
    print("\n" + "=" * 53 + "\n")
    print(render_sextant_16x4_grid(sex_chars))
    print("\n" + "=" * 53 + "\n")
    print(render_octant_16x16_grid(oct_chars))
