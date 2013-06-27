from math import fabs
from unittest import TestCase
from numpy import allclose

_DefaultEpsilon = 1e-10


class PhorayTestCase(TestCase):

    def assertAllClose(self, a, b):
        assert allclose(a[:3], b[:3])
