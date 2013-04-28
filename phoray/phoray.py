from __future__ import division
from itertools import count

DEBUG = False
current_id = count()

def debug(*args):
    if DEBUG:
        print(args)
