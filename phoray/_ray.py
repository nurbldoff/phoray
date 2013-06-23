from __future__ import division
from minivec import Vec, Mat


class Ray(object):
    """
    A ray is defined by its endpoint P0 Vector(X0,Y0,Z0) and its
    "direction cosines", a Vector(k,l,m).

    The vector equation of the line through points A and B is given by
    r = OA + tAB (where t is a scalar multiple)

    If a is vector OA and b is vector OB, then the equation of the
    line can be written: r = a + t(b - a)
    """

    def __init__(self, origin=Vec(0, 0, 0), direction=Vec(0, 0, 1),
                 wavelength=1):
        self.endpoint = origin
        self.direction = direction
        self.wavelength = wavelength

    def translate(self, v):
        """Parallel movement of the Ray by vector v.
        Endpoint is moved, direction unchanged."""
        return Ray(self.endpoint + v, self.direction, self.wavelength)

    def deviate(self, dtheta):
        """Rotate the Ray around the x, y, and z axes by angles
        theta_x, theta_y and theta_z
        """
        rotation = Mat().rotate(dtheta)
        return Ray(self.endpoint, self.direction.transformDir(rotation),
                   self.wavelength)

    def __repr__(self):
        return "Ray(%s, %s)" % (self.endpoint, self.direction)

    def along(self, dist):
        """Return a position along the ray."""
        return self.endpoint + self.direction * dist
