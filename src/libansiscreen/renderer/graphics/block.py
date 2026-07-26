from typing import Any


def encode_block(
    image: Any,
    width_cells: int = 1,
    height_cells: int = 1,
) -> str:
    """
    Generates Unicode Half-Block (▀) fallback ANSI string for an image.
    Uses 1x2 half-block sampling with truecolor foreground and background SGR.
    """
    if not hasattr(image, "resize"):
        return "🖼" * width_cells

    img_w = max(1, width_cells)
    img_h = max(1, height_cells * 2)
    img = image.resize((img_w, img_h)).convert("RGB")
    pixels = img.load()

    rows = []
    for y_cell in range(height_cells):
        row_str = []
        top_y = y_cell * 2
        bot_y = top_y + 1

        for x in range(width_cells):
            tr, tg, tb = pixels[x, top_y]
            if bot_y < img_h:
                br, bg, bb = pixels[x, bot_y]
            else:
                br, bg, bb = tr, tg, tb

            row_str.append(f"\x1b[38;2;{tr};{tg};{tb}m\x1b[48;2;{br};{bg};{bb}m▀")

        row_str.append("\x1b[0m")
        rows.append("".join(row_str))

    return "\n".join(rows)
