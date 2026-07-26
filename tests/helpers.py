from pathlib import Path
from libansiscreen.screen import Screen
from libansiscreen.renderer.ansi_emitter import ANSIEmitter

OUT_DIR = Path(__file__).parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save_output(screen: Screen, filename: str, emitter: ANSIEmitter = None) -> Path:
    """
    Renders the screen using ANSIEmitter and writes the resulting ANSI string
    to tests/out/<filename>. Returns the file path.
    """
    if emitter is None:
        emitter = ANSIEmitter()
    ansi_data = emitter.emit(screen)
    out_path = OUT_DIR / filename
    out_path.write_text(ansi_data, encoding="utf-8")
    return out_path
