from libc.math cimport sqrt

cimport numpy as np
import numpy as np


cpdef np.ndarray quadratic(double a, double b, double c):
    """
    Solve a quadratic function a*x**2 + b*y + c = 0
    """
    cdef double delta, x1, x2

    if a == 0.:
        if b == 0.:
            raise ValueError
        else:
            x1 = -c / b
            return x1, x1
    delta = b ** 2 - 4 * a * c
    x1 = (-b + sqrt(delta)) / (2 * a)
    x2 = (-b - sqrt(delta)) / (2 * a)
    return np.array((x1, x2))
