'''
    demo.py
    Demo of Screen Setup and Graphics for the Badger2040 eInk Badge
    David Guidos, May 2022
'''

import time
import supervisor
import displayio, terminalio, vectorio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons

WHITE = 0xFFFFFF
BLACK = 0x000000

#   f u n c t i o n s

# find center point of a bounding box of a list of points
# note: if points are end points of a line segment, the returned point is the midpoint
def center_point(points):
    	return ( 
		(max([p[0] for p in points]) + min([p[0] for p in points])) / 2,
		(max([p[1] for p in points]) + min([p[1] for p in points])) / 2 
		)

# normalize a list of points to their center point
def normalize_points(points):
    (cpx, cpy) = center_point(points) 
    return [(x - cpx, y - cpy) for (x, y) in points]

def positioned_triangle(points, center_point, scale, fill_color, outline_color):
    triangle = Triangle(int(points[0][0] * scale + center_point[0]), int(points[0][1] * scale + center_point[1]), 
                        int(points[1][0] * scale + center_point[0]), int(points[1][1] * scale + center_point[1]), 
                        int(points[2][0] * scale + center_point[0]), int(points[2][1] * scale + center_point[1]), 
                        fill=fill_color, outline=outline_color)
    return triangle


#   m a i n   

# initialize display
scr = Screen(background_color = WHITE, with_status_bar = False)

# set up buttons
btns = Buttons()

# -----------------------------------

# get sample image (BadOS Logo)
bados_image, bados_palette = adafruit_imageload.load('/assets/images/BadOS-120.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
# add full-size and scaled 2/3, 1/3 images to the screen
x, y = 5, 5
for i in range(3):
    # scale it
    img, pal = scr.thumbnail(bados_image, bados_palette, thumbnail_width = -1, thumbnail_height = int((1 - (i / 3)) * bados_image.height))
    # add the images to the display
    tile_grid = displayio.TileGrid(img, pixel_shader=pal)
    tile_grid.x, tile_grid.y = x, y
    scr.value.append(tile_grid)
    x += img.width + 10

scr.render()

# display for 5 seconds
time.sleep(5)

# -----------------------------------

scr.clear()

# triangles
tri = normalize_points([(85, 10), (70, 45), (105, 50)])
tri_center = (220, 70)
scale_step = 1
for s in range(5, 0, -scale_step):
    scr.value.append(positioned_triangle(tri, tri_center, s / 2.0, fill_color=BLACK, outline_color=BLACK))
    scr.value.append(positioned_triangle(tri, tri_center, (s - scale_step / 2.0) / 2.0, fill_color=WHITE, outline_color=BLACK))

# square
square = Rect(80, 20, 42, 42, fill=BLACK, outline=BLACK)
scr.value.append(square)
square = Rect(85, 25, 21, 21, fill=WHITE, outline=BLACK)
scr.value.append(square)

# circle
circle = Circle(100, 100, 21, fill=BLACK, outline=BLACK)
scr.value.append(circle)
circle = Circle(95, 95, 10, fill=WHITE, outline=BLACK)
scr.value.append(circle)

# texts
txt=label.Label(font=scr.fonts[0], text='Squares', color=BLACK, scale=1)
txt.x, txt.y = 10, 40
scr.value.append(txt)
txt=label.Label(font=scr.fonts[0], text='Circles', color=BLACK, scale=1)
txt.x, txt.y = 10, 100
scr.value.append(txt)
txt=label.Label(font=scr.fonts[0], text='Triangles', color=BLACK, scale=1)
txt.x, txt.y = 180, 5
scr.value.append(txt)

scr.render()

# display for 5 seconds
time.sleep(5)


# -----------------------------------



# -----------------------------------



# -----------------------------------


# loop until timeout or arrow button clicked
end_requested = False
start_time = time.monotonic()
while not end_requested:
    if btns.states_index() == 3 or btns.states_index() == 4:
        # up or down clicked
        end_requested = True
    if time.monotonic() > start_time + 30:
        # 30 sec timeout
        end_requested = True
    time.sleep(0.05)

# return to the menu
supervisor.reload()

'''


# display the info
LINE_HEIGHT = 16
y = int(LINE_HEIGHT * 1.5)
with open('/apps/info/info.txt') as info_file:
    for info_line in info_file:
        textline = label.Label(scr.fonts[2], text=info_line, color=BLACK, scale=1)
        textline.x, textline.y =  10, y
        scr.value.append(textline)
        y += LINE_HEIGHT
        print(f'Screen Y: {y}   {len(scr.value)}')
    # add the OS image
    image, palette = adafruit_imageload.load('/assets/images/BadOS-120.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
    image, palette = scr.thumbnail(image, palette, thumbnail_width = 80, thumbnail_height = -1)
    tile_grid = displayio.TileGrid(image, pixel_shader=palette)
    tile_grid.x, tile_grid.y = 215, 55
    scr.value.append(tile_grid)



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

'''
