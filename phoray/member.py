from __future__ import division
from math import *

from numpy import array, dot, ones, zeros, radians
from numpy.linalg import inv as inverse_matrix
from transformations import (euler_matrix, translation_matrix,
                             concatenate_matrices)

from ray import Rays
from phoray import current_id
from . import Position


class Frame(object):
    """A representation of a frame of reference.

    Contains methods to convert from and to the local coordinate system.
    """

    def __init__(self, position=Position(0, 0, 0), rotation=Position(0, 0, 0)):
        self.position = Position(position)
        self.rotation = Position(rotation)
        self.calculate_matrices()

    def calculate_matrices(self):
        print self.rotation
        rotate = euler_matrix(*radians(self.rotation), axes="rxyz")

        self._matloc = concatenate_matrices(
            inverse_matrix(rotate), translation_matrix(-self.position)).T
        self._matglob = inverse_matrix(self._matloc)

    def localize_position(self, v):
        """Turn global (relative to the frame) coordinates into local."""
        tmp = ones((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matloc)[:, :3]

    def localize_direction(self, v):
        """A direction does not change with translation."""
        print "localize_dir", len(v)
        tmp = zeros((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matloc)[:, :3]

    def globalize_position(self, v):
        """Turn local coordinates into global."""
        tmp = ones((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matglob)[:, :3]

    def globalize_direction(self, v):
        """A direction does not change with translation."""
        tmp = zeros((len(v), 4))  # make 4-vectors for translations
        tmp[:, :3] = v
        return dot(tmp, self._matglob)[:, :3]


class Member(object):

    """Baseclass for a generalized member of an optical system."""

    def __init__(self, _id=None, frames=None):

        if _id is None:
            self._id = current_id.next()
        else:
            self._id = _id

        self.frames = frames

        # Precalculate some matrices. Note that this means that the
        # member can't be moved after creation, unless precalc is
        # called again afterwards.

    def localize(self, rays):
        """
        Transform a Ray in global coordinates into local coordinates
        """
        local_endp = rays.endpoints
        local_dir = rays.directions
        for f in reversed(self.frames):
            local_endp = f.localize_position(local_endp)
            local_dir = f.localize_direction(local_dir)

        return Rays(local_endp, local_dir, rays.wavelengths)

    def globalize(self, rays):
        """
        Transform a local Ray into global coordinates
        """
        global_endp = rays.endpoints
        global_dir = rays.directions
        for f in self.frames:
            global_endp = f.globalize_position(global_endp)
            global_dir = f.globalize_direction(global_dir)

        return Rays(global_endp, global_dir, rays.wavelengths)

    def x_axis(self):
        return self.globalize_vector(array((1, 0, 0)))

    def y_axis(self):
        return self.globalize_vector(array((0, 1, 0)))

    def z_axis(self):
        return self.globalize_vector(array((0, 0, 1)))
