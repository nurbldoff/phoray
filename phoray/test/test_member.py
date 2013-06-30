from random import uniform

from phoray.member import Member
from . import PhorayTestCase


A, B, C, D, E, F = [uniform(-0.5, 0.5) for _ in xrange(6)]


class MemberTestCase(PhorayTestCase):

    def test_localize_vector_position(self):
        v1 = [(A, B, C)]
        dv = (D, E, F)
        member = Member(position=dv)
        v2 = member.localize_vector(v1)
        print v1, v2
        self.assertAllClose(v1[0], v2[0] + dv)

    def test_localize_vector_rotation(self):
        """Check that Euler rotation is applied in the correct order."""
        v1 = [(A, B, C)]
        rot = (90., 0., -90.)
        member = Member(rotation=rot)
        v2 = member.localize_vector(v1)
        self.assertAllClose((-C, A, -B), v2[0])

    def test_localize_vector_offset(self):
        v1 = [(A, B, C)]
        dv = (D, E, F)
        member = Member(offset=dv)
        v2 = member.localize_vector(v1)
        self.assertAllClose(v1[0], v2[0] + dv)

    def test_localize_vector_alignment(self):
        v1 = [(A, B, C)]
        rot = (90, 0, -90)
        member = Member(alignment=rot)
        v2 = member.localize_vector(v1)
        self.assertAllClose((-C, A, -B), v2)

    def test_localize_vector_all(self):
        """Check that transformations are applied in the correct order."""
        v1 = [(A, B, C)]
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        offs = (0, 0, E)
        align = (90, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.localize_vector(v1)
        self.assertAllClose((-B, C-E, -(A-D)), v2[0])

    def test_localize_direction_all(self):
        """Check that only rotations are performed on directions."""
        v1 = [(A, B, C)]
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        offs = (0, 0, E)
        align = (90, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.localize_direction(v1)
        self.assertAllClose((-B, C, -A), v2[0])

    def test_globalize_vector_position(self):
        v1 = [(A, B, C)]
        dv = (D, E, F)
        member = Member(position=dv)
        v2 = member.globalize_vector(v1)
        self.assertAllClose(v1[0], v2[0] - dv)

    def test_globalize_vector_rotation(self):
        """Check that rotation is applied in reverse."""
        v1 = [(A, B, C)]
        rot = (90, 0, -90)
        member = Member(rotation=rot)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((B, -C, -A), v2[0])

    def test_globalize_vector_offset(self):
        v1 = [(A, B, C)]
        dv = (D, E, F)
        member = Member(offset=dv)
        v2 = member.globalize_vector(v1)
        self.assertAllClose(v1[0], v2[0] - dv)

    def test_globalize_vector_alignment(self):
        v1 = [(A, B, C)]
        rot = (90, 0, -90)
        member = Member(alignment=rot)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((B, -C, -A), v2[0])

    def test_globalize_vector_all(self):
        """Check that transformations are applied in the correct order."""
        v1 = (A, B, C)
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        offs = (0, 0, E)
        align = (90, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.globalize_vector(v1)
        self.assertAllClose((-C+D, -A, B+E), v2[0])

    def test_globalize_direction_all(self):
        """Check that transformations are applied in the correct order."""
        v1 = (A, B, C)
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        offs = (0, 0, E)
        align = (90, 0, 0)
        member = Member(position=pos, rotation=rot,
                        offset=offs, alignment=align)
        v2 = member.globalize_direction(v1)
        self.assertAllClose((-C, -A, B), v2[0])
