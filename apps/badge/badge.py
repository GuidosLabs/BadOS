'''
    badge.py
    BadOS app to display badges
    David Guidos, May 2022
'''

import gc, os, sys, math, time
import board, microcontroller, storage, supervisor
import analogio, digitalio, busio, displayio , terminalio , vectorio
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

from BadOS_Buttons import Buttons
from BadOS_Screen import Screen, Status_Bar
from BadOS_Menu import Menu

# constants
WHITE = 0xFFFFFF
BLACK = 0x000000
BADGES_DIR = '/apps/badge/'
ICONS_DIR = '/assets/icons/'
IMAGES_DIR = '/assets/images/'
FONTS_DIR = '/assets/fonts/'

# generate QR code bitmap
# usage example:
#   qr_bitmap = create_qr_bitmap(b"https://guidoslabs.com")
def create_qr_bitmap(code_bytes):
    # create the code
    qr = adafruit_miniqr.QRCode(qr_type = 3, error_correct = adafruit_miniqr.L)
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
    # black/white palette
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
    qr_img = displayio.TileGrid(qr_bitmap, pixel_shader = palette, x = x_pos, y = y_pos)
    qr_group = displayio.Group(scale = scale)
    qr_group.append(qr_img)
    return qr_group

# create QR bitmap from code matrix
def bitmap_QR(matrix):
    # monochome (2 color) palette
    BORDER_PIXELS = 2
    # bitmap the size of the screen, monochrome (2 colors)
    bitmap = displayio.Bitmap(matrix.width + 2 * BORDER_PIXELS, matrix.height + 2 * BORDER_PIXELS, 2)
    # raster the QR code
    for y in range(matrix.height):  # each scanline in the height
        for x in range(matrix.width):
            if matrix[x, y]:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 1
            else:
                bitmap[x + BORDER_PIXELS, y + BORDER_PIXELS] = 0
    return bitmap

# create QR for contact vcard using the badge data
# to replace photo in badge
def badgeQR(badge_data, badge):
    # create vcard string from badge data
    vcard_text = vcard(badge_data)
    # create QR code for the vcard string
    qr = adafruit_miniqr.QRCode(qr_type=9, error_correct=adafruit_miniqr.L)
    qr.add_data(vcard_text.encode('ascii'))
    qr.make()
    qr_bitmap = bitmap_QR(qr.matrix)
    scale = min(board.DISPLAY.width // qr_bitmap.width, board.DISPLAY.height // qr_bitmap.height)
    pos_x = (display.width - IMAGE_WIDTH) + int((display.width - (display.width - IMAGE_WIDTH)-qr_bitmap.width)/2)
    pos_y = int((display.height-qr_bitmap.height)/2)
    qr_img = displayio.TileGrid(qr_bitmap, pixel_shader=palette, x=pos_x, y=pos_y)
    badge.append(qr_img)

# get badge data from file
def get_badge_data(badgedatapath):
    badge_data_dict = {}
    try:
        with open(badgedatapath, "r") as f:       
            badge_data_dict['company'] = f.readline().strip()
            badge_data_dict['name'] = f.readline().strip()
            badge_data_dict['detail1_title'] = f.readline().strip()
            badge_data_dict['detail1_text'] = f.readline().strip()
            badge_data_dict['detail2_title'] = f.readline().strip()
            badge_data_dict['detail2_text'] = f.readline().strip()
            badge_data_dict['telfix'] = f.readline().strip()
            badge_data_dict['telmob'] = f.readline().strip()
            badge_data_dict['email'] = f.readline().strip()
            badge_data_dict['site'] = f.readline().strip()
    except:
        print(f'Error reading {badgedatapath}')    
    return badge_data_dict

# create vcard string for QR code from badge data dictionary
def vcard(badge_data):
    vcard = 'BEGIN:VCARD\n'
    vcard += 'N:' + badge_data['name'] + ';\n'
    vcard += 'TEL;TYPE=work:' + badge_data['telfix'] + '\n'
    vcard += 'TEL;TYPE=cell:' + badge_data['telmob'] + '\n'
    vcard += 'EMAIL;TYPE=work:' + badge_data['email'] + '\n'
    vcard += 'ORG:' + badge_data['company'] + '\n'
    vcard += 'TITLE:' + badge_data['detail1_title'] + ' ' + badge_data['detail1_text'] + '\n'
    vcard += 'NOTE:' + badge_data['detail2_title'] + ' ' + badge_data['detail2_text'] + '\n'
    #vcard += 'ADR;Type=WORK:' + adr + '\n'
    vcard += "URL:" + badge_data['site'] + '\n'
    vcard += 'VERSION:3.0\nEND:VCARD\n'
    return vcard

# create and display the badge
def show_badge(badgename, badge_data):
    global showqr
    COMPANY_HEIGHT = 40
    DETAILS_HEIGHT = 20
    NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
    TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 2
    LEFT_PADDING = 5
    NAME_PADDING = 10

    # create group for the badge
    badge = displayio.Group()

    if showqr == False:
        try:
            badgebmppath = BADGES_DIR + badgename + '/' + badgename + '.bmp'
            image, palette = adafruit_imageload.load(badgebmppath, bitmap=displayio.Bitmap, palette=displayio.Palette)
        except:
            image, palette = adafruit_imageload.load(IMAGES_DIR + 'user.bmp', bitmap = displayio.Bitmap, palette=displayio.Palette)
        photo_image = displayio.TileGrid(image, pixel_shader=palette)
        photo_image.x, photo_image.y = display.width - IMAGE_WIDTH, 0 

    # clear screen (black)
    badge.append(Rect(0, 0, display.width+1, display.height, fill=BLACK, outline=BLACK))   #ID 
    # Draw a border around the image
    badge.append(Line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0, WHITE))
    badge.append(Line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1, WHITE))
    badge.append(Line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1, WHITE))
    badge.append(Line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1, WHITE))
    # company name
    ctxt=label.Label(font=badge_screen.fonts[1], text=badge_data['company'], color=WHITE, scale=1)
    ctxt.x, ctxt.y = LEFT_PADDING, (COMPANY_HEIGHT // 2)
    badge.append(ctxt)

    # white background behind the name
    badge.append(Rect(1, COMPANY_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT, fill=WHITE, outline=WHITE))
    # name, scaling it based on the available width
    fsize = 3 
    name = badge_data['name']
    name_length = len(name) * (fsize * 12)
    if name_length >= (TEXT_WIDTH - NAME_PADDING):
        fsize = 2
        name_length = len(name) * (fsize * 6)
        if name_length >= (TEXT_WIDTH - NAME_PADDING):
            fsize = 1
            name_length = len(name) * (fsize * 6)  
    name_length = len(name) * 18
    ntxt = label.Label(font=badge_screen.fonts[1], text=name, color=BLACK, scale=1)
    ntxt.x, ntxt.y = LEFT_PADDING, (NAME_HEIGHT // 2) + COMPANY_HEIGHT  # (TEXT_WIDTH - name_length) // 2
    badge.append(ntxt)
    # Draw a white backgrounds behind the details
    badge.append(Rect(1, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH, DETAILS_HEIGHT - 1, fill=WHITE, outline=WHITE))
    badge.append(Rect(1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1, fill=WHITE, outline=WHITE))
    # Draw the first detail's title and text
    name_length = len(badge_data['detail1_title']) * 8
    ntxt = label.Label(font=badge_screen.fonts[0], text=badge_data['detail1_title'], color=BLACK, scale=1)
    ntxt.x, ntxt.y = LEFT_PADDING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2) 
    badge.append(ntxt)    
    ntxt = label.Label(font=badge_screen.fonts[0], text=badge_data['detail1_text'], color=BLACK, scale=1)
    #ntxt.x, ntxt.y = LEFT_PADDING + name_length + DETAIL_SPACING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2)
    ntxt.x, ntxt.y = 97, HEIGHT - ((DETAILS_HEIGHT * 3) // 2)
    badge.append(ntxt)    
    # Draw the second detail's title and text
    name_length = len(badge_data['detail2_title']) * 8
    ntxt = label.Label(font=badge_screen.fonts[0], text=badge_data['detail2_title'], color=BLACK, scale=1)
    ntxt.x, ntxt.y = LEFT_PADDING, HEIGHT - (DETAILS_HEIGHT // 2)
    badge.append(ntxt)      
    ntxt=label.Label(font=badge_screen.fonts[0], text=badge_data['detail2_text'], color=BLACK, scale=1)
    #ntxt.x, ntxt.y = LEFT_PADDING + name_length + DETAIL_SPACING, HEIGHT - (DETAILS_HEIGHT // 2)
    ntxt.x, ntxt.y = 97, HEIGHT - (DETAILS_HEIGHT // 2)
    badge.append(ntxt)
    dismiss_badge = False
    while not dismiss_badge:      
        # draw badge image
        if showqr:
            # show QR code
            badgeQR(badge_data, badge)
        else:
            # show photo/image
            badge.append(photo_image)
        # display the completed badge
        display.show(badge)
        display.refresh()
        # remove image for possible replacement
        badge.pop()
        # shut off activity LED
        buttons.LED = 0
        # wait for keypress to dismiss or swap photo/QR code
        button_index = buttons.await_click()
        # turn on activity LED
        buttons.LED = 1
        # wait for button release
        while buttons.states_index() != -1:
            time.sleep(0.05)
        # perform button click
        if button_index == 4:
            # down arrow pressed
            # return to the main menu
            supervisor.reload()
        elif button_index == 3:
            # up arrow
            # toggle qr and photo
            showqr = not showqr
        else:
            # a,b,c pressed
            # return to select a badge
            dismiss_badge = True


# get badge list for selection menu
def get_badge_list():
    badge_list = []
    # get badge names from badge directories; names and icon bitmaps
    ListFiles = os.listdir(BADGES_DIR)
    for badgename in ListFiles:
        #d = os.path.join(rootdir, app)
        #if os.path.isdir(d):
        if "." not in badgename:
            badge_list.append((badgename, BADGES_DIR + badgename + '/' + badgename + '.bmp'))
    badge_list.sort()
    # add selection for exit
    badge_list.append(('exit', '/assets/icons/exit.bmp'))
    return badge_list

# menu selection handler
def menu_select(n):
    # display the selected badge
    ix = menu_page * 3 + n
    if ix < len(badge_list):
        badgename = badge_list[ix][0]
        if badgename == 'exit':
            # exit requested
            # turn on activity LED
            buttons.LED = 1
            # return to the main menu
            supervisor.reload()
        else:
            badgedatapath = BADGES_DIR + badgename + '/' + badgename + '.txt'
            badgedata = get_badge_data(badgedatapath)
            show_badge(badgename, badgedata)

# page selecton handler
def page_select(p):
    global menu_page
    menu_page += p
    if menu_page < 0: menu_page = 0    # TODO: rotate back to last page ?
    if menu_page * 3 >= len(badge_list): menu_page = 0



#   m a i n   s e c t i o n

# variables
menu_page = 0
showqr=False

# buttons and LED 
buttons = Buttons()
buttons.led.value = 1   # led on during start-up

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
badge_screen = Screen()

# get list of badges for menu
badge_list = get_badge_list()

# create the badge selection menu
menu = Menu(display, badge_screen, buttons, badge_list, badge_screen.fonts[0], BADGES_DIR + 'badge' + '.bmp')

# main loop root 
while True:
    ix = menu.show_menu(menu_page)
    if ix < 3:
        # a,b,c
        menu_select(ix)
    elif ix < 5:
        # up, down
        page_select(-1 if ix == 3 else 1)



#   B O N E Y A R D

'''

# add menu line to screen
def update_screen_menuline():
    global mainScreen
    # save group count for removing items to allow clean paging
    groupcount = len(mainScreen)
    # create and add the new menu line
    menu_line = create_menu_line(menu_page)
    mainScreen.append(menu_line)
    # display the screen
    render_screen(mainScreen)
    # after rendering, remove menu line items in preparation for paging
    for i in range(groupcount, len(mainScreen)):
        mainScreen.pop()


    print('pos_x :' + str(pos_x))
    print('pos_y :' + str(pos_y))


'''
