# Introduction

"Mobicam" is a Raspberry Pi python-based device for monitoring 
motion and, when activated, taking pictures.  It was designed
to be "mobile" in the sense that it can be easily move to different
locations in a house.  It can run on batteries for about 6
hours.

# Directory Contents


# Hardware

* Raspberry Pi - I'm using a Raspberry Pi 1 Model B.  Any model
should work, but the STL files I have include a board with bolt
holes designed to line up with
  * https://www.adafruit.com/products/998
* PIR Sensor - used for motion detection
  * https://www.adafruit.com/products/189
* LED's - three, each used for indicating state and when
* Camera - night vision camera with built-in infrared LEDs
  * https://amzn.com/B00N9YWLHE
* Battery
  * https://www.adafruit.com/products/353
* Battery Charger and Power Supply
  * https://www.adafruit.com/products/2465
* Wiring -
  * https://www.adafruit.com/products/266
* Power Button -
* Enclosure - See the included STL files

# Software

The software for this project is composed of two short python
files.  One file (mobicam.py) is the file that's actually run.
When executed, it creates a few different things:

* Web Server -
* Internal state -
* LED State -
* Scheduler -

The second file contains a set of callbacks.  If none is specified
from the command line, it used a default that's included with the
repo.  However, you probably want to do other things that just save
the pictures and print out when motion is detected.  So you can
write your own callback file and specify it on the command line
when running the software.  Then it will use your callbacks rather
than using the one that's included.  This also makes it easy to use
the scripts in this repo directly while still allowing you to write
your own behavior.

