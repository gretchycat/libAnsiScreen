I've added raw mode to the frame buffer put text/put_char methods in the frame buffer class.
binary mode paste is a lot slower than it needs to be.
object mode paste is actually faster.
so binary mode paste needs to be significantly faster. 
the ansi parser should be able to handle sixel, iterm2, kitty codes.
we should also put hooks in for ansi music.
just putting all the music instructions into a queue should be enough.
an extension to this Library will handle parsing out that queue.
9: octant, sextan/quadrant rendering and unit tests updated for all subpixel modes.
10: FIXED: octant flood fill mapping collision bug resolved (all 256 octant bitmasks are 100% unique), and subpixel flood fill max_y bound calculation updated per mode.
