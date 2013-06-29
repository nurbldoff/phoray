from numpy import array

DEBUG = True


def debug(*args):
    if DEBUG:
        print(args)


def Vec(x, y, z):
    return array((x, y, z))


def Position(x, y, z):
    return array((x, y, z))


def Rotation(x, y, z):
    return array((x, y, z))


class Length(float):
    pass
