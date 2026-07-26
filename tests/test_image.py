import pytest
from libansiscreen.screen import Screen
from libansiscreen.image import ImageRegistry, ImageEntry
from libansiscreen.binary_cell import IMAGE_FLAG


def test_image_registry_standalone():
    registry = ImageRegistry()
    dummy_img = "DUMMY_IMAGE_DATA"

    img_id = registry.register(dummy_img, width_cells=5, height_cells=3, metadata={"format": "PNG"})
    assert img_id == 1

    entry = registry.get(img_id)
    assert entry is not None
    assert entry.image == dummy_img
    assert entry.width_cells == 5
    assert entry.height_cells == 3
    assert entry.metadata == {"format": "PNG"}

    assert registry.remove(img_id)
    assert registry.get(img_id) is None


def test_screen_put_image():
    screen = Screen(width=40, height=20)
    mock_image = {"name": "test_logo.png", "data": b"123456"}

    img_id = screen.put_image(x=5, y=2, image=mock_image, width_cells=4, height_cells=2)
    assert img_id == 1

    # Verify that cells in the region (x=5..8, y=2..3) carry the IMAGE_FLAG
    cell = screen.get_cell(5, 2)
    assert cell is not None
    
    # Retrieve raw binary cell parameters
    offset = screen._cell_offset(5, 2)
    from libansiscreen.binary_cell import CELL_STRUCT
    cp, fr, fg, fb, ff, br, bg, bb, bf, attrs, tile_info = CELL_STRUCT.unpack_from(screen.buffer, offset)

    assert (cp & IMAGE_FLAG) != 0
    assert (cp & ~IMAGE_FLAG) == img_id
    assert screen.image_registry.get(img_id).image == mock_image

    # High-level Cell property resolution
    assert cell.is_image is True
    assert isinstance(cell.image, ImageEntry)
    assert cell.image.image == mock_image


def test_image_emitter_placeholder():
    screen = Screen(width=10, height=2)
    mock_img = "SAMPLE_PIL_IMAGE"
    screen.put_image(x=2, y=0, image=mock_img, width_cells=3, height_cells=1)

    rendered = screen.emit()
    assert "🖼" in rendered


def test_put_cell_image_and_clip_operations():
    src = Screen(width=10, height=5)
    mock_pil_img = {"format": "PNG", "bytes": b"\x89PNG\r\n\x1a\n"}

    # 1. Direct put_cell with image kwarg
    src.put_cell(0, 0, image=mock_pil_img)
    cell = src.get_cell(0, 0)

    assert cell.is_image is True
    assert isinstance(cell.image, ImageEntry)
    assert cell.image.image == mock_pil_img

    # 2. Copy image region
    copied_fb = src.copy((0, 0, 5, 2))
    assert copied_fb.get_cell(0, 0).is_image is True

    # 3. Paste image region onto destination
    dst = Screen(width=20, height=10)
    dst.paste(copied_fb, box=(5, 5, 5, 2))

    dst_cell = dst.get_cell(5, 5)
    assert dst_cell.is_image is True
    assert isinstance(dst_cell.image, ImageEntry)
    assert dst_cell.image.image == mock_pil_img


def test_image_emitter_protocol_dispatch():
    from PIL import Image
    from libansiscreen.renderer.ansi_emitter import ANSIEmitter

    screen = Screen(width=10, height=5)
    img = Image.new("RGBA", (16, 16), color=(0, 255, 0, 255))
    screen.put_image(0, 0, image=img, width_cells=2, height_cells=2)

    emitter = ANSIEmitter()

    # Kitty Protocol
    emitter.force_graphics_protocol("kitty")
    out_kitty = emitter.emit(screen)
    assert "\x1b_G" in out_kitty
    assert "a=T" in out_kitty

    # Sixel Protocol
    emitter.force_graphics_protocol("sixel")
    out_sixel = emitter.emit(screen)
    assert "\x1bPq" in out_sixel
    assert "\x1b\\" in out_sixel

    # iTerm2 Protocol
    emitter.force_graphics_protocol("iterm2")
    out_iterm2 = emitter.emit(screen)
    assert "\x1b]1337;File=" in out_iterm2

    # Block / Fallback Protocol
    emitter.force_graphics_protocol("block")
    out_block = emitter.emit(screen)
    assert "🖼" in out_block
