import base64
import io
from typing import Any, Dict, Optional, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None


def parse_iterm2_data(data_str: str) -> Tuple[Optional[Any], Dict[str, Any]]:
    """
    Parses an iTerm2 inline image sequence parameter and base64 payload.
    Sequence format: 1337;File=name=...;inline=1;width=...;height=...:<base64>
    """
    metadata: Dict[str, Any] = {"protocol": "iterm2"}
    if ":" not in data_str:
        return None, metadata

    header, base64_payload = data_str.split(":", 1)
    # Extract params after File=
    if "File=" in header:
        _, params_part = header.split("File=", 1)
        for kv in params_part.split(";"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                metadata[k.strip()] = v.strip()

    if not base64_payload.strip():
        return None, metadata

    try:
        raw_bytes = base64.b64decode(base64_payload.strip())
        if Image is not None:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
            return img, metadata
        return raw_bytes, metadata
    except Exception:
        return None, metadata


def parse_kitty_data(control_str: str, base64_payload: str) -> Tuple[Optional[Any], Dict[str, Any]]:
    """
    Parses a Kitty graphics APC escape sequence control parameters and base64 payload.
    Format: _G<control_str>;<base64_payload>
    """
    metadata: Dict[str, Any] = {"protocol": "kitty"}
    if control_str:
        for item in control_str.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                metadata[k.strip()] = v.strip()

    if not base64_payload.strip():
        return None, metadata

    try:
        raw_bytes = base64.b64decode(base64_payload.strip())
        if Image is not None:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
            return img, metadata
        return raw_bytes, metadata
    except Exception:
        return None, metadata


def parse_sixel_data(sixel_str: str) -> Tuple[Optional[Any], Dict[str, Any]]:
    """
    Parses a Sixel DCS escape sequence payload into a PIL RGBA Image.
    Format: P1;P2;P3;q<sixel_pixels>
    """
    metadata: Dict[str, Any] = {"protocol": "sixel"}
    if "q" in sixel_str:
        _, pixel_data = sixel_str.split("q", 1)
    else:
        pixel_data = sixel_str

    if Image is None:
        return None, metadata

    palette: Dict[int, Tuple[int, int, int]] = {}
    current_color = 0
    x = 0
    y = 0
    max_x = 0
    max_y = 0

    pixels_dict: Dict[Tuple[int, int], Tuple[int, int, int]] = {}

    idx = 0
    n = len(pixel_data)
    while idx < n:
        ch = pixel_data[idx]

        if ch == "#":
            # Color definition (#N;format;r;g;b) or selection (#N)
            idx += 1
            param_str = ""
            while idx < n and (pixel_data[idx].isdigit() or pixel_data[idx] == ";"):
                param_str += pixel_data[idx]
                idx += 1
            if param_str:
                parts = [int(p) for p in param_str.split(";") if p]
                if len(parts) >= 1:
                    current_color = parts[0]
                if len(parts) >= 5 and parts[1] == 2:
                    r = int(parts[2] * 2.55)
                    g = int(parts[3] * 2.55)
                    b = int(parts[4] * 2.55)
                    palette[current_color] = (min(255, r), min(255, g), min(255, b))
            continue

        elif ch == "$":
            # Carriage return (return x to 0 for current 6-pixel band)
            x = 0
            idx += 1
            continue

        elif ch == "-":
            # Line feed (advance y by 6, return x to 0)
            x = 0
            y += 6
            idx += 1
            continue

        elif ch == "!":
            # Repeat count: !N<sixel_char>
            idx += 1
            rep_str = ""
            while idx < n and pixel_data[idx].isdigit():
                rep_str += pixel_data[idx]
                idx += 1
            repeat_count = int(rep_str) if rep_str else 1
            if idx < n:
                sixel_val = ord(pixel_data[idx]) - 63
                idx += 1
                if 0 <= sixel_val <= 63:
                    col_rgb = palette.get(current_color, (255, 255, 255))
                    for _ in range(repeat_count):
                        for bit in range(6):
                            if (sixel_val >> bit) & 1:
                                px = x
                                py = y + bit
                                pixels_dict[(px, py)] = col_rgb
                                if px > max_x:
                                    max_x = px
                                if py > max_y:
                                    max_y = py
                        x += 1
            continue

        elif 63 <= ord(ch) <= 126:
            # Single sixel slice byte (ASCII 63 to 126)
            sixel_val = ord(ch) - 63
            idx += 1
            if 0 <= sixel_val <= 63:
                col_rgb = palette.get(current_color, (255, 255, 255))
                for bit in range(6):
                    if (sixel_val >> bit) & 1:
                        px = x
                        py = y + bit
                        pixels_dict[(px, py)] = col_rgb
                        if px > max_x:
                            max_x = px
                        if py > max_y:
                            max_y = py
                x += 1
            continue

        idx += 1

    img_w = max(1, max_x + 1)
    img_h = max(1, max_y + 1)
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    px_data = img.load()
    for (px, py), rgb in pixels_dict.items():
        if 0 <= px < img_w and 0 <= py < img_h:
            px_data[px, py] = (rgb[0], rgb[1], rgb[2], 255)

    return img, metadata
