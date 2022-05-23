'''
    info.py
    BadOS Info Screen
    David Guidos, May 2022
'''

import time
import supervisor
import displayio, terminalio, vectorio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons

WHITE = 0xFFFFFF
BLACK = 0x000000

#   m a i n   

# initialize display
scr = Screen(background_color = WHITE, with_status_bar = True)

# set up buttons
btns = Buttons()

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
scr.render()
print(f'Screen Rendered {len(scr.value)}')

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
