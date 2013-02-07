from __future__ import division
from math import *

from member import Member
from surface import Surface
from minivec import Vec, Mat
from ray import Ray

# base_schema = [("position", {"type": "position"}),
#                ("rotation", {"type": "rotation"}),
#                ("offset", {"type": "position"}),
#                ("alignment", {"type": "rotation"}),
#                ("geometry", {"type": "geometry"})]


class Element(Member):

    def __init__(self, geometry=Surface(),
                 position=Vec(0, 0, 0), rotation=Vec(0, 0, 0),
                 offset=Vec(0, 0, 0), alignment=Vec(0, 0, 0)):
        self.geometry = geometry
        Member.__init__(self, position, rotation, offset, alignment)
        self.footprint = []

    def propagate(self, ray):
        """
        Takes a ray in global coordinates and returns the ray that
        results from interacting with the surface (e.g. reflection)
        """
        new_ray = self._propagate(ray)
        if new_ray is not None:
            self.footprint.append({"x": new_ray.endpoint.x,
                                   "y": new_ray.endpoint.y})
        return new_ray


class Mirror(Element):

    #schema = OrderedDict(base_schema)

    def _propagate(self, ray):

        if ray is not None:
            ray0 = self.localize(ray)
            reflected_ray = self.geometry.reflect(ray0)
            if reflected_ray is None:
                return None
            else:
                return self.globalize(reflected_ray)
        else:
            return None


class Detector(Element):

    # schema = OrderedDict(base_schema)

    def _propagate(self, ray):
        if ray is not None:
            ray0 = self.localize(ray)
            pos = self.globalize_vector(self.geometry.intersect(ray0))
            return Ray(pos, Vec(0, 0, 0), ray.wavelength)
        else:
            return None


class ReflectiveGrating(Element):

    """A reflective grating."""

    # schema = OrderedDict([("d", {"type": "length"}),
    #                       ("order", {"type": "number"})] + base_schema)

    def __init__(self, d=0, order=0, *args, **kwargs):
        """
        Define a reflecting element with geometry shape given by s. If
        d>0 it will work as a grating with line spacing d and lines in
        the xz-plane and diffraction order given by order. Otherwise
        it works as a plain mirror.
        """
        self.d = d
        self.order = order
        print "Mirror", args, kwargs
        Element.__init__(self, *args, **kwargs)

    def _propagate(self, ray):

        if ray is not None:
            ray0 = self.localize(ray)
            diffracted_ray = self.geometry.diffract(
                ray0, self.d, self.order)
            if diffracted_ray is None:
                return None
            else:
                return self.globalize(diffracted_ray)
        else:
            return None


class ReflectiveVLSGrating(Mirror):

    """A grating with varying line spacing. Not complete."""

    # schema = OrderedDict([("an", {"type": "length"})] + base_schema)

    def __init__(self, an=1.0, *args, **kwargs):
        self.an = an
        Mirror.__init__(self, *args, **kwargs)

    def get_line_distance(self, p):
        """
        Returns the local grating line density according to VLS
        parameters a(x) = a_0 + a_1*x + ... + a_n*x^n where x is the
        distance to the grating center.
        """

        y = 1000 * p.y
        R = 1000 * self.geometry.R
        x = copysign(sqrt(y ** 2 + (R - sqrt(R ** 2 - y ** 2))), y)
        x = 2 * R * asin(x / (2 * R))
        #x=y
        b = -x / sqrt(R ** 2 - x ** 2)
        theta = atan(b)  # grating tangent angle
        print b, theta
        d = 0
        for n, a in enumerate(self.an):
            d += a * x ** n
        d *= cos(theta)
        return 1e-3 / d

    def _propagate(self, ray):

        if ray is not None:
            ray0 = self.localize(ray)
            diffracted_ray = self.geometry.diffract(ray0, None, self.order,
                                                    self.get_line_distance)
            if diffracted_ray is None:
                return None
            else:
                return self.globalize(diffracted_ray)
        else:
            return None


class Glass(Element):

    """A glass surface, defined by the refraction indices on each side."""

    # schema = OrderedDict([("index1", {"type": "number", "value": 1.0}),
    #                       ("index2", {"type": "number", "value": 1.0})] +
    #                      base_schema)

    def __init__(self, index1=1.0, index2=1.0, *args, **kwargs):
        self.index1 = index1
        self.index2 = index2
        Element.__init__(self, *args, **kwargs)

    def _propagate(self, ray):

        if ray is not None:
            ray0 = self.localize(ray)
            refracted_ray = self.geometry.refract(ray0, self.index1,
                                                  self.index2)
            if refracted_ray is None:
                return None
            else:
                return self.globalize(refracted_ray)
        else:
            return None
