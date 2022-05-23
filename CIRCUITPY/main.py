'''
    BadOS Launcher main.py
    By David Guidos, May 2022
    Inspired by the Pimoroni Badger2040 badge, AdaFruit and BeBox
'''

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
import adafruit_ducky
import adafruit_imageload

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons
from BadOS_Menu import Menu

# constants
WHITE = 0xFFFFFF
BLACK = 0x000000

APPS_DIR = '/apps/'
ICONS_DIR = '/assets/icons/'
IMAGES_DIR = '/assets/images/'
FONTS_DIR = '/assets/fonts/'

def read_le(s):
    # as of this writting, int.from_bytes does not have LE support, DIY!
    result = 0
    shift = 0
    for byte in bytearray(s):
        result += byte << shift
        shift += 8
    return result

# get app list
def get_app_list():
    app_list = []
    # get app information from app directories; names and icon bitmaps
    ListFiles = os.listdir(APPS_DIR)
    for appname in ListFiles:
        #d = os.path.join(rootdir, app)
        #if os.path.isdir(d):
        if appname[0:1] != ".":
            app_list.append((appname, APPS_DIR + appname + '/' + appname + '.bmp'))
    # sort alphabetically
    app_list.sort()
    return app_list 

# menu selection handler
def menu_select(n):
    # invoke the selected app
    ix = menu_page * 3 + n
    if ix < len(app_list):
        appname = app_list[ix][0]
        appnamepath = APPS_DIR + appname + '/' + appname + '.py'
        #exec(open(appnamepath).read())
        supervisor.set_next_code_file(appnamepath)
        supervisor.reload()

# page selecton handler
def page_select(p):
    global menu_page
    menu_page += p
    if menu_page < 0: menu_page = 0    # TODO: rotate back to last page ?
    if menu_page * 3 >= len(app_list): menu_page = 0


#   m a i n   s e c t i o n

# disable autoreload
supervisor.disable_autoreload()

# variables
menu_page = 0

# buttons and LED 
buttons = Buttons()
buttons.led.value = 1   # led on during start-up

# check for HID request on restart (any A,B,C pressed)
if buttons.a.value or buttons.b.value or buttons.c.value:
    # TODO: invoke HID app for the specified button
    pass

# initialize display
display = board.DISPLAY
display.rotation = 270
palette = displayio.Palette(1)
palette[0] = WHITE
palette_inverted = displayio.Palette(1)
palette_inverted[0] = BLACK
WIDTH = display.width
HEIGHT = display.height

# create screen
screen = Screen()

# get list of apps for menu and create menu object
app_list = get_app_list()
#print(app_list)
menu = Menu(display, screen, buttons, app_list, screen.fonts[0], ICONS_DIR + 'file' + '.bmp')

# main loop root 
while True:
    ix = menu.show_menu(menu_page)
    if ix < 3:
        # a,b,c
        menu_select(ix)
    elif ix < 5:
        # up, down
        page_select(-1 if ix == 3 else 1)
