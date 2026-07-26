import pytest
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color
from libansiscreen.renderer.ansi_emitter import ANSIEmitter, Box
from libansiscreen.color.palette import (
    create_ansi_16_palette,
    create_ansi_256_palette,
)
from tests.helpers import save_output


def test_emitter_basic_rendering():
    screen = Screen(width=20)
    screen.set_foreground(Color(255, 0, 0))
    screen.put_text("Emitter Test")

    emitter = ANSIEmitter()
    ansi_str = emitter.emit(screen)
    assert isinstance(ansi_str, str)
    assert "\x1b[" in ansi_str

    save_output(screen, "emitter_basic.ans", emitter=emitter)


def test_emitter_full_row_height_coverage():
    screen = Screen(width=10, height=5)
    screen.put_text("0\n1\n2\n3\n4")

    emitter = ANSIEmitter()
    ansi_str = emitter.emit(screen)
    lines = ansi_str.split("\n")

    assert len(lines) == 5
    assert "0" in lines[0]
    assert "4" in lines[4]


def test_emitter_output_modes_and_palettes():
    screen = Screen(width=40)
    screen.set_foreground(Color(200, 100, 50))
    screen.set_background(Color(10, 20, 30))
    screen.put_text("Palette and DOS Mode Tests")

    # Truecolor / Modern
    em_modern = ANSIEmitter()
    save_output(screen, "emitter_out_mode.modern.ans", emitter=em_modern)

    # ANSI 256
    em_256 = ANSIEmitter(palette=create_ansi_256_palette())
    save_output(screen, "emitter_out_mode.ansi256.ans", emitter=em_256)

    # ANSI 16
    em_16 = ANSIEmitter(palette=create_ansi_16_palette())
    save_output(screen, "emitter_out_mode.ansi16.ans", emitter=em_16)

    # DOS Mode
    em_dos = ANSIEmitter(dos_mode=True)
    save_output(screen, "emitter_out_mode.dos.ans", emitter=em_dos)

    # DOS + ICE Mode
    em_ice = ANSIEmitter(dos_mode=True, ice_mode=True)
    save_output(screen, "emitter_out_mode.dos_ice.ans", emitter=em_ice)


def test_emitter_dos_ice_and_cp437_codepage():
    screen = Screen(width=20)
    screen.put_text("┌─┐\n│█│\n└─┘")

    # 1. DOS + ICE mode
    em_dos_ice = ANSIEmitter(dos_mode=True, ice_mode=True)
    assert em_dos_ice.dos_mode is True
    assert em_dos_ice.ice_mode is True

    # 2. CP437 codepage bytes encoding
    em_cp437 = ANSIEmitter(dos_mode=True, encoding="cp437")
    cp437_bytes = em_cp437.emit(screen, return_bytes=True)

    assert isinstance(cp437_bytes, bytes)
    assert b"\xda" in cp437_bytes  # CP437 byte for '┌'
    assert b"\xc4" in cp437_bytes  # CP437 byte for '─'
    assert b"\xbf" in cp437_bytes  # CP437 byte for '┐'


def test_emitter_automatic_color_depth_capability_quantization():
    screen = Screen(width=10)
    screen.set_foreground(Color(123, 45, 67))
    screen.put_text("X")

    emitter = ANSIEmitter()

    # 1. Force ANSI16 mode
    emitter.force_color_depth("ansi16")
    res_16 = emitter.emit(screen)
    assert "\x1b[38;2;" not in res_16  # No truecolor sequence

    # 2. Force ANSI256 mode
    emitter.force_color_depth("ansi256")
    res_256 = emitter.emit(screen)
    assert "\x1b[38;2;" not in res_256  # No truecolor sequence


def test_emitter_box_subregion_and_raw():
    screen = Screen(width=20, height=10)
    screen.put_text("Line 0\nLine 1\nLine 2\nLine 3")

    sub_box = Box(x=0, y=0, width=10, height=2)
    emitter = ANSIEmitter()

    ansi_sub = emitter.emit(screen, box=sub_box, raw=True)
    assert isinstance(ansi_sub, str)

    out_path = save_output(screen, "emitter_subregion.ans")
    assert out_path.exists()


def test_box_dataclass():
    b = Box(x=5, y=5, width=10, height=10)
    assert b.contains(5, 5)
    assert b.contains(14, 14)
    assert not b.contains(4, 5)
    assert not b.contains(15, 15)
