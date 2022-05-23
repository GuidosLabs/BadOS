'''
    d20.py
    Random D20 Die Rolling Program
    David Guidos, May 2022
'''

import os, time
import math, random
import board, supervisor
import displayio, terminalio, vectorio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.triangle import Triangle

from BadOS_Screen import Screen
from BadOS_Buttons import Buttons

WHITE = 0xFFFFFF
BLACK = 0x000000

# d20 triangle mesh routines

# translate mesh position
t = lambda xy, p:(int(xy[0] + p[0]), int(xy[1] + p[1]))

def die_triangle(n, p0, p1, p2):
    tp = (120, 90)  # location of vertex a of main triangle on the display
    triangle = displayio.Group()
    triangle_lines = Triangle(t(p0, tp)[0], t(p0, tp)[1], t(p1, tp)[0], t(p1, tp)[1], t(p2, tp)[0], t(p2, tp)[1], outline=0x000000)
    triangle.append(triangle_lines)
    if n > 0:
        die_number = label.Label(scr.fonts[1], text=str(n), color=BLACK, scale=1)
        die_number.x, die_number.y =  int((t(p0, tp)[0] + t(p2, tp)[0]) / 2 - (4 if n < 10 else 9 * die_number.scale)), int((t(p0, tp)[1] + t(p1, tp)[1]) / 2 + 12 / 2)
        triangle.append(die_number)
    return triangle

def d20_graphic(n, size):
    # D20 die numbers layout
    # a edge is the bottom of the triangle for each number
    # b edge is the left side of each trianels
    # c edge if the right side
    d20_layout = {
		1: ['13a', '7a', '19a'],
		2: ['20b', '12a', '18a'],
		3: ['19b', '17c', '16c'],
		4: ['14b', '18c', '11c'],   
		5: ['13c', '18b', '15b'],
		6: ['14c', '9b', '16b'],
		7: ['1b', '15a', '17a'],
		8: ['20a', '16a', '10a'],
		9: ['19c', '6b', '11b'],	
		10: ['8c', '17c', '12b'],
		11: ['13b', '9c', '4c'],
		12: ['2b', '10c', '15c'],
		13: ['1a', '11a', '5a'],
		14: ['20c', '4a', '6a'],
		15: ['7b', '5c', '12c'],
		16: ['8b', '6c', '3c'],
		17: ['7c', '10b', '3b'],
		18: ['2c', '5b', '4b'],
		19: ['1c', '3a', '9a'],
		20: ['8a', '2a', '14a']
    }	
    # constants
    COS_30 = math.cos(math.radians(30))
    SIN_30 = math.sin(math.radians(30))
    SIN_60 = math.sin(math.radians(60))
    # calculate vertex positions
    # equilateral triangle vertices
    s = size
    si = s * SIN_60
    a = (0, 0)
    b = (s / 2, -si)
    c = (s, 0)
    d = (s / 2, si * 2/3) # bottom tip
    sii = si * (1 + 2/3)
    e = (s - COS_30 * sii, -SIN_30 * sii) # left tip
    f = (COS_30 * sii, -SIN_30 * sii) # right tip
    siii = si * 1/3
    g = (a[0] - siii * COS_30, a[1] + siii * SIN_30) # left bottom tip
    h = (s / 2, -(si + siii)) # top tip
    i = (c[0] + siii * COS_30, c[1] + siii * SIN_30) # right bottom tip
    # draw all the triangles
    d20 = displayio.Group()
    d20.append(die_triangle(n, a, b, c))
    # TODO: add other numbers rotated and skewed to fit their triangles using d20_layout
    n = 0
    d20.append(die_triangle(n, a, b, e))
    d20.append(die_triangle(n, b, c, f))
    d20.append(die_triangle(n, a, c, d))
    d20.append(die_triangle(n, a, d, g))
    d20.append(die_triangle(n, a, e, g))
    d20.append(die_triangle(n, b, e, h))
    d20.append(die_triangle(n, b, f, h))
    d20.append(die_triangle(n, c, f, i))
    d20.append(die_triangle(n, c, d, i))
    return d20

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

# set up buttons
buttons = Buttons()
buttons.led.value = 1  # turn on activity LED

# create screen
scr = Screen(background_color = WHITE, with_status_bar = False)

# select a random number and draw the die
game_over = False
while not game_over:
    buttons.led.value = 1  # turn on activity LED
    # select random number
    rn = random.randint(1, 20)
    print(f'Random d20 selection is {rn}')
    # draw the die
    scr.value.append(d20_graphic(rn, 50))
    # display the graphics
    scr.render()
    # after displaying, remove the die from the screen object in preparation for next update
    scr.value.pop()
    # loop until timeout or button clicked
    end_requested = False
    buttons.led.value = 0  # turn off activity LED
    start_time = time.monotonic()
    while not end_requested:
        bsi = buttons.states_index()
        if bsi == 3 or bsi == 4 or time.monotonic() > start_time + 60:
            # up or down clicked, or timeout
            end_requested = True
            game_over = True
        elif bsi > -1 and bsi < 3:
            # a, b, c button clicked
            # select another random number and redraw the die
            end_requested = True
        time.sleep(0.05)

# return to the system menu
buttons.led.value = 1  # turn on LED
supervisor.reload()



#   b o n e y a r d

'''

# determine the angles of each face starting with
# the selected number.
# eliminate any triangles with any vertex beyond 
# 90 degrees at the edge.
# remap all points within each active triangle.
# icosahedron dihedral angle = 138.19°

# print selected number (n) and touching triangles
n = 20	
print(n, d20[n])
for i in range(3):
	print(int(d20[n][i][0:-1]), d20[int(d20[n][i][0:-1])])

    # create image
    #width, height = 400, 400
    #d20_img = Image.new( mode = "RGB", size = (width, height))    #img = ImageDraw.Draw(d20_img)
	#img.polygon((t(p0), t(p1), t(p2)), outline=(255,255,255))


'''