'''
    ebook.py
    Simple eBook Viewer
    David Guidos, May 2022
'''

import os, time
import board, supervisor
import displayio, terminalio, vectorio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label   #, wrap_text_to_pixels ?

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons
from BadOS_Menu import Menu

WHITE = 0xFFFFFF
BLACK = 0x000000
EBOOK_DIR = '/apps/ebook/'

# clean string of any special characters
def clean_string(s):
    new_s = s
    return new_s

# view book
def view_book(bookname, bookpathname):
    # initialize constants and working variables
    LINE_HEIGHT = 20
    current_page_pointer_index = 0
    file_page_pointers = [0]
    # open the book txt file
    bf = open(bookpathname, 'r')
    # read and process text lines
    finished_viewing = False
    background = vectorio.Rectangle(pixel_shader=scr.background_palette, width=scr.WIDTH + 1, height=scr.HEIGHT, x=0, y=0)
    while not finished_viewing:
        # create page display group for the book page
        book_page = displayio.Group()
        book_page.append(background)
        # go to the file position specified by current_page_pointer_index
        bf.seek(file_page_pointers[current_page_pointer_index])
        line_buffer = bf.readline()
        #wrapped_text = "\n".join(wrap_text_to_pixels(line_buffer, scr.WIDTH, scr.fonts[1]))
        #print(f'Text: {wrapped_text}')
        # process book text line into display lines
        # TODO: special characters? causing next-line stuff
        chars_per_line = 36
        for i in range(7):
            if len(line_buffer) < chars_per_line:
                line_buffer += bf.readline()
            # clean special characters
            line_buffer = clean_string(line_buffer) 
            # TODO: trim back to beginning/end of word and readd unused chars to line_buffer
            dl = label.Label(font=scr.fonts[0], text=line_buffer[0:chars_per_line], color=BLACK, scale=1)
            dl.x, dl.y = 2, int((i + 0.5) * LINE_HEIGHT)
            book_page.append(dl)
            line_buffer = line_buffer[chars_per_line:]
        # update page pointers to last used character on file
        next_page_p = bf.tell() - len(line_buffer)
        if current_page_pointer_index < len(file_page_pointers):
            file_page_pointers.append(next_page_p)
        # display the completed badge
        display.show(book_page)
        display.refresh()
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
            # next page
            current_page_pointer_index += 1
            if current_page_pointer_index >= len(file_page_pointers): current_page_pointer_index = len(file_page_pointers) - 1
        elif button_index == 3:
            # up arrow
            # prevous page
            current_page_pointer_index -= 1
            if current_page_pointer_index < 0: current_page_pointer_index = 0
        else:
            # a,b,c pressed
            # finish viewing this book
            if button_index == 2:
                # c pressed
                # return to the main menu
                supervisor.reload()
            else:
                # return to select another book
                finished_viewing = True


# get book files list
def get_book_list():
    book_list = []
    # get app information from app directories; names and icon bitmaps
    ListFiles = os.listdir(EBOOK_DIR)
    for book in ListFiles:
        if book[-4:].lower() == ".txt":
            book_list.append((book.split('.')[0].upper(), EBOOK_DIR + book))
    # sort alphabetically
    book_list.sort()
    # add selection for exit
    book_list.append(('exit', '/assets/icons/exit.bmp'))
    return book_list 

# menu selection handler
def menu_select(n):
    # view the selected book
    ix = menu_page * 3 + n
    if ix < len(book_list):
        bookname = book_list[ix][0]
        bookpathname = book_list[ix][1]
        if bookname == 'exit':
            # exit requested
            # turn on activity LED
            buttons.LED = 1
            # return to the main menu
            supervisor.reload()
        else:
            view_book(bookname, bookpathname)

# page selecton handler
def page_select(p):
    global menu_page
    menu_page += p
    if menu_page < 0: menu_page = 0    # TODO: rotate back to last page ?
    if menu_page * 3 >= len(book_list): menu_page = 0


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

# get list of books for menu
book_list = get_book_list()

# create the book selection menu
menu = Menu(display, scr, buttons, book_list, scr.fonts[0], EBOOK_DIR + 'ebook' + '.bmp')

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

