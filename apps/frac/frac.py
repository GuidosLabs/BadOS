'''
    frac.py
    BadOS Fractal Demo App
    David Guidos, May 2022
'''
import time
import random
import supervisor
import displayio, terminalio, vectorio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

from BadOS_Screen import Screen, Progress_Indicator
from BadOS_Buttons import Buttons

WHITE = 0xFFFFFF
BLACK = 0x000000

# Mandelbrot fractal evaluation function
def mandelbrot_iteration_value(c, max_iterations):
    ca, cb = c
    za, zb = ca, cb
    for n in range(max_iterations):
        if za ** 2 + zb ** 2 > 4:
            return n
        za, zb = za * za - zb * zb + ca, 2 * za * zb + cb
    return max_iterations

# generate full-screen Mandelbrot set fractal
def fractal(xr, yr, max_iterations):
    # create the fractal
    fractal_bitmap = displayio.Bitmap(scr.WIDTH, scr.HEIGHT, 2)
    fractal_palette = scr.palette

    xmin, xmax = xr
    ymin, ymax = yr

    for x in range(scr.WIDTH):
        ca = (x - 0) / ((scr.WIDTH - 1) - 0) * (xmax - xmin) + xmin       # converted x range 
        for y in range(scr.HEIGHT):
            cb = (y - 0) / ((scr.HEIGHT - 1) - 0) * (ymax - ymin) + ymin  # converted y range 
            fractal_bitmap[x, y] = 1 if mandelbrot_iteration_value((ca, cb), max_iterations) < random.randint(0, max_iterations) else 0
        percent_complete = x / scr.WIDTH * 100
        if x % 60 == 0: update_progress(percent_complete)
    fractal_tile_grid = displayio.TileGrid(fractal_bitmap, pixel_shader=fractal_palette)
    return fractal_tile_grid

# update progress indicator
def update_progress(percent_complete):
    progress_bar = progress.bar(percent_complete)
    scr.value.append(progress_bar)
    scr.render()
    scr.value.pop()

#   m a i n   

# initialize display
scr = Screen()
title = label.Label(font=terminalio.FONT, text='Creating Fractal Image...', color=BLACK, scale=1)
title.x, title.y = 70, 40
scr.value.append(title)

# set up buttons
btns = Buttons()

progress = Progress_Indicator(90, 70, 100, 15, 1)
update_progress(0)

# full mandelbrot set range
#xmin, xmax = -3.0, 0.5
#ymin, ymax = -1.2, 1.2

# interesting
# from experimenting on https://math.hws.edu/eck/js/mandelbrot/MB.html

#   <xmin>-0.995207981249999992472</xmin>
#   <xmax>-0.995110446874999992472</xmax>
#   <ymin>0.294174462500000000010</ymin>
#   <ymax>0.294246553125000000010</ymax>
#xmin, xmax = -0.99520798125, -0.995110446875
#ymin, ymax = 0.2941744625, 0.2942465531250

# <limits>
#    <xmin>-0.632000000000000001700</xmin>
#    <xmax>-0.396000000000000007600</xmax>
#    <ymin>0.520000000000000000000</ymin>
#    <ymax>0.696000000000000000000</ymax>
# </limits>
xmin, xmax = -0.532, -0.396
ymin, ymax = 0.52, 0.696

# TODO: add button options to select alternate ranges

max_iterations = 200
fractal_tile_grid = fractal((xmin, xmax), (ymin, ymax), max_iterations)
# remove the status bar
scr.status_bar_visible = False
# add the fractal image
scr.value.append(fractal_tile_grid)
# display the fractal
scr.render()

# loop until timeout or arrow button clicked
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
supervisor.reload()



#   b o n e y a r d

'''
# Mandelbrot using complex numbers    
def is_stable(c, max_iterations):
    z = 0
    for _ in range(max_iterations):
        z = z ** 2 + c
        if abs(z) > 2:
            return False
    return True
'''

# range conversion formula
# new_value = ( (old_value - old_min) / (old_max - old_min) ) * (new_max - new_min) + new_min

