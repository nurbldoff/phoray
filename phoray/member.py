from __future__ import division
from math import *

from minivec import Vec, Mat
from ray import Ray


class Member(object):

    """Baseclass for a generalized member of an optical system."""

    def __init__(self, position=Vec(0, 0, 0), rotation=Vec(0, 0, 0),
                 offset=Vec(0, 0, 0), alignment=Vec(0, 0, 0)):

        self.position = Vec(position)
        self.rotation = Vec(rotation)

        self.offset = Vec(offset)
        self.alignment = Vec(alignment)

        # Precalculate some matrices. Note that this means that the
        # element can't be moved after creation, unless precalc is
        # called again afterwards.
        self.precalc()

    def precalc(self):
        self._rotate = Mat().rotate(self.rotation)
        self._align = Mat().rotate(self.alignment)

        self._matloc = Mat().translate(-self.position)\
            .transform(self._rotate.invert())\
            .translate(-self.offset).transform(self._align.invert())
        self._matglob = Mat().transform(self._align)\
            .translate(self.offset).transform(self._rotate)\
            .translate(self.position)

    def localize_vector(self, v):
        #return (((v - self.position).transform(self._rotate.invert()) -
        #        self.offset).transform(self._align.invert()))
        return v.transform(self._matloc)

    def localize_direction(self, v):
        #return v.transformDir(self._rotate.invert()).transformDir(
        #    self._align.invert())
        return v.transformDir(self._matloc)

    def localize(self, ray):
        """
        Transform a Ray in global coordinates into local coordinates
        """
        return Ray(self.localize_vector(ray.endpoint),
                   self.localize_direction(ray.direction),
                   ray.wavelength)

    def globalize_vector(self, v):
        #return ((v.transform(self._align) + self.offset).transform(
        #        self._rotate) + self.position)
        return v.transform(self._matglob)

    def globalize_direction(self, v):
        #return v.transformDir(self._align).transformDir(self._rotate)
        return v.transformDir(self._matglob)

    def globalize(self, ray):
        """
        Transform a local Ray into global coordinates
        """
        return Ray(self.globalize_vector(ray.endpoint),
                   self.globalize_direction(ray.direction),
                   ray.wavelength)
