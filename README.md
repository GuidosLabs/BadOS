# BadOS
## *Badge Operating System for Pimoroni Badger2040 Electronic Badge Using CircuitPython*

![BadOS](https://github.com/GuidosLabs/BadOS/blob/main/CIRCUITPY/assets/images/BadOS-120.bmp)

![BadOS_Image](https://github.com/GuidosLabs/BadOS/blob/main/ACE8A8C5-8EA8-4D8F-9D72-653DC783588A.jpeg)
## Overview

The default installation for the Badger2040 is MicroPython, but since CircuitPython offers an easier and more user-friendly system for designing custom applications, it was chosen for this system. The inspiration for this mini-OS / launcher came from both the original MicroPython version as well as a CircuitPython version created by BeBoX. 

Since this is a major restructure and rewrite of both systems, it was decided to create an entirely new repo rather than a fork of either of those systems; but since BadOS retains some of the look and feel of those systems and uses some of their code in several areas, it's only appropriate to give proper credit to both of those systems.

A good resource for learning about the badge and starting with the original MicroPython system can be found at Pimoroni with this link:
https://learn.pimoroni.com/article/getting-started-with-badger-2040


- - - -


## Installation of CircuitPython and BadOS

The installation consists of two very simple steps.
  1. Replace the badge's MicroPython system with CircuitPython.
  2. Install the BadOS system onto the badge.

### Replacing the MicroPython system with CircuitPython.

The Badger2040 hardware/firmware design makes this very easy. First, download the latest version of CircuitPython for this hardware from the following link. It will be a file with the .UF2 extension.
https://circuitpython.org/board/pimoroni_badger2040/

Then plug the badge into a USB port. Locate the two small buttons on the back of the badge at the top. While holding the button labeled 'boot/usr', press the nearby Reset button labeled 'rst'. The badge will reset, make a USB connection and expose part of its storage as a flash drive named 'RPI-RP2'. Simply copy (or click-drag) the downloaded CircuitPython .UF2 file onto the root directory of this drive (alongside the .HTM and .TXT files). Once the UF2 file is in place, just press the Reset button again and the badge firmware will install CircuitPython. That completes step one!

### Install BadOS

Download the files from this repo.
After CircuitPython is installed and the badge has been restarted by pressing only the Reset button, it will expose a different partition of its storage as a new flash drive called 'CIRCUITPY'.

Copy all of the files/directories from the CIRCUITPY directory of this repo onto the root CIRCUITPY directory on the badge. At that point, the directory on the badge should have 'main.py' and three folders named 'apps', 'assets' and 'lib'.  That completes step two! 

Your badge should now be ready to go. Just press Reset to restart it with BadOS running on CircuitPython.


- - - -


## BadOS Directory Structure

The 'main.py' Python program in the root directory is the main launcher program for BadOS. 

The 'apps' directory is where the launcher finds all of the application programs for the user to select. All sub-directories contain a single application listed in the launcher menu.

The 'assets' directory contains three sub-dirs with various fonts, icons and images used by the system.

The 'lib' directory is where the libraries to assist with using the hardware and the BadOS functions are stored.


- - - -


## Applications

* BADGE - This is the main function of the badge hardware. It allows you to customize and display a badge with your own image and information.

* CLOCK - Digital and text clock.

* D20 - Random roll of a D20 die.

* DEMO -  Demonstration of graphics.

* EBOOK - Read an electronic book.

* FRAC -  Generate a fractal graphic of a section of the Mandelbrot set.

* IMAGE - Select and display bitmaps.

* INFO -  Information about the badge hardware and BadOS.

* KEYBD - Emulate a keyboard when connected to USB.

* PREFS - Preferences. Select the keyboard language country (France or USA).

* THERML - Future program to support capture and display of real-time images from a thermal camera accessory for the badge. 

* WORLD - Generate and show simple world map graphic.


- - - -

## Customizing the Badge Layout

To customize a badge with your information, you need to create a text file with your info and a bitmap of the image to display.  The bitmap needs to be a valid .bmp file with a black/white single-bit depth palette 104 pixels wide by 128 high or smaller.

In the /badge directory are several example badges. The easiest option is to duplicate or rename one of those directories and the included files to whatever name you like, and change the data in the corresponding .txt file to your information. Some of those fields are displayed on the badge, others are used to create a vcard QR code so you can easily provide your contact information to anyone with a smartphone camera.


- - - -

## Custom Applications

To add a custom application, simply create a new folder in 'apps' named for your application. Since space is limited on the menu screen of the badge, any application named more than 6 characters is truncated, so keep that in mind when you name your application. 

Within your new application folder, create two files with the same name as your application but with extensions '.bmp' and '.py'. These will be used by the launcher to create the icon for your application in the menu and for your Python program that will be launched. If the launcher doesn't find a '.bmp', it will use a default icon for your app.


- - - -


## Libraries

The best way to see the various functions that are available in the libraries is to review the code for the main.py launcher and the various apps to see how they're imported and used. 


- - - -


## Issues and Work-In-Process

The Keybd app is currently not operational and is also being rewritten. At that point, it will include the HID capability.

The Ebook app does a simple line-wrap of the text without regard to any words which are split. It also needs to handle some special characters which currently perform line-feeds and other control functions at inappropriate locations. This will be fixed soon.

The Therml app is a future application requiring hardware which is currently not available.

Documentation explaining how to use the BadOS library functions for Screen, Buttons, Menu and other capabilities is being written and should be available here soon. Until then, you can at least see how they are used in the various sample applications. 

Thank you for your patience! I hope you enjoy using BadOS.



