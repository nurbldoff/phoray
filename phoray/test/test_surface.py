from math import degrees, fabs, sqrt
from random import uniform
from unittest import TestCase

from numpy import array, allclose

from phoray.surface import Plane, Sphere, Cylinder, Paraboloid
from phoray.ray import Ray, Rays

from . import PhorayTestCase


A, B, C = [uniform(-0.5, 0.5) for _ in xrange(3)]


class PlaneSurfaceTestCase(PhorayTestCase):

    def test_intersect(self):
        plane = Plane()
        rays = Rays(array([(A, B, -1, 1)]), array([(0, 0, 1, 0)]))
        intersection = plane.intersect(rays)
        self.assertTrue(allclose(intersection, array([(A, B, 0, 1)])))

    def test_reflect(self):
        plane = Plane()
        ray = Rays(array([(A, B, -1, 1)]), array([(0, 0, 1, 0)]))
        reflection = plane.reflect(ray)
        self.assertTrue(allclose(reflection.endpoints, (A, B, 0, 1)))
        self.assertTrue(allclose(reflection.directions, (0, 0, -1, 0)))


class SphereSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        plane = Sphere(1)
        rays = Rays(array([(0, 0, -1, 1)]), array([(A, B, 1, 0)]) /
                   sqrt(A**2 + B**2 + 1))
        reflection = plane.reflect(rays)
        print "rays", rays, "refl", reflection
        self.assertTrue(allclose(reflection.endpoints + reflection.directions,
                                 [(0, 0, -1, 1)]))


# class CylinderSurfaceTestCase(PhorayTestCase):

#     def test_reflect(self):
#         surf = Cylinder(1)
#         ray = Ray(array((0, 0, -1)), array((A, B, 1)) / sqrt(A**2 + B**2 + 1))
#         reflection = surf.reflect(ray)
#         self.assertTrue(allclose(reflection.direction[0], ray.direction[0]))
#         self.assertTrue(allclose(reflection.direction[1], -ray.direction[1]))
#         self.assertTrue(allclose(reflection.direction[2], -ray.direction[2]))


# class ParaboloidSurfaceTestCase(PhorayTestCase):

#     def test_reflect(self):
#         surf = Paraboloid(1, 1, -1)
#         ray = Ray(array((0, 0, -0.25)), array((A, B, 1)))
#         reflection = surf.reflect(ray)
#         print reflection
#         self.assertAlmostEquals(reflection.direction[0], 0)
#         self.assertAlmostEquals(reflection.direction[1], 0)
