from __future__ import division
from math import *
from collections import defaultdict

from member import Member
from surface import Surface
from minivec import Vec, Mat
from ray import Ray


class Element(Member):

    def __init__(self, geometry=Surface(), *args, **kwargs):
        self.geometry = geometry
        Member.__init__(self, *args, **kwargs)
        self.footprint = defaultdict(list)

    def propagate(self, ray, source=0):
        """
        Takes a ray in global coordinates and returns the ray that
        results from interacting with the surface (e.g. reflection)
        """
        new_ray = self._propagate(ray)
        if new_ray is not None:
            self.footprint[source].append((new_ray.endpoint.x,
                                           new_ray.endpoint.y,
                                           new_ray.wavelength))
        return new_ray


class Mirror(Element):

    """A mirror reflects incoming rays in its surface."""

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

    """A detector does not propagate rays further. It is intended to
    be the final element in a system.
    """

    def _propagate(self, ray):
        ray0 = self.localize(ray)
        p = self.geometry.intersect(ray0)
        if p:
            pos = self.globalize_vector(p)
            return Ray(pos, None, ray.wavelength)
        else:
            return None


class Screen(Element):

    """A screen does not interact with the direction of the imcoming
    rays, but simply passes them through. Useful for checking the
    intersection of a beam.
    """

    def _propagate(self, ray):
        ray0 = self.localize(ray)
        p = self.geometry.intersect(ray0)
        if p:
            p = self.globalize_vector(p)
            return Ray(p, ray.direction, ray.wavelength)
        else:
            return None


class ReflectiveGrating(Element):

    """A reflective grating diffracts incoming rays reflectively."""

    def __init__(self, d=0., order=0, *args, **kwargs):
        """
        Define a reflecting element with geometry shape given by s. If
        d>0 it will work as a grating with line spacing d and lines in
        the xz-plane and diffraction order given by order. Otherwise
        it works as a plain mirror.
        """
        self.d = d
        self.order = order
        #print "Mirror", args, kwargs
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
        #print b, theta
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
