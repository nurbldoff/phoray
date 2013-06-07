from math import degrees
from unittest import TestCase

from phoray.ray import Ray
from phoray.minivec import Vec


class RayTestCase(TestCase):

    def test_translate(self):
        ray = Ray(Vec(1.0, 2.1, 3.2))
        ray2 = ray.translate(Vec(4.0, 5.1, 6.2))
        print ray2
        self.assertTrue(ray2.endpoint.almost(5, 7.2, 9.4))

    def test_deviate(self):
        ray = Ray(direction=Vec(1.0, 2.1, 3.2))
        ray2 = ray.deviate(Vec(0.1, 0.2, 0.3))
        print ray2
        self.assertTrue(ray2.direction.almost(1.0, 2.3, 3.5))
