from minivec import Vec

DEBUG = True


def debug(*args):
    if DEBUG:
        print(args)


class Position(Vec):
    pass


class Rotation(Vec):
    pass


class Length(float):
    pass
