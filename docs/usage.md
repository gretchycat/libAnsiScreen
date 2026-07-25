# Library Usage: libAnsiScreen

This guide provides tested, runnable code recipes for common tasks using `libAnsiScreen`.

---

## 1. Basic Setup and Rendering
Create a screen buffer, set graphics attributes, write text, and emit ANSI sequences.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# Create a screen buffer with a fixed width of 20 columns
screen = Screen(width=20)

# Set initial graphics state (SGR)
screen.set_foreground(Color(255, 0, 0))  # Bright Red
screen.set_background(Color(0, 0, 50))   # Dark Blue

# Write text into the screen buffer
screen.put_text("Hello, ANSI!")

# Render to ANSI escape sequence string and print
print(screen.emit())
```

---

## 2. Half-Block Pixel Graphics
Use half-block mode (`▀`, `▄`, `█`) to draw color graphics at 1x2 subpixel resolution (vertical coordinate `y` is in half-character units).

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

screen = Screen(width=40)
red = Color(255, 0, 0)
blue = Color(0, 0, 255)

# Draw intersecting lines using half-block pixel plotting
for i in range(20):
    screen.pixel_plot(i, i, red)
    screen.pixel_plot(39 - i, i, blue)

print(screen.emit())
```

---

## 3. Applying Gradients
Apply smooth RGB color gradients across text or character backgrounds using `colorize()`.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

screen = Screen(width=30)
screen.put_text("GRADIENT TEXT EXAMPLE\n" * 5)

# Define an RGB gradient progression
gradient = [
    Color(0, 0, 255),    # Blue
    Color(0, 255, 0),    # Green
    Color(0, 255, 255)   # Cyan
]

# Apply horizontal gradient to text foreground
screen.colorize(gradient, mode="hgrad", foreground=True)

print(screen.emit())
```

---

## 4. Parsing ANSI Data
Feed raw or ANSI-encoded streams into `Screen` to reconstruct or manipulate ANSI documents.

```python
from libansiscreen.screen import Screen

# Raw ANSI string containing color codes
ansi_data = "\x1b[31mRed Text\x1b[0m \x1b[32mGreen Text\x1b[0m"

screen = Screen(width=20)
screen.feed(ansi_data)

# Modify the parsed buffer directly (e.g. clearing first 3 cells)
for x in range(3):
    screen.put_cell(x, 0, char=' ', fg=None, bg=None)

print(screen.emit())
```

---

## 5. Clipping and Pasting
Copy, cut, and paste regions between screen buffers with transparency rules.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# Create a source "sprite" screen
sprite = Screen(width=5)
sprite.set_background(Color(200, 200, 0))
sprite.put_text("Smile")

# Create a destination screen
dst = Screen(width=20)
dst.put_text("-" * 20 + "\n")
dst.put_text("-" * 20 + "\n")

# Paste the sprite at box region (x=5, y=0, w=5, h=1)
dst.paste(sprite, box=(5, 0, 5, 1))

print(dst.emit())
```

---

## 6. High-Resolution Geometry & Subpixels
Use geometry primitives, star generators, and high-resolution subpixel modes (`octant`, `quadrant`, `braille`).

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

screen = Screen(width=60)
yellow = Color(255, 255, 0)
green = Color(0, 180, 0)

# Draw a 5-pointed star using half-block pixels
screen.regular_star(cx=30, cy=15, radius=10, n=5, k=2, state=yellow)

# Draw a filled rectangle using universal dispatcher
screen.rectangle(x1=5, y1=5, x2=15, y2=10, state=green, mode="half")

# High-resolution subpixel line using Braille mode (2x4 grid)
screen.spixel_line(x0=0, y0=0, x1=40, y1=20, state=True, mode="braille")

print(screen.emit())
```
