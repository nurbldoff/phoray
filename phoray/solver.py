from math import *


def quadratic(a, b, c, no_complex=True):
    """
    Solve a quadratic function a*x**2 + b*y + c = 0
    """
    if a == 0.:
        if b == 0.:
            return None
        else:
            x1 = -c / b
            return x1, x1
    delta = b ** 2 - 4 * a * c
    try:
        x1 = (-b + sqrt(delta)) / (2 * a)
        x2 = (-b - sqrt(delta)) / (2 * a)
    except ValueError:
        if no_complex:
            return None
        else:
            x1 = complex(0, -b + sqrt(-delta)) / (2 * a)
            x2 = complex(0, -b - sqrt(-delta)) / (2 * a)
    return x1, x2
