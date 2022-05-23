'''
    BadOS_Buttons
    Common Button Handling Functions for BadOS
    David Guidos, May 2022
'''

__version__ = "1.0.0"
__repo__ = "https://github.com/guidoslabs/BadOS.git"

import time
import board, microcontroller, storage, supervisor
from digitalio import DigitalInOut, Direction, Pull

class Buttons:

    def __init__(self):
        # initialize buttons and LED
        # buttons go True when pressed
        self.a = DigitalInOut(board.SW_A)
        self.a.direction = Direction.INPUT
        self.a.pull = Pull.DOWN
        self.b = DigitalInOut(board.SW_B)
        self.b.direction = Direction.INPUT
        self.b.pull = Pull.DOWN
        self.c = DigitalInOut(board.SW_C)
        self.c.direction = Direction.INPUT
        self.c.pull = Pull.DOWN
        self.up = DigitalInOut(board.SW_UP)
        self.up.direction = Direction.INPUT
        self.up.pull = Pull.DOWN
        self.down = DigitalInOut(board.SW_DOWN)
        self.down.direction = Direction.INPUT
        self.down.pull = Pull.DOWN
        self.user = board.USER_SW
        self.led = DigitalInOut(board.USER_LED)
        self.led.direction = Direction.OUTPUT

    # wait for button click and return index of button (0,1,2 for a,b,c; 4,5 for up,down)
    def await_click(self):
        clicked = False
        self.led.value = 0   # awaiting click; activity LED off
        while not clicked:
            bs = self.states()
            clicked = any(bs)
            # prevent spinning    TODO: sleep mode to save energy?
            time.sleep(0.01)
        return bs.index(True)

    # state of all buttons [a,b,c,up,down]
    def states(self):
        states = [self.a.value, self.b.value, self.c.value, self.up.value, self.down.value]
        return states

    # index of clicked button
    def states_index(self):
        bs = self.states()
        return bs.index(True) if True in bs else -1


