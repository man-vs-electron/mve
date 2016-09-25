"""Sample (and default) set of callbacks for mobicam.

Provides a simple set of callbacks for mobicam and 
an example that can be expanded and customized.
"""

import os
import sys
import time
import datetime
import picamera

pic_path = os.path.join(os.path.expanduser("~"), "mobicam_pics")
if not os.path.exists(pic_path):
        os.makedirs(pic_path)
camera = picamera.PiCamera()

def take_picture():
    fname = os.path.join(pic_path, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg"))
    camera.capture(fname)
        
def init(state):
    """Called when setting up before any of the other methods"""
    print "Initializing"

def motion_start():
    """Called when motion starts"""
    print "Motion Started"

def motion_end(duration):
    """Called when motion ends, along with the duration in seconds"""
    print "Motion ended at %s" % duration

def http_get(path):
    """Called when the http server is accessed."""
    print "Path: %s" % path
    
def on_timer():
    """Called every 30 minutes"""
    print "Timer went off.  Take a picture!"

def motion_while_monitoring():
    """Called repeatedly when the system is monitoring and motion detected"""
    print "Danger, Will Robinson!"
    take_picture()
