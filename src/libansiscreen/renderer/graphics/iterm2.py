import base64
import io
from typing import Any


def encode_iterm2(
    image: Any,
    width_cells: int = 1,
    height_cells: int = 1,
) -> str:
    """
    Generates iTerm2 / WezTerm Inline Image Protocol escape sequence.
    Format: \\x1b]1337;File=inline=1;width={width_cells};height={height_cells}:{base64_data}\\x07
    """
    buf = io.BytesIO()
    if hasattr(image, "save"):
        image.save(buf, format="PNG")
        png_bytes = buf.getvalue()
    elif isinstance(image, bytes):
        png_bytes = image
    elif isinstance(image, dict) and "data" in image:
        png_bytes = image["data"]
    else:
        return ""

    b64_data = base64.b64encode(png_bytes).decode("ascii")
    header = f"inline=1;width={width_cells};height={height_cells};size={len(png_bytes)}"
    return f"\x1b]1337;File={header}:{b64_data}\x07"
