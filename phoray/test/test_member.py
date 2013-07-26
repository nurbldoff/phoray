from random import uniform

from phoray.member import Member, Frame
from phoray.ray import Rays
from . import PhorayTestCase


A, B, C, D, E, F, G, H, I = [uniform(-0.5, 0.5) for _ in range(9)]


class FrameTestCase(PhorayTestCase):

    def test_localize_position_translation(self):
        v1 = [(A, B, C)]
        dv = (D, E, F)
        frame = Frame(position=dv)
        v2 = frame.localize_position(v1)
        self.assertAllClose(v1[0], v2[0] + dv)

    def test_localize_position_rotation(self):
        """Euler rotation is applied in the correct order."""
        v1 = [(A, B, C)]
        rot = (90., 0., -90.)
        frame = Frame(rotation=rot)
        v2 = frame.localize_position(v1)
        self.assertAllClose((-C, A, -B), v2[0])

    def test_localize_position_all(self):
        """Transformations are applied in the correct order."""
        v1 = [(A, B, C)]
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        frame = Frame(position=pos, rotation=rot)
        v2 = frame.localize_position(v1)
        self.assertAllClose((-B, A-D, C), v2[0])

    def test_localize_direction_all(self):
        """Only rotations are performed on directions."""
        v1 = [(A, B, C)]
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        frame = Frame(position=pos, rotation=rot)
        v2 = frame.localize_direction(v1)
        self.assertAllClose((-B, A, C), v2[0])

    def test_globalize_position_translation(self):
        v1 = [(A, B, C)]
        dv = (D, E, F)
        frame = Frame(position=dv)
        v2 = frame.globalize_position(v1)
        self.assertAllClose(v1[0], v2[0] - dv)

    def test_globalize_position_rotation(self):
        """Rotation is applied in reverse."""
        v1 = [(A, B, C)]
        rot = (90, 0, -90)
        frame = Frame(rotation=rot)
        v2 = frame.globalize_position(v1)
        self.assertAllClose((B, -C, -A), v2[0])

    def test_globalize_position_all(self):
        """Transformations are applied in the correct order."""
        v1 = (A, B, C)
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        frame = Frame(position=pos, rotation=rot)
        v2 = frame.globalize_position(v1)
        self.assertAllClose((B+D, -A, C), v2[0])

    def test_globalize_direction_all(self):
        """Transformations are applied in the correct order."""
        v1 = (A, B, C)
        pos = (D, 0, 0)
        rot = (0, 0, -90)
        frame = Frame(position=pos, rotation=rot)
        v2 = frame.globalize_direction(v1)
        self.assertAllClose((B, -A, C), v2[0])


class MemberTestCase(PhorayTestCase):

    """TODO: Expand these tests to cover more combinations and edge cases."""

    def test_localize(self):
        p = [(A, B, C)]
        d = [(D, E, F)]
        pos = (G, H, I)
        r1 = Rays(p, d, None)
        member = Member(frames=[Frame(position=pos)])
        r2 = member.localize(r1)
        self.assertAllClose(r1.endpoints[0], r2.endpoints[0] + pos)
        self.assertAllClose(r1.directions[0], r2.directions[0])

    def test_localize_multiple_frames(self):
        "Localizing a ray with several rotated frames is correctly ordered"
        p = [(A, B, C)]
        d = [(B, C, A)]
        rot1 = (90, 0, 0)
        rot2 = (0, 0, 90)
        r1 = Rays(p, d, None)
        member = Member(frames=[Frame(rotation=rot1), Frame(rotation=rot2)])
        r2 = member.localize(r1)
        self.assertAllClose(r2.endpoints[0], (B, C, A))

    def test_globalize(self):
        p = [(A, B, C)]
        d = [(D, E, F)]
        pos = (G, H, I)
        r1 = Rays(p, d, None)
        member = Member(frames=[Frame(position=pos)])
        r2 = member.globalize(r1)
        self.assertAllClose(r1.endpoints[0], r2.endpoints[0] - pos)
        self.assertAllClose(r1.directions[0], r2.directions[0])

    def test_globalize_multiple_frames(self):
        "Globalizing a ray with several rotated frames is correctly ordered"
        p = [(A, B, C)]
        d = [(B, C, A)]
        rot1 = (90, 0, 0)
        rot2 = (0, 0, 90)
        r1 = Rays(p, d, None)
        member = Member(frames=[Frame(rotation=rot1), Frame(rotation=rot2)])
        r2 = member.globalize(r1)
        self.assertAllClose(r2.endpoints[0], (C, A, B))
