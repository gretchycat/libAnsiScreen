I've added raw mode to the frame buffer put text/put_char methods in the frame buffer class.
binary mode paste is a lot slower than it needs to be.
object mode paste is actually faster.
so binary mode paste needs to be significantly faster.
5: COMPLETED: ANSIParser now handles incoming Sixel (DCS), iTerm2 (OSC 1337), and Kitty (APC G) image sequences, registering images into ImageRegistry and stamping image cells onto the framebuffer.
6: COMPLETED: ANSI Music hooks added to frameBuffer (music_queue, add_music, pop_music_queue, clear_music_queue) and ANSIParser state machine.
7: ANSI Music escape sequences (ESC [ M, ESC [ N, ESC M, ESC N) and direct API commands are automatically queued for library extensions to consume.
8:
9: octant, sextan/quadrant rendering and unit tests updated for all subpixel modes.
10: FIXED: octant flood fill mapping collision bug resolved (all 256 octant bitmasks are 100% unique), and subpixel flood fill max_y bound calculation updated per mode.
