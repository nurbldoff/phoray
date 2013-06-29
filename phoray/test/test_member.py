from math import pi
from random import uniform
from unittest import TestCase

from numpy import array

from phoray.member import Member
from . import PhorayTestCase
from phoray.vector import position, direction


A, B, C, D, E, F = [uniform(-0.5, 0.5) for _ in xrange(6)]


class MemberTestCase(PhorayTestCase):

    def test_localize_vector_position(self):
        v1 = array([(A, B, C)])
        dv = position(D, E, F)
        member = Member(position=dv)
        v2 = member.localize_vector(v1)
        print v1, v2
        self.assertAllClose(v1[0] - dv, v2[0])

    def test_localize_vector_rotation(self):
        """Check that Euler rotation is applied in the correct order (XYZ)."""
        v1 = position(A, B, C)
        rot = (pi/2, 0, -pi/2)
        member = Member(rotation=rot)
        v2 = member.localize_vector(v1)
        self.assertAllClose((-C, A, -B), v2)

    def test_localize_vector_offset(self):
        v1 = position(A, B, C)
        dv = position(D, E, F)
        member = Member(offset=dv)
        v2 = member.localize_vector(v1)
        self.assertAllClose(v1 - dv, v2)

    def test_localize_vector_alignment(self):
        v1 = position(A, B, C)
        rot = (pi/2, 0, -pi/2)
        member = Member(alignment=rot)
        v2 = member.localize_vector(v1)
        self.assertAllClose((-C, A, -B), v2)

    def test_localize_vector_all(self):
        """Check that transformations are applied in the correct order."""
        v1 = position(A, B, C)
        pos = position(D, 0, 0)
        rot = (0, 0, -pi/2)
        offs = position(0, 0, E)
        align = (pi/2, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.localize_vector(v1)
        self.assertAllClose((-B, C-E, -(A-D)), v2)

    def test_localize_direction_all(self):
        """Check that only rotations are performed on directions."""
        v1 = direction(A, B, C)
        pos = position(D, 0, 0)
        rot = (0, 0, -pi/2)
        offs = position(0, 0, E)
        align = (pi/2, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.localize_direction(v1)
        self.assertAllClose((-B, C, -A), v2)

    def test_globalize_vector_position(self):
        v1 = position(A, B, C)
        dv = position(D, E, F)
        member = Member(position=dv)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((v1 + dv), v2)

    def test_globalize_vector_rotation(self):
        """Check that rotation is applied in reverse."""
        v1 = position(A, B, C)
        rot = (pi/2, 0, -pi/2)
        member = Member(rotation=rot)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((B, -C, -A), v2)

    def test_globalize_vector_offset(self):
        v1 = position(A, B, C)
        dv = position(D, E, F)
        member = Member(offset=dv)
        v2 = member.globalize_vector(v1)
        self.assertAllClose(v1 + dv, v2)

    def test_globalize_vector_alignment(self):
        v1 = position(A, B, C)
        rot = (pi/2, 0, -pi/2)
        member = Member(alignment=rot)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((B, -C, -A), v2)

    def test_globalize_vector_all(self):
        """Check that transformations are applied in the correct order."""
        v1 = position(A, B, C)
        pos = position(D, 0, 0)
        rot = (0, 0, -pi/2)
        offs = position(0, 0, E)
        align = (pi/2, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((-C+D, -A, B+E), v2)

    def test_globalize_direction_all(self):
        """Check that transformations are applied in the correct order."""
        v1 = direction(A, B, C)
        pos = position(D, 0, 0)
        rot = (0, 0, -pi/2)
        offs = position(0, 0, E)
        align = (pi/2, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.globalize_direction(v1)
        self.assertAllClose((-C, -A, B), v2)
