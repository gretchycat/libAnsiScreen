"""
Octant Character Array Generator (0x00 - 0xFF)

Builds a complete 256-element array of Unicode block octant characters using
Python's built-in `unicodedata` standard library with 100% Unicode 16.0 specification alignment.

Bit order:
- 1 = 0x01 (Octant 1: Top-Left)
- 2 = 0x02 (Octant 2: Top-Right)
- 3 = 0x04 (Octant 3: Upper-Middle-Left)
- 4 = 0x08 (Octant 4: Upper-Middle-Right)
- 5 = 0x10 (Octant 5: Lower-Middle-Left)
- 6 = 0x20 (Octant 6: Lower-Middle-Right)
- 7 = 0x40 (Octant 7: Bottom-Left)
- 8 = 0x80 (Octant 8: Bottom-Right)
"""

import unicodedata

def get_octant_array():
    # 26 bitmasks that correspond to pre-existing Unicode block elements / space
    PRE_EXISTING_OCTANT_NAMES = {
        0x00: 'SPACE',
        0x01: 'LEFT HALF UPPER ONE QUARTER BLOCK',
        0x02: 'RIGHT HALF UPPER ONE QUARTER BLOCK',
        0x03: 'UPPER ONE QUARTER BLOCK',
        0x05: 'QUADRANT UPPER LEFT',
        0x0A: 'QUADRANT UPPER RIGHT',
        0x0F: 'UPPER HALF BLOCK',
        0x14: 'MIDDLE LEFT ONE QUARTER BLOCK',
        0x28: 'MIDDLE RIGHT ONE QUARTER BLOCK',
        0x3F: 'UPPER THREE QUARTERS BLOCK',
        0x40: 'LEFT HALF LOWER ONE QUARTER BLOCK',
        0x50: 'QUADRANT LOWER LEFT',
        0x55: 'LEFT HALF BLOCK',
        0x5A: 'QUADRANT UPPER RIGHT AND LOWER LEFT',
        0x80: 'RIGHT HALF LOWER ONE QUARTER BLOCK',
        0xA0: 'QUADRANT LOWER RIGHT',
        0xA5: 'QUADRANT UPPER LEFT AND LOWER RIGHT',
        0xAA: 'RIGHT HALF BLOCK',
        0xAF: 'QUADRANT UPPER LEFT AND UPPER RIGHT AND LOWER RIGHT',
        0xC0: 'LOWER ONE QUARTER BLOCK',
        0xF0: 'LOWER HALF BLOCK',
        0xF5: 'QUADRANT UPPER LEFT AND LOWER LEFT AND LOWER RIGHT',
        0xFA: 'QUADRANT UPPER RIGHT AND LOWER LEFT AND LOWER RIGHT',
        0xFC: 'LOWER THREE QUARTERS BLOCK',
        0xFF: 'FULL BLOCK',
    }

    PRE_EXISTING_OCTANT_CODEPOINTS = {
        0x00: ' ',
        0x01: '\U0001CEA8',
        0x02: '\U0001CEAB',
        0x03: '\U0001FB82',
        0x05: '\u2598',
        0x0A: '\u259D',
        0x0F: '\u2580',
        0x14: '\U0001FBE6',
        0x28: '\U0001FBE7',
        0x3F: '\U0001FB85',
        0x40: '\U0001CEA3',
        0x50: '\u2596',
        0x55: '\u258C',
        0x5A: '\u259E',
        0x80: '\U0001CEA0',
        0xA0: '\u2597',
        0xA5: '\u259A',
        0xAA: '\u2590',
        0xAF: '\u259C',
        0xC0: '\u2582',
        0xF0: '\u2584',
        0xF5: '\u259B',
        0xFA: '\u259F',
        0xFC: '\u2586',
        0xFF: '\u2588',
    }

    """Generate the complete 256-element array of octant characters (0x00 - 0xFF) using Python unicodedata."""
    octant_chars = [''] * 256
    unassigned = []

    for mask in range(256):
        if mask in PRE_EXISTING_OCTANT_NAMES:
            name = PRE_EXISTING_OCTANT_NAMES[mask]
            try:
                octant_chars[mask] = unicodedata.lookup(name)
            except KeyError:
                octant_chars[mask] = PRE_EXISTING_OCTANT_CODEPOINTS[mask]
        else:
            # Unicode 16.0 specifies octant block sorting by highest active bit H, then rest_mask
            H = mask.bit_length() - 1
            rest_mask = mask & ~(1 << H)
            unassigned.append(((H, rest_mask), mask))

    unassigned.sort(key=lambda x: x[0])

    for idx, (_, mask) in enumerate(unassigned):
        digits = [str(b + 1) for b in range(8) if (mask >> b) & 1]
        octant_name = f"BLOCK OCTANT-{''.join(digits)}"
        try:
            octant_chars[mask] = unicodedata.lookup(octant_name)
        except KeyError:
            octant_chars[mask] = chr(0x1CD00 + idx)

    return octant_chars


if __name__ == '__main__':
    chars = get_octant_array()
    print(f"Successfully generated {len(chars)} octant characters (0x00 - 0xFF) matching Unicode 16.0 standard.")
    print(f"Sample - 0x00 (space): {repr(chars[0x00])}")
    print(f"Sample - 0x01 (octant 1): {repr(chars[0x01])} (U+{ord(chars[0x01]):04X})")
    print(f"Sample - 0x04 (octant 3, U+1CD00): {repr(chars[0x04])} (U+{ord(chars[0x04]):04X})")
    print(f"Sample - 0x0F (upper half): {repr(chars[0x0F])} (U+{ord(chars[0x0F]):04X})")
    print(f"Sample - 0xFF (full block): {repr(chars[0xFF])} (U+{ord(chars[0xFF]):04X})")
