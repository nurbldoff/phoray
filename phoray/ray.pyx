from __future__ import division
#from minivec import Vec, Mat
#from vector cimport Vector
#from vector import Vector
from numpy import array
cimport numpy as np

cdef class Ray:
    """
    A ray is defined by its endpoint P0 Vector(X0,Y0,Z0) and its
    "direction cosines", a vector(k,l,m).

    The vector equation of the line through points A and B is given by
    r = OA + tAB (where t is a scalar multiple)

    If a is vector OA and b is vector OB, then the equation of the
    line can be written: r = a + t(b - a)
    """

    def __init__(self, origin=array((0, 0, 0)), direction=array((0, 0, 1)),
                 wavelength=1):
        self.endpoint = origin
        self.direction = direction
        self.wavelength = wavelength

    cpdef Ray translate(self, np.ndarray v):
        """Parallel movement of the Ray by vector v.
        Endpoint is moved, direction unchanged."""
        return Ray(self.endpoint + v, self.direction, self.wavelength)

    cpdef Ray rotate(self, np.ndarray dtheta):
        """Rotate the Ray around the x, y, and z axes by angles
        theta_x, theta_y and theta_z
        """
        return Ray(self.endpoint, self.direction.rotate(dtheta),
                   self.wavelength)

    def __repr__(self):
        return "Ray(%s, %s)" % (self.endpoint, self.direction)

    cpdef np.ndarray along(self, double dist):
        """Return a position along the ray."""
        return self.endpoint + self.direction * dist
