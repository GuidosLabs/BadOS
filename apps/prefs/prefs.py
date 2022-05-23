'''
    prefs.py
    BadOS Language Preferences Selection Program
    David Guidos, May 2022
'''

import os, time
import board, supervisor, microcontroller
import displayio, terminalio, vectorio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons
from BadOS_Menu import Menu

WHITE = 0xFFFFFF
BLACK = 0x000000

# language preferences list
language_list = [('France','/apps/prefs/france.bmp'),('USA','/apps/prefs/usa.bmp')]

def read_le(s):
    # as of this writting, int.from_bytes does not have LE support, DIY!
    result = 0
    shift = 0
    for byte in bytearray(s):
        result += byte << shift
        shift += 8
    return result

# save language preference to non-volatile memory
# languages saved as 'fr' or 'us'
def save_language(lang):
    tomem=bytearray(lang.encode())
    microcontroller.nvm[0:2]=tomem[0:2]   

# preference menu selection handler
def menu_select(n):
    # save the selected language
    ix = menu_page * 3 + n
    if ix < len(language_list):
        lang = language_list[ix][0][:2].lower()
        save_language(lang)
        # return to the main menu
        supervisor.reload()

# arrow button selecton handler
def page_select(p):
    # arrow key pressed
    # return to the main menu
    supervisor.reload()


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

# create screen
scr = Screen(background_color = WHITE, with_status_bar = True)

# set up buttons
buttons = Buttons()

# create the book selection menu
menu = Menu(display, scr, buttons, language_list, scr.fonts[0], '/apps/prefs/prefs.bmp')

# main loop root
menu_page = 0 
while True:
    ix = menu.show_menu(menu_page)
    if ix < 3:
        # a,b,c
        menu_select(ix)
    elif ix < 5:
        # up, down
        page_select(-1 if ix == 3 else 1)






#   b o n e y a r d

'''

ARROW_THICKNESS = 3
ARROW_WIDTH = 18
ARROW_HEIGHT = 14
ARROW_PADDING = 2
TEXT_PADDING = 4
TEXT_SIZE = 0.5
TEXT_SPACING = int(34 * TEXT_SIZE)
TEXT_WIDTH = WIDTH - TEXT_PADDING - TEXT_PADDING - ARROW_WIDTH

# Draw a upward arrow
def draw_up(x, y, width, height, thickness, padding):
    border = (thickness // 4) + padding
    ebgroup.append(Line(x + border, y + height - border,
                 x + (width // 2), y + border, WHITE))
    ebgroup.append(Line(x + (width // 2), y + border,
                 x + width - border, y + height - border, WHITE))
# Draw a downward arrow
def draw_down(x, y, width, height, thickness, padding):
    border = (thickness // 2) + padding
    ebgroup.append(Line(x + border, y + border,
                 x + (width // 2), y + height - border, WHITE))
    ebgroup.append(Line(x + (width // 2), y + height - border,
                 x + width - border, y + border, WHITE))

# Draw the frame of the text reader
def draw_frame():
    ebgroup.append(Rect(0, 0, display.width +1, display.height, fill=WHITE, outline=WHITE))
    ebgroup.append(Rect(WIDTH - ARROW_WIDTH, 0, ARROW_WIDTH +1, HEIGHT, fill=BLACK, outline=BLACK))
    draw_up(WIDTH - ARROW_WIDTH, (HEIGHT // 4) - (ARROW_HEIGHT // 2),
                ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)
    draw_down(WIDTH - ARROW_WIDTH, ((HEIGHT * 3) // 4) - (ARROW_HEIGHT // 2),
              ARROW_WIDTH, ARROW_HEIGHT, ARROW_THICKNESS, ARROW_PADDING)


def ebbutton(pin):
    global next_page, prev_page, change_font_size, change_font
    if pin == 5:
        next_page = True

    if pin == 4:
        prev_page = True
# ------------------------------
#         Render page
# ------------------------------

def render_page():
    global next_page, prev_page, change_font_size, change_font, ebook
    inipop = len(ebgroup)
    row = 0
    line = ""
    pos = ebook.tell()
    next_pos = pos
    add_newline = False
    led.value=1
    while True:
        # Read a full line and split it into words
        words = ebook.readline().split(" ")

        # Take the length of the first word and advance our position
        next_word = words[0]
        if len(words) > 1:
            next_pos += len(next_word) + 1
        else:
            next_pos += len(next_word)  # This is the last word on the line

        # Advance our position further if the word contains special characters
        if '\u201c' in next_word:
            next_word = next_word.replace('\u201c', '\"')
            next_pos += 2
        if '\u201d' in next_word:
            next_word = next_word.replace('\u201d', '\"')
            next_pos += 2
        if '\u2019' in next_word:
            next_word = next_word.replace('\u2019', '\'')
            next_pos += 2

        # Rewind the file back from the line end to the start of the next word
        ebook.seek(next_pos)

        # Strip out any new line characters from the word
        next_word = next_word.strip()

        # If an empty word is encountered assume that means there was a blank line
        if len(next_word) == 0:
            add_newline = True

        # Append the word to the current line and measure its length
        appended_line = line
        if len(line) > 0 and len(next_word) > 0:
            appended_line += " "
        appended_line += next_word
        appended_length = len(appended_line)*6

        # Would this appended line be longer than the text display area, or was a blank line spotted?
        if appended_length >= TEXT_WIDTH or add_newline:

            # Yes, so write out the line prior to the append
            print(line)
            title = label.Label(font=terminalio.FONT, text=line, color=BLACK, scale=1)
            title.y = (row * TEXT_SPACING) + (TEXT_SPACING // 2) + TEXT_PADDING
            title.x = TEXT_PADDING
            ebgroup.append(title)
            # Clear the line and move on to the next row
            line = ""
            row += 1

            # Have we reached the end of the page?
            if (row * TEXT_SPACING) + TEXT_SPACING >= HEIGHT:
                print("+++++")
                endpop=len(ebgroup)
                display.show(ebgroup)
                display.refresh()
                # pop lines for later :)
                for lp in range(inipop,endpop):
                    ebgroup.pop()
                # Reset the position to the start of the word that made this line too long
                ebook.seek(pos)
                return
            else:
                # Set the line to the word and advance the current position
                line = next_word
                pos = next_pos

            # A new line was spotted, so advance a row
            if add_newline:
                print("")
                row += 1
                if (row * TEXT_SPACING) + TEXT_SPACING >= HEIGHT:
                    print("+++++")
                    endpop=len(ebgroup)
                    display.show(ebgroup)
                    while display.busy==True:
                        time.sleep(0.01)
                    display.refresh()
                    # pop lines for later :)
                    for lp in range(inipop,endpop):
                        ebgroup.pop()
                    return
                add_newline = False
        else:
            # The appended line was not too long, so set it as the line and advance the current position
            line = appended_line
            pos = next_pos


ebook=""
page = 0
font_size = 1
inverted = False

# vars 
next_page = True
prev_page = False
last_offset = 0
current_page = 0
offsets = []

# scan files for book/text files 
files = os.listdir("/book/")
ebfiles = []
count = 0
for n in files:
    if n[-4:]==".txt":
        if n[0:2]!="._":
            ebfiles.append((n.replace(".txt",""),count))
            count=count+1        
ebfiles.append(("EXIT",count))


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


'''

