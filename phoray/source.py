from random import seed, randint, gauss
from collections import OrderedDict

from numpy import array, dot, ones, zeros, random
from transformations import euler_matrix

from member import Member
from ray import Rays
from . import Rotation, Position


class Source(Member):

    "Source base class"

    def __init__(self,
                 wavelength=0.0, color="#ffffff", *args, **kwargs):

        Member.__init__(self, *args, **kwargs)
        self.wavelength = wavelength
        self.color = color

        self.axis = array((0., 0., 1.0))

    def generate(self, n):
        """Needs to be overridden by child classes.
        Should return a list of Rays, probably limited by n.
        """


class TrivialSource(Source):

    """A very simple pointsource that sends out rays in one direction."""

    def generate(self, n=1):
        endpoints = zeros((n, 3))
        directions = ones((n, 3)) * self.axis
        rays = Rays(endpoints, directions)
        return self.globalize(rays)


class GaussianSource(Source):

    """A source that sends out rays according to a Gaussian distribution,
    in both origin and direction.

    FIXME: the divergence is only correct for small angles.
    """

    def __init__(self, size=Position(0, 0, 0),
                 divergence=Position(0, 0, 0),
                 random_seed=randint(0, 1000000),
                 *args, **kwargs):
        self.size = size
        self.divergence = divergence
        self.random_seed = random_seed
        seed(random_seed)

        Source.__init__(self, *args, **kwargs)

    def generate(self, n=1):

        sx, sy, sz = self.size
        s = array((zeros((n)) if sx == 0 else random.normal(0, sx, n),
                   zeros((n)) if sy == 0 else random.normal(0, sy, n),
                   zeros((n)) if sz == 0 else random.normal(0, sz, n))).T

        dx, dy, dz = self.divergence
        d = array((zeros((n)) if dx == 0 else random.normal(0, dx, n),
                   zeros((n)) if dy == 0 else random.normal(0, dy, n),
                   zeros((n,)))).T + self.axis

        rays = self.globalize(Rays(endpoints=s, directions=d,
                                   wavelengths=ones((n,)) * self.wavelength))
        print "Ray 0", rays.endpoints[0], rays.directions[0]

        return rays
