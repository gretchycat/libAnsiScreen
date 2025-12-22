from __future__ import annotations

from typing import Iterable, List, Tuple

RGB = Tuple[int, int, int]

# ============================================================
# ANSI 16 COLOR DEFINITIONS
# ============================================================

# Base colors (0–7):
# 0 black (k)
# 1 red
# 2 green
# 3 yellow
# 4 blue
# 5 magenta
# 6 cyan
# 7 white

ANSI16_RING = [1, 3, 2, 6, 4, 5]  # r y g c b m
ANSI16_GRAY = [0, 7]             # k w

ANSI16_SYMBOLS = {
    'k': 0, 'r': 1, 'g': 2, 'y': 3,
    'b': 4, 'm': 5, 'c': 6, 'w': 7,
}


def symbol_to_ansi16(ch: str) -> int:
    base = ANSI16_SYMBOLS[ch.lower()]
    return base + 8 if ch.isupper() else base


def is_bright(c: int) -> bool:
    return c >= 8


def base(c: int) -> int:
    return c & 7


def apply_brightness(c: int, bright: bool) -> int:
    return c + 8 if bright else c


# ============================================================
# 4-BIT HUE EXPANSION
# ============================================================

def _traverse_hue_16(a: int, b: int) -> List[int]:
    ai = ANSI16_RING.index(a)
    bi = ANSI16_RING.index(b)

    diff = (bi - ai) % len(ANSI16_RING)
    step = 1

    if diff > len(ANSI16_RING) // 2:
        diff = len(ANSI16_RING) - diff
        step = -1

    seq = [a]
    cur = ai
    for _ in range(diff):
        cur = (cur + step) % len(ANSI16_RING)
        seq.append(ANSI16_RING[cur])

    return seq


def expand_ansi16_pair(a: int, b: int) -> List[int]:
    """
    Expand a single ANSI16 color transition into intermediate steps.
    Brightness changes are applied only at the final step.
    """
    ba, bb = is_bright(a), is_bright(b)
    sa, sb = base(a), base(b)

    # hue → hue
    if sa in ANSI16_RING and sb in ANSI16_RING:
        path = _traverse_hue_16(sa, sb)

    # gray → gray
    elif sa in ANSI16_GRAY and sb in ANSI16_GRAY:
        path = [sa] if sa == sb else [sa, sb]

    # gray → hue
    elif sa in ANSI16_GRAY and sb in ANSI16_RING:
        anchor = 3 if sa == 7 else 1  # w→y, k→r
        tail = _traverse_hue_16(anchor, sb)
        path = [sa, anchor] + tail[1:]

    # hue → gray
    elif sa in ANSI16_RING and sb in ANSI16_GRAY:
        anchor = 3 if sb == 7 else 5  # →y or →m
        head = _traverse_hue_16(sa, anchor)
        path = head + [sb]

    else:
        path = [sa, sb]

    # Apply brightness only at the end
    out = [apply_brightness(p, ba) for p in path]
    if ba != bb:
        final = apply_brightness(path[-1], bb)
        if out[-1] != final:
            out.append(final)

    return out


def expand_ansi16(seq: Iterable[int]) -> List[int]:
    """
    Expand a sequence of ANSI16 colors into intermediate hue steps.
    """
    seq = list(seq)
    if len(seq) < 2:
        return seq[:]

    out: List[int] = []
    for i in range(len(seq) - 1):
        part = expand_ansi16_pair(seq[i], seq[i + 1])
        if out and part and out[-1] == part[0]:
            part = part[1:]
        out.extend(part)

    return out


# ============================================================
# PALETTE → RGB CONVERSION
# ============================================================

def ansi16_to_rgb(index: int, palette) -> RGB:
    c = palette[index]
    return (c.r, c.g, c.b)


def ansi256_to_rgb(index: int, palette) -> RGB:
    c = palette[index]
    return (c.r, c.g, c.b)


# ============================================================
# RGB INTERPOLATION
# ============================================================

def _lerp_rgb(a: RGB, b: RGB, t: float) -> RGB:
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


def fill_gradient(
    stops: List[RGB],
    steps: int = 16,
) -> List[RGB]:
    """
    Interpolate RGB stops to a fixed number of steps.
    """
    if steps <= 0 or not stops:
        return []

    if len(stops) == 1:
        return [stops[0]] * steps

    segments = len(stops) - 1
    out: List[RGB] = []

    for i in range(steps):
        t = i / (steps - 1)
        seg = min(int(t * segments), segments - 1)
        local_t = (t - seg / segments) * segments
        out.append(_lerp_rgb(stops[seg], stops[seg + 1], local_t))

    return out


# ============================================================
# INGREDIENT FUNCTION (PUBLIC ENTRY POINT)
# ============================================================

def gradient_colors(
    seeds,
    *,
    steps: int = 16,
    palette16=None,
    palette256=None,
) -> List[RGB]:
    """
    Normalize gradient seeds, expand if needed, and return RGB gradient list.

    seeds may be:
      - ANSI16 symbolic string: "rGyW"
      - list of ANSI16 / ANSI256 indices
      - list of RGB tuples
      - mixed list of the above

    palettes are required for index-based inputs.
    """

    if steps <= 0:
        return []

    rgb_stops: List[RGB] = []

    # ANSI16 symbolic string
    if isinstance(seeds, str):
        if palette16 is None:
            raise ValueError("palette16 required for ANSI16 symbolic gradients")

        ansi16_seq = [symbol_to_ansi16(ch) for ch in seeds]
        expanded = expand_ansi16(ansi16_seq)
        rgb_stops = [ansi16_to_rgb(i, palette16) for i in expanded]

    else:
        for s in seeds:
            # RGB tuple
            if isinstance(s, tuple) and len(s) == 3:
                rgb_stops.append(s)

            # ANSI index
            elif isinstance(s, int):
                if s < 16:
                    if palette16 is None:
                        raise ValueError("palette16 required for ANSI16 indices")
                    rgb_stops.append(ansi16_to_rgb(s, palette16))
                else:
                    if palette256 is None:
                        raise ValueError("palette256 required for ANSI256 indices")
                    rgb_stops.append(ansi256_to_rgb(s, palette256))

            # ANSI16 symbol
            elif isinstance(s, str) and len(s) == 1:
                if palette16 is None:
                    raise ValueError("palette16 required for ANSI16 symbols")
                idx = symbol_to_ansi16(s)
                rgb_stops.append(ansi16_to_rgb(idx, palette16))

            else:
                raise TypeError(f"Unsupported gradient seed: {s!r}")

    return fill_gradient(rgb_stops, steps=steps)
