import pytest
from PIL import Image
from libansiscreen.renderer.graphics import (
    encode_kitty,
    encode_iterm2,
    encode_sixel,
    encode_block,
    encode_image,
)


def create_sample_image():
    img = Image.new("RGBA", (16, 16), color=(255, 0, 0, 255))
    return img


def test_kitty_graphics_generator():
    img = create_sample_image()
    kitty_out = encode_kitty(img, width_cells=2, height_cells=1)

    assert "\x1b_G" in kitty_out
    assert "a=T" in kitty_out
    assert "f=32" in kitty_out
    assert "\x1b\\" in kitty_out


def test_iterm2_graphics_generator():
    img = create_sample_image()
    iterm2_out = encode_iterm2(img, width_cells=4, height_cells=2)

    assert "\x1b]1337;File=" in iterm2_out
    assert "inline=1" in iterm2_out
    assert "width=4" in iterm2_out
    assert "\x07" in iterm2_out


def test_sixel_graphics_generator():
    img = create_sample_image()
    sixel_out = encode_sixel(img, width_cells=2, height_cells=2)

    assert sixel_out.startswith("\x1bPq")
    assert sixel_out.endswith("\x1b\\")
    assert "#0;2;" in sixel_out  # Palette definition


def test_block_graphics_generator():
    img = create_sample_image()
    block_out = encode_block(img, width_cells=3, height_cells=1)

    assert "▀" in block_out
    assert "\x1b[38;2;" in block_out
    assert "\x1b[48;2;" in block_out


def test_universal_encode_image_dispatcher():
    img = create_sample_image()

    assert "\x1b_G" in encode_image(img, protocol="kitty")
    assert "\x1b]1337" in encode_image(img, protocol="iterm2")
    assert "\x1bPq" in encode_image(img, protocol="sixel")
    assert "▀" in encode_image(img, protocol="block")
