'''
	clock.py
    BadOS App to display the time
	David Guidos, April 2022
'''

import time
import board, microcontroller, storage, supervisor
import terminalio, vectorio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from BadOS_Screen import Screen
from BadOS_Buttons import Buttons

# constants
WHITE = 0xFFFFFF
BLACK = 0x000000

DIGITS_TEXT = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
TENS_TEXT = ['', 'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

# convert hour to 12hr format if is12hr true
twelve_hr = lambda h, is12hr: (h - 12 if h > 12 else h) if h > 0 else 12 if is12hr else h

# return am/pm if 12hr format
am_pm = lambda ts, is12hr: 'p.m.' if int(ts.split(':')[0]) > 11 else 'a.m.' if is12hr else ''

# convert two-digit number to text string
def number_text(n):
	return DIGITS_TEXT[n] if n < 20 else TENS_TEXT[n // 10] + ( '-' + DIGITS_TEXT[n % 10] if n % 10 > 0 else '')

# convert time string (nn:nn) to text string
# returns 12hr format if disp_12hr else 24hr format
def time_text(ts, disp_12hr):
	return number_text(twelve_hr(int(ts.split(':')[0]), disp_12hr)) + ' ' + \
           ('' if (int(ts.split(':')[1]) == 0) else (number_text(int(ts.split(':')[1])) + ' ')) + \
           am_pm(ts, disp_12hr)
	
# friendly time text string
def friendly_time(ts, disp_12hr):
	# TODO: quarter til, half past, nearest 5 min, etc.
	return 

# get current time as string ('hh:mm:ss')
# deltas for hours and minutes to allow setting time
def get_current_time(hour_delta, min_delta, sec_delta):
    seconds = time.monotonic() + ((hour_delta * 60) + min_delta) * 60 + sec_delta
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return "%d:%02d:%02d" % (hour, min, sec)
	

#   m a i n

# initialize display
scr = Screen()
white_background = vectorio.Rectangle(pixel_shader=scr.palette, width=scr.display.width+1, height=scr.display.height, x=0, y=0)
title = label.Label(font=terminalio.FONT, text='Clock', color=BLACK, scale=2)
title.x, title.y = 60, 20
scr.value.append(white_background)
#scr.screen.append(title)

# create buttons object
btns = Buttons()

# create hours, minutes and seconds deltas for setting time
# TODO: fix for complete 
hour_delta = 0
min_delta = 0
sec_delta = 0

# loop displaying the time
end_requested = False
auto_end_count = 1000
while not end_requested:
    now = get_current_time(hour_delta, min_delta, sec_delta)
    print(f'{now}\n')
    print(f'the 12hr time is\n{time_text(now, True)}\n')
    print(f'the 24hr time is\n{time_text(now, False)}\n')
    time_number = label.Label(font=terminalio.FONT, text=now, color=BLACK, scale=3)
    time_number.x, time_number.y = 10, 15
    timeis_label = label.Label(font=terminalio.FONT, text="the time is:", color=BLACK, scale=2)
    timeis_label.x, timeis_label.y = 10, 50
    time_txt = label.Label(font=terminalio.FONT, text=time_text(now, True), color=BLACK, scale=2)
    time_txt.x, time_txt.y = 10, 75
    seconds_txt = label.Label(font=terminalio.FONT, text='and ' + number_text(int(now[-2:])) + ' seconds', color=BLACK, scale=2)
    seconds_txt.x, seconds_txt.y = 10, 100
    scr.value.append(time_number)
    scr.value.append(timeis_label)
    scr.value.append(time_txt)
    scr.value.append(seconds_txt)
    scr.render()
    just_refreshed = True
    # after render, remove time fields from screen object for next refresh
    for i in range(4):
        scr.value.pop()
    # wait 10 seconds for next refresh checking buttons for clicks while waiting
    waiting = True
    while waiting:
        now = get_current_time(hour_delta, min_delta, sec_delta)
        if now[-1:] == '0':
            if not just_refreshed:
                waiting = False
        else:
            just_refreshed = False
        # check if button clicked to update time or end program    
        btn_index = btns.states_index()
        if btn_index != -1:
            # button click detected
            if btn_index == 3 or btn_index == 4:
                # up/down arrows clicked, end program
                waiting = False
                end_requested = True
            elif btn_index == 0:
                # a button clicked; increment hours
                hour_delta = (hour_delta + 1) % 24
            elif btn_index == 1:
                # b button clicked; increment minutes
                min_delta = (min_delta + 1) % 60
            elif btn_index == 2:
                # c button clicked; reset seconds to 00
                sec_delta = -(int(now[-2:]) - sec_delta)
            # wait for button release
            while(btns.states_index() != -1):
                time.sleep(0.05)
        # prevent spinning while waiting
        time.sleep(0.05)
    # auto end
    auto_end_count -= 1
    if auto_end_count == 0:
        end_requested = True
    print('auto_end count: ', auto_end_count)

# return to the menu
supervisor.reload()




#   B O N E Y A R D

'''
# test routine
for n in range(100):
    print(number_text(n))
'''

# now = time.strftime("%H:%M:%S", time.localtime())	
'''
    hour = (hour + hour_delta) % 24
    min = (min + min_delta) % 60
    sec = (sec + sec_delta) % 60
'''