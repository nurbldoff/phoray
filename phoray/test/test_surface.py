from math import degrees, fabs, sqrt
from random import uniform
from unittest import TestCase

from phoray.surface import Plane, Sphere, Cylinder, Paraboloid
from phoray.ray import Ray
from phoray.minivec import Vec

from . import PhorayTestCase


A, B, C = [uniform(-0.5, 0.5) for _ in xrange(3)]


class PlaneSurfaceTestCase(PhorayTestCase):

    def test_intersect(self):
        plane = Plane()
        ray = Ray(Vec(A, B, -1), Vec(0, 0, 1))
        intersection = plane.intersect(ray)
        self.assertAlmostEqual(intersection, Vec(A, B, 0))

    def test_reflect(self):
        plane = Plane()
        ray = Ray(Vec(A, B, -1), Vec(0, 0, 1))
        reflection = plane.reflect(ray)
        self.assertAlmostEqual(reflection.endpoint, Vec(A, B, 0))
        self.assertAlmostEqual(reflection.direction, Vec(0, 0, -1))


class SphereSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        plane = Sphere(R=1)
        ray = Ray(Vec(0, 0, -1), Vec(A, B, 1).normalize())
        reflection = plane.reflect(ray)
        self.assertAlmostEqual(reflection.endpoint + reflection.direction,
                               Vec(0, 0, -1))


class CylinderSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        surf = Cylinder(R=1)
        ray = Ray(Vec(0, 0, -1), Vec(A, B, 1).normalize())
        reflection = surf.reflect(ray)
        self.assertAlmostEqual(reflection.direction.x, ray.direction.x)
        self.assertAlmostEqual(reflection.direction.y, -ray.direction.y)
        self.assertAlmostEqual(reflection.direction.z, -ray.direction.z)


class ParaboloidSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        surf = Paraboloid(a=1, b=1, c=-1)
        ray = Ray(Vec(0, 0, -0.25), Vec(A, B, 1).normalize())
        reflection = surf.reflect(ray)
        print reflection
        self.assertAlmostEqual(reflection.direction.x, 0)
        self.assertAlmostEqual(reflection.direction.y, 0)
