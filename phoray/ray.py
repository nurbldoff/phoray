from __future__ import division
from numpy import array


class Rays(object):

    def __init__(self, endpoints, directions):
        self.endpoints = endpoints
        self.directions = directions

    def __repr__(self):
        return "%r, %r" % (self.endpoints, self.directions)


class Ray(object):
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

    # def translate(self, v):
    #     """Parallel movement of the Ray by vector v.
    #     Endpoint is moved, direction unchanged."""
    #     return Ray(self.endpoint + v, self.direction, self.wavelength)

    # def rotate(self, dtheta):
    #     """Rotate the Ray around the x, y, and z axes by angles
    #     theta_x, theta_y and theta_z
    #     """
    #     return Ray(self.endpoint, self.direction.rotate(dtheta),
    #                self.wavelength)

    def __repr__(self):
        return "Ray(%s, %s)" % (self.endpoint, self.direction)

    def along(self, dist):
        """Return a position along the ray."""
        return self.endpoint + self.direction * dist
