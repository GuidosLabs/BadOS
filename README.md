# BadOS
CircuitPython Mini Operating System for Pimoroni Badger2040 Electronic Badge

Overview

The default installation for the Badger2040 is MicroPython, but since CircuitPython offers an easier and more user-friendly system for designing custom applications it was chosen for this system. The inspiration for this mini-OS / launcher came from both the original MicroPython version as well as a CircuitPython version created by BeBox. 

Since this is a major restructure and rewrite of both systems, it was decided to create an entirely new repo rather than a fork of either of those systems; but since I retained some of the look and feel of those systems and used a portion of the code for particular portions of the design, I feel it appropriate to give proper credit to both of those systems.

A good resource for learning about the badge and starting with the original MicroPython system can be found at Pimoroni with this link:
https://learn.pimoroni.com/article/getting-started-with-badger-2040


Installation of BadOS on CircuitPython

The installation consists of two very simple steps.
  1. Relace the badge's MicroPython system with CircuitPython.
  2. Install BadOS system onto the badge.

Replacing the MicroPython system with CircuitPython.

The Badger2040 hardware/firmware design makes this very easy. First, download the latest version of CircuitPython for this hardware from the following link:
https://circuitpython.org/board/pimoroni_badger2040/

Then plug the badge into a USB port and press the Reset button on the back of the badge while first holding the adjacent User button. The badge will expose a partition of its storage as a flash drive named 'RPI-RP2'. Simply copy (or click-drag) the downloaded CircuitPython .UF2 file onto the root directory of this drive (alongside the .HTM and .TXT files). Once the UF2 file is in place, just press the Reset button and the badge firmware will install CircuitPython. That completes step one!

Install BadOS

Download the files from this repo (or from the .zip file).
After CircuitPython is installed and the badge has been restarted by pressing only the Reset button, it will expose a different partition of its storage as a new flash drive called 'CIRCUITPY'.

Copy all of the files/directories from the CIRTUITPY folder of this repo onto the root folder of CIRCUITPY on the badge. At that point, the root folder on the badge should have 'main.py' and three folders named 'apps', 'assets' and 'lib'.  That completes step two! 

Your badge should now be ready to go. Just press Reset to restart it with BadOS running on CircuitPython.



BadOS Directory Structure

The 'main.py' Python program in the root directory is the main launcher program for BadOS. 

The 'apps' directory is where the launcher finds all of the application programs for the user to select. 

The 'assets' directory contains three sub-dirs with various fonts, icons and images used by the system.

The 'lib' directory is where the libraries to assist with using the hardware and the BadOS functions are stored.



Applications

Badge - This is the main function of the badge hardware. It allows you to customize and display a badge with your own image and information.

Clock - This 



Custom Applications

To add a custom application, simply create a new folder in 'apps' named for your application. Since space is limited on the menu screen of the badge, any application named more than 6 characters is truncated, so keep that in mind when you name your application. 

Within your new application folder, create two files with the same name as your application but with extensions '.bmp' and '.py'. These will be used by the launcher to create the icon for your application in the menu and for your Python program that will be launched. If the launcher doesn't find a '.bmp', it will use a default icon for your app.


Libraries

The best way to see the various functions that are available in the libraries is to review the code for the main.py launcher and the various apps to see how they're imported and used. 



