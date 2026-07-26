import io
from typing import Any


def encode_sixel(
    image: Any,
    width_cells: int = 1,
    height_cells: int = 1,
) -> str:
    """
    Generates Sixel Raster Graphics escape sequence for an image.
    Format: \\x1bPq#0;2;R;G;B...\\x1b\\\\
    """
    if not hasattr(image, "convert"):
        return ""

    target_w = max(8, width_cells * 8)
    target_h = max(16, height_cells * 16)
    img = image.resize((target_w, target_h)).convert("RGB")

    quantized = img.quantize(colors=256)
    palette = quantized.getpalette() or []
    w, h = quantized.size

    out = ["\x1bPq"]

    # Output Palette Definitions
    num_colors = min(256, len(palette) // 3)
    for idx in range(num_colors):
        r = int(palette[idx * 3] * 100 / 255)
        g = int(palette[idx * 3 + 1] * 100 / 255)
        b = int(palette[idx * 3 + 2] * 100 / 255)
        out.append(f"#{idx};2;{r};{g};{b}")

    # Output Sixel Bands (6 vertical pixels per row)
    pixels = quantized.load()
    for y6 in range(0, h, 6):
        for color_idx in range(num_colors):
            row_sixels = []
            active = False
            for x in range(w):
                bitmask = 0
                for bit in range(6):
                    py = y6 + bit
                    if py < h and pixels[x, py] == color_idx:
                        bitmask |= 1 << bit
                        active = True
                row_sixels.append(chr(63 + bitmask))

            if active:
                out.append(f"#{color_idx}")
                curr_ch = None
                count = 0
                for ch in row_sixels:
                    if ch == curr_ch:
                        count += 1
                    else:
                        if curr_ch is not None:
                            if count > 3:
                                out.append(f"!{count}{curr_ch}")
                            else:
                                out.append(curr_ch * count)
                        curr_ch = ch
                        count = 1
                if curr_ch is not None:
                    if count > 3:
                        out.append(f"!{count}{curr_ch}")
                    else:
                        out.append(curr_ch * count)
                out.append("$")
        out.append("-")

    out.append("\x1b\\")
    return "".join(out)
