'''
    image.py
    Simple Image Viewer
    David Guidos, May 2022
'''

import os, time
import board, supervisor
import displayio, terminalio, vectorio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons
from BadOS_Menu import Menu

WHITE = 0xFFFFFF
BLACK = 0x000000
BITMAP_DIR = '/assets/images/'
IMAGE_DIR = '/apps/image/'

# view image
def view_image(imagename, imagepathname):
    # initialize constants and working variables
    # shut off activity LED
    buttons.LED = 0
    # create group for the image
    image_group = displayio.Group()
    print(f'Loading {imagename} from {imagepathname}')
    try:
        # load the image and display it
        image, palette = adafruit_imageload.load(imagepathname, bitmap=displayio.Bitmap, palette=displayio.Palette)
        # process the image to display
        tile_grid = displayio.TileGrid(image, pixel_shader=palette)
        tile_grid.x, tile_grid.y = int((scr.WIDTH - image.width) / 2), int((scr.HEIGHT - image.height) / 2)
        image_group.append(tile_grid)
        # show the image without the screen status bar, but restore the bar afterwards  
        scr.status_bar_visible = False
        scr.value.append(image_group)
        scr.render()
        scr.value.pop()
        scr.status_bar_visible = True
    except:
       # error finding or loading image
       pass
    # wait for button release
    while buttons.states_index() != -1:
        time.sleep(0.05)
    # shut off activity LED
    buttons.LED = 0
    # TODO: timeout with checking buttons
    time.sleep(10)


# get directory list
# TODO: walk the dir structure to find all the images
def get_directories():
    dir_list = []
    return dir_list

# get image files list for a specific folder
def get_image_list(dirpath):
    image_list = []
    # get bitmap names from the specified directory
    ListFiles = os.listdir(dirpath)
    for filename in ListFiles:
        if filename[0] != '.' and filename[-4:].lower() == ".bmp":
            image_list.append((filename.split('.')[0].upper(), dirpath + filename))
    # sort alphabetically
    image_list.sort()
    # add selection for exit
    image_list.append(('exit', '/assets/icons/exit.bmp'))
    return image_list 

# menu selection handler
def menu_select(n):
    global menu_mode
    if menu_mode == 'dir':
        # directory selected
        # change menu to select image in directory
        menu = image_menu
        menu_mode = 'image'
    else:
        # image selected
        # view the selected image
        ix = menu_page * 3 + n
        if ix < len(image_list):
            imagename = image_list[ix][0]
            imagepathname = image_list[ix][1]
            if imagename == 'exit':
                # exit requested
                # turn on activity LED
                buttons.LED = 1
                # return to the main menu
                supervisor.reload()
            else:
                view_image(imagename, imagepathname)

# page selecton handler
def page_select(p):
    global menu_page
    menu_page += p
    if menu_page < 0: menu_page = 0    # TODO: rotate back to last page ?
    if menu_page * 3 >= len(image_list): menu_page = 0


#   m a i n   

# initialize display
display = board.DISPLAY
display.rotation = 270
palette = displayio.Palette(1)
palette[0] = WHITE
palette_inverted = displayio.Palette(1)
palette_inverted[0] = BLACK
WIDTH = display.width
HEIGHT = display.height
IMAGE_WIDTH = 104

# create screen
scr = Screen(background_color = WHITE, with_status_bar = True)

# set up buttons
buttons = Buttons()

# get list of images for menu
image_list = get_image_list(BITMAP_DIR)
print(image_list)

# create the dir/image selection menu
menu_mode = 'image'
menu_page = 0 
dir_menu = Menu(display, scr, buttons, image_list, scr.fonts[0], BITMAP_DIR + 'file.bmp')
image_menu = Menu(display, scr, buttons, image_list, scr.fonts[0], IMAGE_DIR + 'image.bmp')
menu = dir_menu     # start with selecting a directory first

# main loop root
while True:
    ix = menu.show_menu(menu_page)
    if ix < 3:
        # a,b,c
        menu_select(ix)
    elif ix < 5:
        # up, down
        page_select(-1 if ix == 3 else 1)




'''

IMAGE_WIDTH = 104
IMAGE_HEIGHT = 128

# scan files for pictures files
files = os.listdir("/images/")
picfiles = []
count = 0
for n in files:
    if n[-4:]==".bmp":
        if n[0:2]!="._":
            picfiles.append((n.replace(".bmp",""),count))
            count=count+1        
picfiles.append(("EXIT",count))

'''

