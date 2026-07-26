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
