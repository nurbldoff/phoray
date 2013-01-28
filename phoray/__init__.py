from minivec import Vec

DEBUG = True


def debug(*args):
    if DEBUG:
        print(args)


Position = Vec
Rotation = Vec
Length = float
