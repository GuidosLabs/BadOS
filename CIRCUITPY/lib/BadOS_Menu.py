'''
    BadOS Menu
    Common Menu Functions for BadOS
    David Guidos, May 2022
'''
__version__ = "1.0.0"
__repo__ = "https://github.com/guidoslabs/BadOS.git"

import time
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

from BadOS_Buttons import Buttons

# constants
WHITE = 0xFFFFFF
BLACK = 0x000000
BUTTON_CENTER_POSITIONS = (42, 145, 251) # center x positions on screen for bottom buttons

class Menu:

    def __init__(self, display, screen, buttons, item_list, font, defaulticon):
        self.display = display
        self.screen = screen
        self.buttons = buttons
        self.items = item_list
        self.font = font
        self.defaulticon = defaulticon
        #self.buttons = Buttons()

    # generate screen group for menu line starting with item at page number
    def menu_line(self, pagenum):
        menu_line = displayio.Group()
        number_of_items = len(self.items)
        items_per_line = len(BUTTON_CENTER_POSITIONS)
        number_of_pages = (number_of_items - 1) // items_per_line + 1
        for i in range(items_per_line):
            # create line of icons
            ix = pagenum * 3 + i
            if ix < number_of_items:
                x = BUTTON_CENTER_POSITIONS[i]
                appname = self.items[ix][0]
                try:
                    image, palette = adafruit_imageload.load(self.items[ix][1], bitmap=displayio.Bitmap, palette=displayio.Palette)
                except:
                    image, palette = adafruit_imageload.load(self.defaulticon, bitmap=displayio.Bitmap, palette=displayio.Palette)
                # convert to thumbnail if too large
                if image.height > 64 or image.width > 64:
                    if image.height < image.width:
                        # landscape
                        image, palette = self.screen.thumbnail(image, palette, thumbnail_width = 90, thumbnail_height = -1)
                    else:
                        # portrait
                        image, palette = self.screen.thumbnail(image, palette, thumbnail_width = -1, thumbnail_height = 64)
                # process the image to display
                tile_grid = displayio.TileGrid(image, pixel_shader=palette)
                tile_grid.x, tile_grid.y = int(x - 32 + (64 - image.width) / 2), 24   # x - (tile_grid.get_width() // 2)  # 32
                menu_line.append(tile_grid)
                icon = label.Label(self.font, text=self.items[ix][0][0:6].upper(), color=BLACK, scale=1)
                icon_width = 50  # make dynamic using real width?
                icon.x, icon.y =  x - int(icon_width / 2) + (0 if len(icon.text) > 4 else 10), 16 + 90 + 2
                menu_line.append(icon)
            # create page indicators if more than one page
            if number_of_pages > 1:
                ind_size = 7
                status_bar_height = 20
                x = self.display.width - ind_size - 2
                y = (self.display.height - status_bar_height) // 2 - (number_of_pages * (ind_size + 2) // 2) + 10
                for i in range(number_of_pages):
                    if i == pagenum:
                        page_ind = Rect(x, y + (i * (ind_size + 2)), ind_size, ind_size, fill=BLACK, outline=BLACK)
                    else:
                        page_ind = Rect(x, y + (i * (ind_size + 2)), ind_size, ind_size, fill=WHITE, outline=BLACK)
                    menu_line.append(page_ind)
        return menu_line

    # render the screen
    def render_screen(self):
        self.display.show(self.screen.value)
        while self.display.busy==True:
            time.sleep(0.01)     
        self.display.refresh()   

    # show menu and await response
    def show_menu(self, pagenum):
        # save group count for removing items to allow clean paging
        groupcount = len(self.screen.value)
        # create and add the new menu line
        menu_line = self.menu_line(pagenum)
        self.screen.value.append(menu_line)
        # display the screen
        self.render_screen()
        # after rendering, remove menu line items in preparation for paging
        for i in range(groupcount, len(self.screen.value)):
            self.screen.value.pop()
        # await response
        ix = self.buttons.await_click()
        self.buttons.led.value = 1  # turn on LED
        return ix



