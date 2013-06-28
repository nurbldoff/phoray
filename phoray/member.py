from __future__ import division
from math import *

from numpy import array, dot
from numpy.linalg import inv as invert_matrix
from transformations import (euler_matrix, translation_matrix,
                             concatenate_matrices)

from ray import Ray
from phoray import current_id


class Member(object):

    """Baseclass for a generalized member of an optical system."""

    def __init__(self, _id=None, position=array((0, 0, 0)),
                 rotation=array((0, 0, 0)),
                 offset=array((0, 0, 0)), alignment=array((0, 0, 0))):

        if _id is None:
            self._id = current_id.next()
        else:
            self._id = _id

        self.position = array(position)
        self.rotation = array(rotation)

        self.offset = array(offset)
        self.alignment = array(alignment)

        # Precalculate some matrices. Note that this means that the
        # member can't be moved after creation, unless precalc is
        # called again afterwards.
        self.precalc()

        self._schema = None

    def _precalc(self):
        # This is just the old pre-numpy code, remove
        self._rotate = Mat().rotate(self.rotation)
        self._align = Mat().rotate(self.alignment)

        self._matloc = Mat().translate(-self.position)\
            .transform(self._rotate.invert())\
            .translate(-self.offset).transform(self._align.invert())
        self._matglob = Mat().transform(self._align)\
            .translate(self.offset).transform(self._rotate)\
            .translate(self.position)

    def precalc(self):
        self._rotate = euler_matrix(*self.rotation, axes="rxyz")
        self._align = euler_matrix(*self.alignment, axes="rxyz")

        self._matloc = concatenate_matrices(invert_matrix(self._align),
                                            translation_matrix(-self.offset),
                                            invert_matrix(self._rotate),
                                            translation_matrix(-self.position)
                                            ).T
        self._matglob = concatenate_matrices(translation_matrix(self.position),
                                             self._rotate,
                                             translation_matrix(self.offset),
                                             self._align).T

    def localize_vector(self, v):
        #return (((v - self.position).transform(self._rotate.invert()) -
        #        self.offset).transform(self._align.invert()))
        return dot(v, self._matloc)

    def localize_direction(self, v):
        #return v.transformDir(self._rotate.invert()).transformDir(
        #    self._align.invert())
        return dot(v, self._matloc)

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
        return dot(v, self._matglob)

    def globalize_direction(self, v):
        #return v.transformDir(self._align).transformDir(self._rotate)
        return dot(v, self._matglob)

    def globalize(self, ray):
        """
        Transform a local Ray into global coordinates
        """
        return Ray(self.globalize_vector(ray.endpoint),
                   self.globalize_direction(ray.direction),
                   ray.wavelength)

    def x_axis(self):
        return self.globalize_vector(array((1, 0, 0)))

    def y_axis(self):
        return self.globalize_vector(array((0, 1, 0)))

    def z_axis(self):
        return self.globalize_vector(array((0, 0, 1)))
