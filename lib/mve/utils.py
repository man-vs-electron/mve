from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    """Print to stderr

    Follows the python 3 convention for the
    print function.  This is a convenience function
    for making code shorter.

    Taken from: http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    """
    print(*args, file=sys.stderr, **kwargs)
