"""
Sextant Character Array Generator (0x00 - 0x3F)

Builds a complete 64-element array of Unicode block sextant characters using
Python's built-in `unicodedata` standard library.

Bit order:
- 1 = 0x01 (Subpixel 1: Top-Left)
- 2 = 0x02 (Subpixel 2: Top-Right)
- 3 = 0x04 (Subpixel 3: Middle-Left)
- 4 = 0x08 (Subpixel 4: Middle-Right)
- 5 = 0x10 (Subpixel 5: Bottom-Left)
- 6 = 0x20 (Subpixel 6: Bottom-Right)
"""

import unicodedata

def get_sextant_array():
    # 4 bitmasks overlapping with pre-existing Unicode block elements
    PRE_EXISTING_SEXTANT_NAMES = {
        0x00: 'SPACE',
        0x15: 'LEFT HALF BLOCK',
        0x2A: 'RIGHT HALF BLOCK',
        0x3F: 'FULL BLOCK',
    }

    PRE_EXISTING_SEXTANT_FALLBACKS = {
        0x00: ' ',
        0x15: '\u258C',
        0x2A: '\u2590',
        0x3F: '\u2588',
    }

    """Generate the complete 64-element array of sextant characters (0x00 - 0x3F) using Python unicodedata."""
    sextant_chars = [''] * 64

    for mask in range(64):
        if mask in PRE_EXISTING_SEXTANT_NAMES:
            name = PRE_EXISTING_SEXTANT_NAMES[mask]
            try:
                sextant_chars[mask] = unicodedata.lookup(name)
            except KeyError:
                sextant_chars[mask] = PRE_EXISTING_SEXTANT_FALLBACKS[mask]
        else:
            digits = [str(b + 1) for b in range(6) if (mask >> b) & 1]
            name = f"BLOCK SEXTANT-{''.join(digits)}"
            try:
                sextant_chars[mask] = unicodedata.lookup(name)
            except KeyError:
                # Direct codepoint offset U+1FB00 mapping
                sextant_chars[mask] = chr(0x1FB00 + mask - 1)

    return sextant_chars


if __name__ == '__main__':
    chars = get_sextant_array()
    print(f"Successfully generated {len(chars)} sextant characters (0x00 - 0x3F) using built-in unicodedata.")
    print(f"Sample - 0x00 (space): {repr(chars[0x00])}")
    print(f"Sample - 0x01 (sextant 1): {repr(chars[0x01])} (U+{ord(chars[0x01]):04X})")
    print(f"Sample - 0x15 (left half): {repr(chars[0x15])} (U+{ord(chars[0x15]):04X})")
    print(f"Sample - 0x3F (full block): {repr(chars[0x3F])} (U+{ord(chars[0x3F]):04X})")
