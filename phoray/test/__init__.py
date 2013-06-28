from unittest import TestCase
from numpy import allclose


class PhorayTestCase(TestCase):

    def assertAllClose(self, a, b):
        assert allclose(a[:3], b[:3])
