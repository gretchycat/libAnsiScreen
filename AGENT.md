I've added raw mode to the frame buffer put text/put_char methods in the frame buffer class.
binary mode paste is a lot slower than it needs to be.
object mode paste is actually faster.
so binary mode paste needs to be significantly faster. 
the ansi parser should be able to handle sixel, iterm2, kitty codes.
we should also put hooks in for ansi music.
just putting all the music instructions into a queue should be enough.
an extension to this Library will handle parsing out that queue.
octant, sextan/quadrant rendering is working mostly okay right now.we should add some more special cases to the unit tests.
I said mostly okay because for some reason, octane flood fill does not stay Within bounds

