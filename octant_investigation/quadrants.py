"""
Quadrant Character Array Generator (0x0 - 0xF)

Builds a complete 16-element array of Unicode block quadrant characters using
Python's built-in `unicodedata` standard library.

Bit order:
- 1 = 0x1 (Subpixel 1: Top-Left)
- 2 = 0x2 (Subpixel 2: Top-Right)
- 3 = 0x4 (Subpixel 3: Bottom-Left)
- 4 = 0x8 (Subpixel 4: Bottom-Right)
"""

import unicodedata

# Official Unicode character names for 16 2x2 Quadrant combinations
QUADRANT_NAMES = {
    0x0: 'SPACE',
    0x1: 'QUADRANT UPPER LEFT',
    0x2: 'QUADRANT UPPER RIGHT',
    0x3: 'UPPER HALF BLOCK',
    0x4: 'QUADRANT LOWER LEFT',
    0x5: 'LEFT HALF BLOCK',
    0x6: 'QUADRANT UPPER RIGHT AND LOWER LEFT',
    0x7: 'QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER LEFT',
    0x8: 'QUADRANT LOWER RIGHT',
    0x9: 'QUADRANT UPPER LEFT AND LOWER RIGHT',
    0xA: 'RIGHT HALF BLOCK',
    0xB: 'QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT',
    0xC: 'LOWER HALF BLOCK',
    0xD: 'QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT',
    0xE: 'QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT',
    0xF: 'FULL BLOCK',
}

QUADRANT_FALLBACKS = {
    0x0: ' ',
    0x1: '\u2598',
    0x2: '\u259D',
    0x3: '\u2580',
    0x4: '\u2596',
    0x5: '\u258C',
    0x6: '\u259E',
    0x7: '\u259B',
    0x8: '\u2597',
    0x9: '\u259A',
    0xA: '\u2590',
    0xB: '\u259C',
    0xC: '\u2584',
    0xD: '\u2599',
    0xE: '\u259F',
    0xF: '\u2588',
}


def get_quadrant_array():
    """Generate the complete 16-element array of quadrant characters (0x0 - 0xF) using Python unicodedata."""
    quad_chars = [''] * 16
    for mask in range(16):
        name = QUADRANT_NAMES[mask]
        try:
            quad_chars[mask] = unicodedata.lookup(name)
        except KeyError:
            quad_chars[mask] = QUADRANT_FALLBACKS[mask]
    return quad_chars


if __name__ == '__main__':
    chars = get_quadrant_array()
    print(f"Successfully generated {len(chars)} quadrant characters (0x0 - 0xF) using built-in unicodedata.")
    print(f"Sample - 0x0 (space): {repr(chars[0x0])}")
    print(f"Sample - 0x1 (top-left): {repr(chars[0x1])} (U+{ord(chars[0x1]):04X})")
    print(f"Sample - 0x5 (left half): {repr(chars[0x5])} (U+{ord(chars[0x5]):04X})")
    print(f"Sample - 0xF (full block): {repr(chars[0xF])} (U+{ord(chars[0xF]):04X})")
