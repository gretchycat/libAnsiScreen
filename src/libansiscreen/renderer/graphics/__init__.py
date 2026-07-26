from typing import Any, Optional
from .kitty import encode_kitty
from .iterm2 import encode_iterm2
from .sixel import encode_sixel
from .block import encode_block

__all__ = [
    "encode_kitty",
    "encode_iterm2",
    "encode_sixel",
    "encode_block",
    "encode_image",
]


def encode_image(
    image: Any,
    protocol: str = "block",
    width_cells: int = 1,
    height_cells: int = 1,
) -> str:
    """
    Universal graphics generator dispatcher.
    Encodes a PIL Image or image object into the requested terminal graphics protocol format.
    Protocols: 'kitty', 'iterm2', 'sixel', 'block'
    """
    proto = protocol.lower()
    if proto == "kitty":
        return encode_kitty(image, width_cells=width_cells, height_cells=height_cells)
    elif proto == "iterm2":
        return encode_iterm2(image, width_cells=width_cells, height_cells=height_cells)
    elif proto == "sixel":
        return encode_sixel(image, width_cells=width_cells, height_cells=height_cells)
    else:
        return encode_block(image, width_cells=width_cells, height_cells=height_cells)
