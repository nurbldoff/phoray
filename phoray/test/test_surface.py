from math import degrees, fabs, sqrt
from random import uniform
from unittest import TestCase

from numpy import array, allclose, NaN, isnan

from phoray.surface import Plane, Sphere, Cylinder, Ellipsoid, Paraboloid
from phoray.ray import Rays

from . import PhorayTestCase


A, B, C = [uniform(-0.5, 0.5) for _ in xrange(3)]


class PlaneSurfaceTestCase(PhorayTestCase):

    def test_intersect(self):
        plane = Plane()
        rays = Rays(array([(A, B, -1)]), array([(0, 0, 1)]), None)
        intersection = plane.intersect(rays)
        self.assertTrue(allclose(intersection, array([(A, B, 0)])))

    def test_intersect_miss(self):
        "Check that intersecting outside the edges returns NaNs"
        plane = Plane(xsize=0.1)
        rays = Rays(array([(A + 1, B, -1)]), array([(0, 0, 1)]), None)
        intersection = plane.intersect(rays)
        self.assertTrue(all(isnan(intersection[0])))

    def test_reflect(self):
        plane = Plane()
        ray = Rays(array([(A, B, -1)]), array([(0, 0, 1)]), None)
        reflection = plane.reflect(ray)
        self.assertTrue(allclose(reflection.endpoints, (A, B, 0)))
        self.assertTrue(allclose(reflection.directions, (0, 0, -1)))

    def test_reflect_miss(self):
        plane = Plane()
        ray = Rays(array([(A+1, B, -1)]), array([(0, 0, 1)]), None)
        reflection = plane.reflect(ray)
        self.assertTrue(all(isnan(reflection.endpoints[0])))


class SphereSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        sphere = Sphere(1)
        rays = Rays(array([(0, 0, -1)]), array([(A, B, 1)]) /
                    sqrt(A**2 + B**2 + 1), None)
        reflection = sphere.reflect(rays)
        self.assertTrue(allclose(reflection.endpoints + reflection.directions,
                                 [(0, 0, -1)]))


class CylinderSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        surf = Cylinder(1)
        ray = Rays(array([(0, 0, -1)]),
                   array([(A, B, 1)]) / sqrt(A**2 + B**2 + 1), None)
        reflection = surf.reflect(ray).directions[0]
        self.assertTrue(allclose(reflection[0], ray.directions[0][0]))
        self.assertTrue(allclose(reflection[1], -ray.directions[0][1]))
        self.assertTrue(allclose(reflection[2], -ray.directions[0][2]))


class EllipsoidSurfaceTestCase(PhorayTestCase):

    def test_reflect_spherical(self):
        """Check that an ellipsoid with all equal radii is a sphere."""
        sphere = Ellipsoid(1, 1, 1)
        rays = Rays(array([(0, 0, -1)]), array([(A, B, 1)]) /
                    sqrt(A**2 + B**2 + 1), None)
        reflection = sphere.reflect(rays)
        self.assertTrue(allclose(reflection.endpoints + reflection.directions,
                                 [(0, 0, -1)]))


class ParaboloidSurfaceTestCase(PhorayTestCase):

    def test_reflect(self):
        surf = Paraboloid(1, 1, -1)
        ray = Rays(array([(0, 0, -0.25)]), array([(A, B, 1)]), None)
        reflection = surf.reflect(ray)
        self.assertAlmostEquals(reflection.directions[0][0], 0)
        self.assertAlmostEquals(reflection.directions[0][1], 0)
