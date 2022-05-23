'''
    world.py
    World Map Demo App
    David Guidos, May 2022
'''

import time
import supervisor
import displayio, terminalio, vectorio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

from BadOS_Screen import Screen, Progress_Indicator
from BadOS_Buttons import Buttons

WHITE = 0xFFFFFF
BLACK = 0x000000


def world_map(screen):
    # create the bitmap
    world_width, world_height = 128 * 2, 64 * 2
    world_compressed = '26040309|2304010E|1A0203010103060C2005|1703040101010103060A1E0A0201|0B020B040201020505090E020B1C|08130106020303070E0803070121|061A0304030504030907022F|06170702040310040133|0418050208020F05012D0203|0402060F0505180402280601|0301081004051302030302280702|0C11020711010101032E0701|0C110108110101020131|0C1603011434|0C1603021235|0C17170B02050220|0B151705020101050502021F|0A151804040201070103021D|0A13190406010101020802190301|0A121B0203020709011B0201|0A121C060A220201|0B0F1C0903010522|0B0E1D35|0B01010605011C19011C|0D0506011B140105031A|0C0101042214010805140101|0F030701191601080413|0E040202040101011616020706050306|1005070116170106070405050601|13041C170203090307050501|14031C1A0C0208040501|16010401171902010A020A020601|16020206141B0B0108010902|1908141A0C0107010A01|190B1204021216010502|190B1A0F16020402|180D190E17020303|180F170D1902020301010401|1811150D1902020301010504|1813140B1B010E03|1813140B1D030A04|1912140B|1A10150C2601|1A10150C030121030201|1B0F150C02021E060201|1C0E150A03021E0B|1D0C160904021D0C|1D0C170903021B0F|1D0A190804011B10|1D091A072110|1D091B062110|1D081C052210|1D081C0423040308|1D0645010805|1D074D040901|1E045C01|1E0351010901|1E045901|1E035801|1E04|1F02|2002|2102'
    world_bitmap = displayio.Bitmap(world_width, world_height, 2)
    world_palette = screen.palette

    # # clear the bitmap to white
    # for x in range(world_width):
    #     for y in range(world_height):
    #         world_bitmap[x, y] = 1
    # decompress the world map
    y = 0
    for r in world_compressed.split('|'):
        x = 0
        for n in range(len(r)//4):
            x += int(r[n*4:n*4+2], 16)
            for xd in range(int(r[n*4+2:n*4+4], 16)):
                x += 1
                world_bitmap[x * 2, y * 2] = 1
                world_bitmap[x * 2 + 1, y * 2] = 1
                world_bitmap[x * 2, y * 2 + 1] = 1
        y += 1

    world_tile_grid = displayio.TileGrid(world_bitmap, pixel_shader=world_palette)
    world_tile_grid.x, world_tile_grid.y = 32, 0
    return world_tile_grid

	
#   m a i n

# initialize display
scr = Screen()
title = label.Label(font=terminalio.FONT, text='World Map', color=BLACK, scale=1)
title.x, title.y = 130, 20
scr.value.append(title)

# set up buttons
btns = Buttons()
btns.led.value = 1

# remove the status bar
scr.status_bar_visible = False
# add the world image
scr.value.append(world_map(scr))
# display the image
scr.render()

# loop until timeout or arrow button clicked
btns.led.value = 0
end_requested = False
start_time = time.monotonic()
while not end_requested:
    if btns.states_index() == 3 or btns.states_index() == 4:
        # up or down clicked
        end_requested = True
    if time.monotonic() > start_time + 60:
        # 60 sec timeout
        end_requested = True
    time.sleep(0.05)

# return to the menu
btns.led.value = 1
supervisor.reload()


