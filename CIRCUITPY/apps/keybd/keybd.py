'''
keyboard app
By David Guidos, May 2022
Inspired by the Pimoroni Badger2040 badge, AdaFruit and BeBox???
'''
import gc, os , math, microcontroller, digitalio, board, storage
import analogio, time, usb_hid
from adafruit_hid.keyboard import Keyboard
import adafruit_ducky, busio, displayio , terminalio , vectorio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
import adafruit_miniqr

def fixlayout(lang):
    global usb, keyboard, keyboard_layout
    print("fixlayout usb =", end='')
    print(usb)
    try:
        keyboard = Keyboard(usb_hid.devices)
        usb=True
    except:
        usb=False
    layout=lang
    if usb==True:
        keyboard = Keyboard(usb_hid.devices)
        if lang=="fr": 
            from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
            keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
            
        else:
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
            keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
        #usb=True
        #print(usb)
    else:
        print("not connected on usb")
        #usb=False
    return usb
    #print(tomem[0:2] + " / " + lang + "/" + layout)
        
def callduck(filename):
    if usb==True:
        duck = adafruit_ducky.Ducky(filename, keyboard, keyboard_layout)    
        result = True
        while result is not False:
            result = duck.loop()
    else:
        result = "No usb"
    return result

#   m a i n

try:
    keyboard = Keyboard(usb_hid.devices)
    usb=True
except:
    usb=False
flag=False
#HID init

try :
    layout = microcontroller.nvm[0:2].decode() # 2 chars form nvm memory index 0
    #layout = layout.decode().strip()
    #print("Find "+layout+" in mémory")
except:
    layout = "fr" # fr or us fixed value if no data in memory
#print("Keyboard layout :"+layout)
try:    
    if usb==True:
        keyboard = Keyboard(usb_hid.devices)
        if layout=="fr": 
            from adafruit_hid.keyboard_layout_fr import KeyboardLayoutFR
            keyboard_layout = KeyboardLayoutFR(keyboard)  # We're in France :)
            
        else:
            from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
            keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
except:
    print("error")



# scan files for HID scripts 
ListHIDFiles = os.listdir("/apps/keyboard/hid/")
hidfiles =[]
count = 0
for n in ListHIDFiles:
    if n[-4:]==".txt":
        if n[0:2]!="._":
            hidfiles.append((n.replace(".txt",""),count))
            count=count+1
hidfiles.append(("EXIT",count))


