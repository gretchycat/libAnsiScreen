import struct
from typing import Optional
from .cell import Cell
from .color.rgb import Color
from .image import ImageEntry

CELL_SIZE = 16

# Layout (16 bytes total):
# uint32 codepoint_or_imgid (4 bytes)
# uint8  fg_r, fg_g, fg_b, fg_flags (4 bytes)
# uint8  bg_r, bg_g, bg_b, bg_flags (4 bytes)
# uint16 attrs (2 bytes)
# uint16 tile_info / flags (2 bytes)
CELL_STRUCT = struct.Struct("<I BBB B BBB B H H")

# Flags
FLAG_COLOR_SET   = 0x01
FLAG_CELL_NULL   = 0x8000  # Cell is explicitly None
IMAGE_FLAG       = 0x80000000
CODEPOINT_MASK   = 0x7FFFFFFF


def pack_cell_fields(
    buffer: bytearray,
    offset: int,
    codepoint_or_imgid: int = 0,
    fg_r: int = 0,
    fg_g: int = 0,
    fg_b: int = 0,
    fg_set: bool = False,
    bg_r: int = 0,
    bg_g: int = 0,
    bg_b: int = 0,
    bg_set: bool = False,
    attrs: int = 0,
    tile_info: int = 0,
) -> None:
    """
    Packs raw cell parameters directly into buffer at specified byte offset.
    """
    fg_flags = FLAG_COLOR_SET if fg_set else 0
    bg_flags = FLAG_COLOR_SET if bg_set else 0

    CELL_STRUCT.pack_into(
        buffer,
        offset,
        codepoint_or_imgid,
        fg_r,
        fg_g,
        fg_b,
        fg_flags,
        bg_r,
        bg_g,
        bg_b,
        bg_flags,
        attrs,
        tile_info,
    )


def pack_cell(buffer: bytearray, offset: int, cell: Optional[Cell]) -> None:
    """
    Packs a Python Cell object into buffer at specified byte offset.
    If cell is None, marks cell with FLAG_CELL_NULL.
    """
    if cell is None:
        CELL_STRUCT.pack_into(buffer, offset, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, FLAG_CELL_NULL)
        return

    # Determine character codepoint or image id
    codepoint = 0
    if cell.image is not None:
        if isinstance(cell.image, ImageEntry):
            codepoint = IMAGE_FLAG | cell.image.image_id
        elif isinstance(cell.image, int):
            codepoint = IMAGE_FLAG | cell.image
    elif isinstance(cell.char, ImageEntry):
        codepoint = IMAGE_FLAG | cell.char.image_id
    elif isinstance(cell.char, str) and len(cell.char) > 0:
        codepoint = ord(cell.char[0])

    fg_r, fg_g, fg_b, fg_set = 0, 0, 0, False
    if cell.fg is not None:
        fg_r, fg_g, fg_b, fg_set = cell.fg.r, cell.fg.g, cell.fg.b, True

    bg_r, bg_g, bg_b, bg_set = 0, 0, 0, False
    if cell.bg is not None:
        bg_r, bg_g, bg_b, bg_set = cell.bg.r, cell.bg.g, cell.bg.b, True

    tile_info = ((cell.tile_y & 0x7F) << 8) | (cell.tile_x & 0xFF)
    pack_cell_fields(
        buffer,
        offset,
        codepoint_or_imgid=codepoint,
        fg_r=fg_r,
        fg_g=fg_g,
        fg_b=fg_b,
        fg_set=fg_set,
        bg_r=bg_r,
        bg_g=bg_g,
        bg_b=bg_b,
        bg_set=bg_set,
        attrs=cell.attrs,
        tile_info=tile_info,
    )


def unpack_cell(buffer: bytearray, offset: int) -> Optional[Cell]:
    """
    Unpacks a 16-byte cell from buffer at offset into a Python Cell instance.
    Returns None if cell is explicitly marked None.
    """
    (
        cp,
        fr,
        fg,
        fb,
        ff,
        br,
        bg,
        bb,
        bf,
        attrs,
        tile_info,
    ) = CELL_STRUCT.unpack_from(buffer, offset)

    if tile_info == FLAG_CELL_NULL:
        return None

    char = None
    image_id = None
    if cp != 0:
        if cp & IMAGE_FLAG:
            image_id = cp & CODEPOINT_MASK
        else:
            char = chr(cp)

    fg_color = Color(fr, fg, fb) if (ff & FLAG_COLOR_SET) else None
    bg_color = Color(br, bg, bb) if (bf & FLAG_COLOR_SET) else None

    tile_x = tile_info & 0xFF
    tile_y = (tile_info >> 8) & 0x7F

    return Cell(
        char=char,
        fg=fg_color,
        bg=bg_color,
        attrs=attrs,
        image=image_id,
        tile_x=tile_x,
        tile_y=tile_y,
    )
