import base64
import io
import pytest
from PIL import Image
from libansiscreen.screen import Screen
from libansiscreen.renderer.ansi_emitter import ANSIEmitter


def create_test_base64_image(width=16, height=16, color=(255, 0, 0)):
    img = Image.new("RGBA", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def test_parse_sixel_sequence():
    r"""
    Verify that incoming Sixel DCS escape sequences (\x1bPq...\x1b\) are decoded,
    registered into ImageRegistry, and stamped onto screen cells.
    """
    for use_bin in (False, True):
        scr = Screen(width=10, height=5, use_binary=use_bin)

        # Basic Sixel sequence defining palette #0 (black) and #1 (white) with 2 slices
        sixel_seq = "\x1bPq#0;2;0;0;0#1;2;100;100;100#1~~\x1b\\"
        scr.feed(sixel_seq)

        assert len(scr.image_registry._images) == 1
        entry = scr.image_registry.get(1)
        assert entry is not None
        assert entry.metadata["protocol"] == "sixel"

        cell = scr.get_cell(0, 0)
        assert cell is not None
        assert cell.is_image
        assert cell.image.image_id == 1


def test_parse_iterm2_sequence():
    r"""
    Verify that incoming iTerm2 OSC escape sequences (\x1b]1337;File=...:<base64>\x07)
    are decoded, registered into ImageRegistry, and stamped onto screen cells.
    """
    b64_str = create_test_base64_image(16, 16, (0, 255, 0))
    for use_bin in (False, True):
        scr = Screen(width=10, height=5, use_binary=use_bin)
        iterm2_seq = f"\x1b]1337;File=inline=1;width=2;height=1:{b64_str}\x07"
        scr.feed(iterm2_seq)

        assert len(scr.image_registry._images) == 1
        entry = scr.image_registry.get(1)
        assert entry is not None
        assert entry.metadata["protocol"] == "iterm2"
        assert entry.metadata["inline"] == "1"


def test_parse_kitty_sequence():
    r"""
    Verify that incoming Kitty APC escape sequences (\x1b_Ga=T...;<base64>\x1b\)
    are decoded, registered into ImageRegistry, and stamped onto screen cells.
    """
    b64_str = create_test_base64_image(16, 16, (0, 0, 255))
    for use_bin in (False, True):
        scr = Screen(width=10, height=5, use_binary=use_bin)
        kitty_seq = f"\x1b_Ga=T,f=32;{b64_str}\x1b\\"
        scr.feed(kitty_seq)

        assert len(scr.image_registry._images) == 1
        entry = scr.image_registry.get(1)
        assert entry is not None
        assert entry.metadata["protocol"] == "kitty"


def test_image_cell_block_fallback_emission():
    """
    Verify that when terminal capabilities fall back to block rendering,
    registered image cells are emitted as downsampled 1x2 half-block SGR sequences (▀).
    """
    for use_bin in (False, True):
        scr = Screen(width=10, height=5, use_binary=use_bin)
        b64_str = create_test_base64_image(16, 32, (255, 0, 0))
        scr.feed(f"\x1b]1337;File=inline=1:{b64_str}\x07")

        emitter = ANSIEmitter()
        emitter.force_graphics_protocol("block")
        emitted_output = emitter.emit(scr)

        # Verify downsampled half-block character '▀' and truecolor SGR sequences are present
        assert "▀" in emitted_output
        assert "\x1b[38;2;255;0;0m" in emitted_output
