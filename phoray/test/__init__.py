from math import fabs
from unittest import TestCase


_DefaultEpsilon = 1e-10


class PhorayTestCase(TestCase):

    def assertAlmostEqual(self, a, b, epsilon=_DefaultEpsilon):
        try:
            a1, a2, a3 = a
            b1, b2, b3 = b
            assert (fabs(a1 - b1) < epsilon > fabs(a2 - b2) and
                    fabs(a3 - b3) < epsilon)
        except TypeError:
            assert fabs(a - b) < epsilon
