from __future__ import division
from math import *

from numpy import array, dot, ones, zeros
from numpy.linalg import inv as invert_matrix
from transformations import (euler_matrix, translation_matrix,
                             concatenate_matrices)

from ray import Rays
from phoray import current_id
from . import Position


class Member(object):

    """Baseclass for a generalized member of an optical system."""

    def __init__(self, _id=None, position=Position(0, 0, 0),
                 rotation=Position(0, 0, 0),
                 offset=Position(0, 0, 0), alignment=Position(0, 0, 0)):

        if _id is None:
            self._id = current_id.next()
        else:
            self._id = _id

        if isinstance(position, dict):
            self.position = Position(**position)
        else:
            self.position = Position(*position)
        self.rotation = Position(*rotation)

        self.offset = Position(*offset)
        self.alignment = Position(*alignment)

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
        print self.rotation
        self._rotate = euler_matrix(self.rotation[0], self.rotation[1],
                                    self.rotation[2], axes="rxyz")
        self._align = euler_matrix(self.alignment[0], self.alignment[1],
                                   self.alignment[2], axes="rxyz")

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
        tmp = ones((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matloc)[:, :3]

    def localize_direction(self, v):
        tmp = zeros((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matloc)[:, :3]

    def localize(self, rays):
        """
        Transform a Ray in global coordinates into local coordinates
        """
        return Rays(self.localize_vector(rays.endpoints),
                    self.localize_direction(rays.directions),
                    rays.wavelengths)

    def globalize_vector(self, v):
        #return ((v.transform(self._align) + self.offset).transform(
        #        self._rotate) + self.position)
        tmp = ones((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matglob)[:, :3]

    def globalize_direction(self, v):
        #return v.transformDir(self._align).transformDir(self._rotate)
        tmp = zeros((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matglob)[:, :3]

    def globalize(self, rays):
        """
        Transform a local Ray into global coordinates
        """
        return Rays(self.globalize_vector(rays.endpoints),
                    self.globalize_direction(rays.directions),
                    rays.wavelengths)

    def x_axis(self):
        return self.globalize_vector(array((1, 0, 0)))

    def y_axis(self):
        return self.globalize_vector(array((0, 1, 0)))

    def z_axis(self):
        return self.globalize_vector(array((0, 0, 1)))
