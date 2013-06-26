from math import degrees
from unittest import TestCase

from numpy import array, allclose

from phoray.ray import Ray


class RayTestCase(TestCase):

    pass

    # def test_translate(self):
    #     ray = Ray(array((1.0, 2.1, 3.2)))
    #     ray2 = ray.translate(array((4.0, 5.1, 6.2)))
    #     print ray2
    #     self.assertTrue(allclose(ray2.endpoint, (5, 7.2, 9.4)))
