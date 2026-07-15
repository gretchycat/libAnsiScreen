import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from libansiscreen.screen import Screen
from libansiscreen.renderer.ansi_emitter import ANSIEmitter
from libansiscreen.color.rgb import Color
from libansiscreen.parser.ansi_parser import ANSIParser

def test_emit_diff():
    s1 = Screen(width=20, height=5)
    s1.put_text("Hello World!")
    s1.put_text("\nThis is row 2")
    
    s2 = s1.copy()
    s2.cursor_goto(6, 0)
    s2.put_text("Earth") # "Hello Earth!"
    s2.cursor_goto(0, 2)
    s2.put_text("Row 3 added")
    
    emitter = ANSIEmitter()
    diff = emitter.emit_diff(s2, s1)
    
    print(f"Diff length: {len(diff)}")
    print(f"Diff: {repr(diff)}")
    
    # Verification: Applying diff to s1 should result in s2
    s_verify = s1.copy()
    parser = ANSIParser(s_verify)
    parser.feed(diff)
    
    # Compare s_verify and s2
    match = True
    for y in range(s2.height):
        for x in range(s2.width):
            c2 = s2.get_cell(x, y)
            cv = s_verify.get_cell(x, y)
            if c2 != cv:
                print(f"Mismatch at {x},{y}: expected {c2}, got {cv}")
                match = False
    
    if match:
        print("Verification successful!")
    return match

if __name__ == "__main__":
    if test_emit_diff():
        sys.exit(0)
    else:
        sys.exit(1)
