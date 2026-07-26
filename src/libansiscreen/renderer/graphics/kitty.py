import base64
import io
from typing import Any


def encode_kitty(
    image: Any,
    width_cells: int = 1,
    height_cells: int = 1,
) -> str:
    """
    Generates Kitty Terminal Graphics Protocol escape sequence for an image.
    Escape format: \\x1b_Ga=T,f=32,s=W,v=H,c=COLS,r=ROWS,m=1;BASE64\\x1b\\\\
    """
    if hasattr(image, "convert"):
        img = image.convert("RGBA")
        img_w, img_h = img.size
        raw_bytes = img.tobytes()
    elif isinstance(image, dict) and "data" in image:
        raw_bytes = image["data"]
        img_w = image.get("width", 100)
        img_h = image.get("height", 100)
    else:
        buf = io.BytesIO()
        if hasattr(image, "save"):
            image.save(buf, format="PNG")
            raw_bytes = buf.getvalue()
            img_w = getattr(image, "width", 100)
            img_h = getattr(image, "height", 100)
        else:
            return ""

    b64_data = base64.b64encode(raw_bytes).decode("ascii")
    chunk_size = 4096
    chunks = [b64_data[i : i + chunk_size] for i in range(0, len(b64_data), chunk_size)]

    out = []
    for idx, chunk in enumerate(chunks):
        is_last = idx == len(chunks) - 1
        m = 0 if is_last else 1
        if idx == 0:
            header = f"a=T,f=32,s={img_w},v={img_h},c={width_cells},r={height_cells},m={m}"
        else:
            header = f"m={m}"
        out.append(f"\x1b_G{header};{chunk}\x1b\\")

    return "".join(out)
