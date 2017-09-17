from __future__ import print_function
import sys
import netifaces
import string
from astral import Astral
from datetime import datetime

def sunrise_sunset(city_name, which_day=datetime.now()):
    """Get the Sunrise and sunset for the given city

    Uses the astral library (from Pip).
    
    Arguments
    =========
    city_name - must be a city that astral knows about
    which_date - datetime object for the day of interest.  By default, uses the current date
    """
    s =  Astral()[city_name].sun(which_day, local=True)
    return [s["sunrise"], s["sunset"]]

def eprint(*args, **kwargs):
    """Print to stderr

    Follows the python 3 convention for the
    print function.  This is a convenience function
    for making code shorter.

    Taken from: http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    """
    print(*args, file=sys.stderr, **kwargs)

def my_mac(interface="wlan0"):
    """Get the mac address for the specified interface.
    
    Arguments
    =========
    interface - the network interface of interest
    """
    return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']    

def is_printable(s):
    """Returns whether a string contains only printable characters

    Arguments
    =========
    s - the string to test
    """
    return all(c in string.printable for c in s)

def force_printable(s):
    """Make a printable string from the provied string.

    If s only contains printable characters, return s.  If not,
    return a "string_escape" encoded version of the string.
    """
    return s if is_printable(s) else s.encode("string_escape")

def cls(num_lines=100):
    """Clear the screen by printing n lines
    """
    print ("\n"*num_lines)
