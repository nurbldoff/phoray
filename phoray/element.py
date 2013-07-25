from __future__ import division
from math import *
from collections import defaultdict

from numpy import array, NaN, empty

from .member import Member
from .surface import Surface
from .ray import Rays


class Element(Member):

    def __init__(self, geometry:Surface, footprint=True, *args, **kwargs):
        self.geometry = geometry
        self.save_footprint = footprint
        self.footprint = defaultdict(list)
        Member.__init__(self, *args, **kwargs)

    def propagate(self, rays, source=0):
        """
        Takes a ray in global coordinates and returns the ray that
        results from interacting with the surface (e.g. reflection)
        """

        new_rays = self._propagate(self.localize(rays))
        if self.save_footprint:
            self.footprint[source] = array((new_rays.endpoints.T[0],
                                            new_rays.endpoints.T[1],
                                            new_rays.wavelengths)).T
        return self.globalize(new_rays)


class Mirror(Element):

    """A mirror reflects incoming rays in its surface."""

    def _propagate(self, rays):
        return self.geometry.reflect(rays)


class Detector(Element):

    """A detector does not propagate rays further. It is intended to
    be the final element in a system.
    """

    def _propagate(self, rays):
        p = self.geometry.intersect(rays)
        nans = empty((len(rays), 3))
        nans[:] = (NaN, NaN, NaN)
        return Rays(p, nans, rays.wavelengths)


class Screen(Element):

    """A screen does not interact with the direction of the imcoming
    rays, but simply passes them through. Useful for checking the
    intersection of a beam.
    """

    def _propagate(self, rays):
        p = self.geometry.intersect(rays)
        return Ray(p, rays.direction, rays.wavelength)


class ReflectiveGrating(Element):

    """A reflective grating diffracts incoming rays reflectively."""

    def __init__(self, d:float=0., order:int=0, *args, **kwargs):
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

    def _propagate(self, rays):
        diffracted_rays = self.geometry.diffract(
            rays, self.d, self.order)
        return diffracted_rays


class ReflectiveVLSGrating(Mirror):

    """A grating with varying line spacing. Not complete."""

    def __init__(self, an:float=1.0, *args, **kwargs):
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

    def _propagate(self, rays):
        diffracted_rays = self.geometry.diffract(rays, None, self.order,
                                                 self.get_line_distance)
        return self.globalize(diffracted_rays)


class Glass(Element):

    """A glass surface, defined by the refraction indices on each side."""

    def __init__(self, index1:float=1.0, index2:float=1.0, *args, **kwargs):
        self.index1 = index1
        self.index2 = index2
        Element.__init__(self, *args, **kwargs)

    def _propagate(self, ray):
        refracted_rays = self.geometry.refract(rays, self.index1,
                                               self.index2)
        return refracted_rays
