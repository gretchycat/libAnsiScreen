# Library Usage: libAnsiScreen

This guide provides runnable code recipes for common tasks using `libAnsiScreen`.

## 1. Basic Setup and Rendering
The most fundamental task is creating a screen, adding content, and rendering it to ANSI.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# Create a screen with 20 columns
screen = Screen(width=20)

# Set some graphics state
screen.set_foreground(Color(255, 0, 0)) # Red
screen.set_background(Color(0, 0, 50))  # Dark Blue

# Write some text
screen.put_text("Hello, ANSI!")

# Render to string and print
print(screen.emit())
```

## 2. Drawing Shapes with Pixel Plotting
`libAnsiScreen` supports a simulated "pixel" mode using half-block characters (▀, ▄, █).

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

screen = Screen(width=40)
red = Color(255, 0, 0)
blue = Color(0, 0, 255)

# Draw a diagonal line using pixels
# (x, y) coordinates where y is in half-character units
for i in range(20):
    screen.pixelplot(i, i, red)
    screen.pixelplot(39-i, i, blue)

print(screen.emit())
```

## 3. Applying Gradients
You can easily apply color gradients to a screen's content.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

screen = Screen(width=30)
screen.put_text("GRADIENT TEXT EXAMPLE\n" * 5)

# Define a simple RGB gradient (Blue to Green to Cyan)
gradient = [
    Color(0, 0, 255),
    Color(0, 255, 0),
    Color(0, 255, 255)
]

# Apply as a horizontal gradient to the foreground
screen.colorize(gradient, mode="hgrad", foreground=True)

print(screen.emit())
```

## 4. Parsing Existing ANSI Data
You can feed ANSI-encoded strings into a `Screen` to manipulate them.

```python
from libansiscreen.screen import Screen
from libansiscreen.parser.ansi_parser import ANSIParser

# Raw ANSI string with color codes
ansi_data = "\x1b[31mRed Text\x1b[0m \x1b[32mGreen Text\x1b[0m"

screen = Screen(width=20)
parser = ANSIParser(screen)
parser.feed(ansi_data)

# Now we can modify the parsed content
# For example, clear the first 3 characters
for x in range(3):
    screen.put_cell(x, 0, char=' ', fg=None, bg=None)

print(screen.emit())
```

## 5. Clipping and Pasting
You can copy regions between screens with transparency support.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

# Source screen with a 'sprite'
sprite = Screen(width=5)
sprite.set_background(Color(200, 200, 0))
sprite.put_text("Smile")

# Destination screen
dst = Screen(width=20)
dst.put_text("-" * 20 + "\n")
dst.put_text("-" * 20 + "\n")

# Paste the sprite at (5, 0)
# box format: (x, y, width, height)
dst.paste(sprite, box=(5, 0, 5, 1))

print(dst.emit())
```

## 6. Advanced Geometry
Use the high-level drawing primitives for complex shapes.

```python
from libansiscreen.screen import Screen
from libansiscreen.color.rgb import Color

screen = Screen(width=60)
yellow = Color(255, 255, 0)

# Draw a regular star (5 points)
# center_x, center_y, radius, n, k, color
screen.regular_star(30, 15, 10, 5, 2, yellow)

# Draw a rectangle
# x1, y1, x2, y2, fill_color
screen.draw_rectangle(5, 5, 15, 10, fill=Color(0, 100, 0))

print(screen.emit())
```
