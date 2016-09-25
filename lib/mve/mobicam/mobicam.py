"""Script for running mobicam.

Initializes all variables, the state object,
and starts the main loop.  Mobicam's behavior 
can be configured by creating a new module
with the following global and then invoking this
script from the command line with the name of
the module:

init(state)
motion_start()
motion_end(duration)
http_get(path)
on_time()
motion_while_monitoring()

mobicam features a web server for communicating
with it externally and a 30 minute periodic
timer.

"""
import sys
import logging
import time
import datetime
import threading
import requests
import importlib
import RPi.GPIO as GPIO
from apscheduler.scheduler import Scheduler
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

#################################################################
# define and setup the GPIO and state variables

# Global Constants
MOTION_SENSOR_PIN = 24
RED_LED_PIN = 14
GREEN_LED_PIN = 15
YELLOW_LED_PIN = 18

class mobicam_state():
    """Object representing the state of mobicam.

    This class is instantiated by the module and passed on
    to the module containing the callbacks.
    """

    def __init__(self):
        """Set is_monitoring to false"""
        self.is_monitoring = False
        
    def lightState(self, light_pin, isOn):
        """Generic call to change light state"""
        GPIO.output(light_pin, GPIO.HIGH if isOn else GPIO.LOW)

    def redOn(self):
        self.lightState(RED_LED_PIN, True)

    def redOff(self):
        self.lightState(RED_LED_PIN, False)

    def greenOn(self):
        self.lightState(GREEN_LED_PIN, True)

    def greenOff(self):
        self.lightState(GREEN_LED_PIN, False)

    def yellowOn(self):
        self.lightState(YELLOW_LED_PIN, True)

    def yellowOff(self):
        self.lightState(YELLOW_LED_PIN, False)

    def currentMotion(self):
        '''Whether the motion sensor is currently seeing motion
        '''
        return GPIO.input(MOTION_SENSOR_PIN)

logging.basicConfig()

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
for pin in [RED_LED_PIN, GREEN_LED_PIN, YELLOW_LED_PIN]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin,GPIO.LOW)
GPIO.output(GREEN_LED_PIN, GPIO.HIGH)

_callbacks = importlib.import_module(sys.argv[1] if len(sys.argv)>1 and "-"!=sys.argv[1] else "mve.mobicam.default_callbacks")
_state = mobicam_state()
_callbacks.init(_state)

#################################################################
# define and setup the callback for motion detection

_motion_start_time = None

def _onMontionChange(channel):
    '''Callback for motion change

    This function will get called when wall-e detects
    either the start or end of motion
    '''
    global _motion_start_time
    global _state
    if _state.currentMotion():
        _motion_start_time = time.mktime(datetime.datetime.now().timetuple())
        report = 0
        _callbacks.motion_start()
    else:
        if _motion_start_time is None:
            report = 1
        else:
            report = time.mktime(datetime.datetime.now().timetuple()) - _motion_start_time
            if report==0:
                report = 1
            _motion_start_time=None
        _callbacks.motion_end(report)

# Register the callback
GPIO.add_event_detect(MOTION_SENSOR_PIN, GPIO.BOTH, callback=_onMontionChange, bouncetime=200)

#################################################################
# define and setup the scheduler

_sched = Scheduler()
_sched.start()

@_sched.interval_schedule(minutes=30)
def _on_timer():
    _callbacks.on_timer()

#################################################################
# define and setup the http servers for controlling the device
    
class _MobicamHandler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write("Message Received !")
        if self.path.lower().endswith("start"):
            _state.is_monitoring = True
            _state.redOn()
            _state.greenOff()
        if self.path.lower().endswith("stop"):
            _state.is_monitoring = False
            _state.redOff()
            _state.greenOn()
        _callbacks.http_get(self.path)
        
                
class _WebServerThread(threading.Thread):

    def run(self):
        server = HTTPServer(('', 8080), _MobicamHandler)
        print 'Started httpserver on port 8080'

        #Wait forever for incoming htto requests
        server.serve_forever()
                
#start the web server
_webThread = _WebServerThread()
_webThread.setDaemon(True)
_webThread.start()

#################################################################                        
# The basic loop. 

print "Starting.  Monitoring is %s" % _state.is_monitoring
while True:

    if _state.is_monitoring and _state.currentMotion():
        _callbacks.motion_while_monitoring()
    time.sleep(1)

