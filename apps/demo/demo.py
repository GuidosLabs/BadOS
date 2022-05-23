'''
helpfull demo file by BeBoX to help users programing their
personnal badge applications
demo show various usage of displayio libs
contact : depanet@gmail.com
twitter : @beboxos
'''
import time
import board, terminalio, displayio, vectorio, supervisor
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon

import adafruit_miniqr

display = board.DISPLAY

# Set text, font, and color
title = "Hello World"
subtitle = "From CircuitPython"
font2 = terminalio.FONT
font = bitmap_font.load_font("/assets/fonts/Arial-12.bdf")
color = 0x000000
WHITE = 0xFFFFFF
BLACK = 0x000000

# Set the palette for the background color
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF

# Add a background rectangle
rectangle = vectorio.Rectangle(pixel_shader=palette, width=298-110, height=display.height-8, x=4, y=4)

# Create the title and subtitle labels
title_label = label.Label(font, text=title, color=color, scale=2)
subtitle_label = label.Label(font, text=subtitle, color=color, scale=1)

# Set the label locations
title_label.x = 10
title_label.y = 45

subtitle_label.x = 10
subtitle_label.y = 90

# Create the display group and append objects to it
group = displayio.Group()
print("group len" + str(len(group)))
group.append(rectangle)
print("group len" + str(len(group)))
group.append(title_label)
print("group len" + str(len(group)))
group.append(subtitle_label)
print("group len" + str(len(group)))

#image
image, palette = adafruit_imageload.load(
    '/assets/images/badger.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette
)
tile_grid = displayio.TileGrid(image, pixel_shader=palette)
tile_grid.x = 298-104
group.append(tile_grid)
print("group len" + str(len(group)))
# Show the group and refresh the screen to see the result
display.show(group)
display.refresh()
time.sleep(5)
group.pop()
print("group len" + str(len(group)))
display.refresh()
time.sleep(5)
group.append(tile_grid)
print("group len" + str(len(group)))
display.refresh()
time.sleep(5)
# Loop forever so you can enjoy your message
splash = displayio.Group()
display.show(splash)

# Make a background color fill
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF
bg_sprite = displayio.TileGrid(color_bitmap, x=0, y=0, pixel_shader=color_palette)
splash.append(bg_sprite)
##########################################################################

splash.append(Line(5, 74, 10, 110, 0x000000))
splash.append(Line(15, 74, 20, 110, 0x000000))
splash.append(Line(25, 74, 30, 110, 0x000000))
splash.append(Line(35, 74, 40, 110, 0x000000))

# Draw star
polygon = Polygon(
    [
        (255, 40),
        (262, 62),
        (285, 62),
        (265, 76),
        (275, 100),
        (255, 84),
        (235, 100),
        (245, 76),
        (225, 62),
        (248, 62),
    ],
    outline=0x000000,
)
splash.append(polygon)

triangle = Triangle(170, 20, 140, 90, 210, 100, fill=0x999999, outline=0x000000)
splash.append(triangle)

rect = Rect(80, 20, 41, 41, fill=0x999999, outline=0x666666)
splash.append(rect)

circle = Circle(100, 100, 20, fill=0xFFFFFF, outline=0x000000)
splash.append(circle)

rect2 = Rect(70, 85, 61, 30, outline=0x0, stroke=3)
splash.append(rect2)

roundrect = RoundRect(10, 10, 61, 51, 10, fill=0x666666, outline=0x000000, stroke=6)
splash.append(roundrect)

display.refresh()
time.sleep(5)
display.show(group)
display.refresh()
time.sleep(5)

# generate QR code bitmap
# usage example:
#   qr_bitmap = create_qr_bitmap(b"https://guidoslabs.com")
def create_qr_bitmap(code_bytes):
    # create the code
    qr = adafruit_miniqr.QRCode(qr_type=3, error_correct=adafruit_miniqr.L)
    qr.add_data(code_bytes)
    qr.make()
    # convert to monochrome bitmap sized to the screen (limited by height)
    BORDER_PIXELS = 2
    bitmap = displayio.Bitmap(qr.matrix.width + 2 * BORDER_PIXELS, qr.matrix.height + 2 * BORDER_PIXELS, 2)
    # raster the QR code
    for y in range(qr.matrix.height):
        for x in range(qr.matrix.width):
            bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 1 if qr.matrix[x, y] else 0
    return bitmap

# add QR code to the screen
# usage example:
#   qr_group = show_qr_bitmap(create_qr_bitmap(b"http://guidoslabs.com"), -1, -1, -1, -1)
#   board.DISPLAY.show(qr_group)
def show_qr_bitmap(qr_bitmap, x_pos, y_pos, d_width, d_height):
    # We'll draw with a classic black/white palette
    palette = displayio.Palette(2)
    palette[0] = WHITE
    palette[1] = BLACK
    # use hardware display width and height if -1, -1
    if d_width == -1 and d_height == -1:
        d_width = board.DISPLAY.width
        d_height = board.DISPLAY.height
    # scale the QR code
    scale = min(d_width // qr_bitmap.width, d_height // qr_bitmap.height)
    # if -1, -1 location, center it
    if x_pos == -1 and y_pos == -1: 
        x_pos = int(((board.DISPLAY.width / scale) - qr_bitmap.width) / 2)
        y_pos = int(((board.DISPLAY.height / scale) - qr_bitmap.height) / 2)
    qr_img = displayio.TileGrid(qr_bitmap, pixel_shader=palette, x=x_pos, y=y_pos)
    qr_group = displayio.Group(scale=scale)
    qr_group.append(qr_img)
    return qr_group

splash2 = show_qr_bitmap(create_qr_bitmap(b"http://guidoslabs.com"), -1, -1, -1, -1)
board.DISPLAY.show(splash2)
display.refresh()
time.sleep(5)
board.DISPLAY.show(splash)
display.refresh()
time.sleep(5)
board.DISPLAY.show(group)
display.refresh()
time.sleep(5)
board.DISPLAY.show(splash2)
display.refresh()
time.sleep(5)

# return to the menu
supervisor.reload()

print('info app ended')
