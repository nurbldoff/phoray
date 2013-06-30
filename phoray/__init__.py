from numpy import array

DEBUG = True


def debug(*args):
    if DEBUG:
        print(args)


def Position(*args):
    print "Position", args
    if len(args) == 1:
        if isinstance(args[0], dict):
            return array((args[0]["x"], args[0]["y"], args[0]["z"]))
        else:
            return array(args[0])
    elif len(args) == 3:
        return array(args)


def Rotation(x, y, z):
    return array((x, y, z))


class Length(float):
    pass
