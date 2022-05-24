'''
    BadOS Screen
    Common Screen Functions for BadOS
    David Guidos, May 2022
'''

__version__ = "1.0.0"
__repo__ = "https://github.com/guidoslabs/BadOS.git"

import gc, os, sys, math, time
import board, microcontroller, storage, supervisor
import analogio, digitalio, busio, displayio , terminalio , vectorio, usb_hid
from digitalio import DigitalInOut, Direction, Pull
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_hid.keyboard import Keyboard
import adafruit_miniqr
import adafruit_imageload

WHITE = 0xFFFFFF
BLACK = 0x000000
MAX_BATTERY_VOLTAGE = 400
MIN_BATTERY_VOLTAGE = 320
ICONS_DIR = '/assets/icons/'
IMAGES_DIR = '/assets/images/'
FONTS_DIR = '/assets/fonts/'

class Screen:

    # constants
    display = board.DISPLAY
    display.rotation = 270
    palette = displayio.Palette(1)
    palette[0] = WHITE
    palette_inverted = displayio.Palette(1)
    palette_inverted[0] = BLACK
    WIDTH = display.width
    HEIGHT = display.height
    FONTS_DIR = '/assets/fonts/'

    def __init__(self, background_color = WHITE, with_status_bar = True):
        # get fonts
        font = bitmap_font.load_font(self.FONTS_DIR + 'Arial-12.bdf')
        font2 = bitmap_font.load_font(self.FONTS_DIR + 'Earth 2073-18.bdf')
        font3=terminalio.FONT
        self.fonts = [font, font2, font3]
        self.background_color = background_color
        self.background_palette = self.palette_inverted if background_color == BLACK else self.palette
        self.status_bar = Status_Bar(self.display)
        self.value = self.create_screen()
        self._status_bar_visible = with_status_bar
        if not with_status_bar:
            self.value.pop()

    @property
    def status_bar_visible(self):
        return self._status_bar_visible

    @status_bar_visible.setter
    def status_bar_visible(self, value):
        if value != self._status_bar_visible:
            # visibility changing
            if value:
                # becoming visible 
                # insert into screen at index position 1
                self.value.insert(1, self.status_bar.value)
            else:
                # becoming invisible
                # remove from screen
                self.value.pop(1)
        self._status_bar_visible = value

    # create and layout display screen
    def create_screen(self):
        screen = displayio.Group()
        background = vectorio.Rectangle(pixel_shader=self.background_palette, width=self.WIDTH + 1, height=self.HEIGHT, x=0, y=0)
        screen.append(background)
        screen.append(self.status_bar.value)
        return screen

    # render the screen
    def render(self):
        # refresh the status bar; always at index 1 (background is at 0)
        if self.status_bar_visible:
            self.value[1] = self.status_bar.value
        # update the display
        self.display.show(self.value)
        while self.display.busy==True:
            time.sleep(0.01)     
        self.display.refresh()

    # clear screen
    # remove all screen objects, except the background and status bar (if visible)
    def clear(self):
        while len(self.value) > (2 if self.status_bar_visible else 1):
            self.value.pop()

    @staticmethod
    # create thumbnail of bitmap image
    def thumbnail(bitmap_image, bitmap_palette, thumbnail_width = -1, thumbnail_height = 64):
        # determine size of thumbnail bitmap
        if thumbnail_height == -1:
            thumbnail_height = int(bitmap_image.height * thumbnail_width / bitmap_image.width)
        elif thumbnail_width == -1:
            thumbnail_width = int(bitmap_image.width * thumbnail_height / bitmap_image.height)
        # create the result bitmap
        thumbnail_image = displayio.Bitmap(thumbnail_width, thumbnail_height, 2)
        thumbnail_palette = displayio.Palette
        hf = thumbnail_height / bitmap_image.height # height conversion factor
        wf = thumbnail_width / bitmap_image.width   # height conversion factor
        for x in range(thumbnail_width):
            xi = int(x / wf)
            for y in range(thumbnail_height):
                yi = int(y / hf)
                thumbnail_image[x, y] = bitmap_image[xi, yi]
        return thumbnail_image, bitmap_palette



class Status_Bar:
    
    def __init__(self, display):
        self.display = display
        self.settings = Settings()
        vref_en = analogio.AnalogIn(board.VREF_POWER)
        self.battery_sense = analogio.AnalogIn(board.VBAT_SENSE)   
    
    # determine the number of bars representing the logic supply voltage
    @staticmethod
    def battery_level(battery_voltage):
        vbat=int((battery_voltage / 100) + 140)
        range_map = lambda input, in_min, in_max, out_min, out_max: (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min
        return int(range_map(vbat, MIN_BATTERY_VOLTAGE, MAX_BATTERY_VOLTAGE, 0, 4))

    # create the battery level icon and text
    def create_battery_level(self, x, y):
        # get voltage
        battery_voltage = self.battery_sense.value
        # show voltage value
        bat_level_group = displayio.Group()
        batvolt = label.Label(font=terminalio.FONT, text=str('{:.2f}v'.format((battery_voltage/10000)+1)), color=WHITE, scale=1)
        batvolt.x, batvolt.y = 235, 7
        bat_level_group.append(batvolt)
        # show battery icon
        bat_level_group.append(Rect(x, y, 19, 10, fill=WHITE, outline=WHITE))
        bat_level_group.append(Rect(x + 19, y + 3, 2, 4, fill=WHITE, outline=WHITE))
        bat_level_group.append(Rect(x + 1, y + 1, 17, 8, fill=BLACK, outline=BLACK))
        if self.battery_level(battery_voltage) < 1:
            bat_level_group.append(Line(x + 3, y, x + 3 + 10, y + 10, BLACK))
            bat_level_group.append(Line(x + 3 + 1, y, x + 3 + 11, y + 10, BLACK))
            bat_level_group.append(Line(x + 2 + 2, y - 1, x + 4 + 12, y + 11, WHITE))
            bat_level_group.append(Line(x + 2 + 3, y - 1, x + 4 + 13, y + 11, WHITE))
        else:
            # show battery bars
            for i in range(4):
                if self.battery_level(battery_voltage) / 4 > (1.0 * i) / 4:
                    bat_level_group.append(Rect(i * 4 + x + 2, y + 2, 3, 6, fill=WHITE, outline=WHITE))
        return bat_level_group

    def usb_available(self):
        try:
            keyboard = Keyboard(usb_hid.devices)
            usb = True
        except:
            usb = False
        return usb

    def usb_connected_icon(self):
        if self.usb_available():
            image, palette = adafruit_imageload.load(ICONS_DIR + 'usb.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)        
        else:
            image, palette = adafruit_imageload.load(ICONS_DIR + 'blank.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette) 
        tile_grid = displayio.TileGrid(image, pixel_shader=palette)
        return tile_grid

    @staticmethod        
    def create_storage_usage(x):
        storage_usage = displayio.Group()
        # f_bfree and f_bavail should be the same?
        # f_files, f_ffree, f_favail and f_flag are unsupported.
        f_bsize, f_frsize, f_blocks, f_bfree, _, _, _, _, _, f_namemax = os.statvfs("/")
        f_total_size = f_frsize * f_blocks
        f_total_free = f_bsize * f_bfree
        f_total_used = f_total_size - f_total_free
        f_used = 100 / f_total_size * f_total_used
        # f_free = 100 / f_total_size * f_total_free
        batbg = Rect(x + 10, 3, 80, 10, fill=BLACK, outline=WHITE)
        batlvl1 = Rect(x + 11, 4, 78, 8, fill=BLACK, outline=BLACK)
        batlvl2 = Rect(x + 12, 5, int(76 / 100.0 * f_used), 6, fill=WHITE, outline=WHITE)
        battxt = label.Label(font=terminalio.FONT, text='{:.0f}%'.format(f_used), color=WHITE, scale=1)
        battxt.x, battxt.y = x + 92, 7
        storage_usage.append(batbg)
        storage_usage.append(batlvl1)
        storage_usage.append(batlvl2)
        storage_usage.append(battxt)
        return storage_usage

    @ property
    def value(self):
        # init and set black background
        bar = displayio.Group()
        background = Rect(0, 0, self.display.width, 16, fill=BLACK, outline=BLACK)
        # title
        title = label.Label(font=terminalio.FONT, text='BadOS CPython', color=WHITE, scale=1)
        title.x, title.y = 3, 7
        # storage usage
        stg = self.create_storage_usage(85)
        # battery
        battery = self.create_battery_level(self.display.width - 22 - 3, 3)
        # country/language
        llang = label.Label(font=terminalio.FONT, text=self.settings.language.upper(), color=WHITE, scale=1)
        llang.x, llang.y = 202, 7
        # usb icon
        usb_icon = self.usb_connected_icon()
        usb_icon.x, usb_icon.y = 216, 0
        # append components
        bar.append(background)
        bar.append(title)
        bar.append(stg)
        bar.append(battery)
        bar.append(llang)
        bar.append(usb_icon)
        return bar


class Settings:
    def __init__(self):
        self.language = self.keyboard_language()
        self.layout = self.keyboard_layout(self.language)

    @staticmethod
    def keyboard_language():
        try :
            language = microcontroller.nvm[0:2].decode() # 2 chars form nvm memory index 0
        except:
            language = 'us' # default
        return language
    
    @staticmethod
    def keyboard_layout(language):
        keyboard = Keyboard(usb_hid.devices)
        if language == 'fr':
            # France
            from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
            layout = KeyboardLayoutFR(keyboard) 
        else:
            # USA
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
            layout = KeyboardLayoutUS(keyboard)
        return layout


class Progress_Indicator:

    def __init__(self, x, y, width, height, text_scale):
        self.x, self.y, self.width, self.height, self.text_scale = x, y, width, height, text_scale

    def bar(self, percent_complete):
        bar = displayio.Group()
        print(self.x, self.y, self.width, self.height)
        bar_background = Rect(self.x, self.y, self.width, self.height, fill=BLACK, outline=WHITE)
        print(self.x + 1, self.y + 1, self.width - 2, self.height - 2)
        bar_frame = Rect(self.x + 1, self.y + 1, self.width - 2, self.height - 2, fill=BLACK, outline=BLACK)
        print(self.x + 3, self.y + 3, int((self.width - 6) / 100.0 * percent_complete), self.height - 6)
        bar_progress = Rect(self.x + 3, self.y + 3, int((self.width - 6) / 100.0 * percent_complete + 1), self.height - 6, fill=WHITE, outline=WHITE)
        bar_text = label.Label(font=terminalio.FONT, text='{:.0f}%'.format(percent_complete), color=BLACK, scale=self.text_scale)
        bar_text.x, bar_text.y = self.x + self.width + 2, self.y + 8
        bar.append(bar_background)
        bar.append(bar_frame)
        bar.append(bar_progress)
        bar.append(bar_text)
        return bar
