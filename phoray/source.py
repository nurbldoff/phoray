from random import seed, randint, gauss
from sys import maxsize

from numpy import array, ones, zeros, random

from .member import Member
from .ray import Rays
from . import Rotation, Position, Length


class Source(Member):

    "Source base class"

    def __init__(self,
                 wavelength:Length=0.0, color:str="#ffffff", *args, **kwargs):

        Member.__init__(self, *args, **kwargs)
        self.wavelength = wavelength
        self.color = color

        self.axis = array((0., 0., 1.0))

    def generate(self, n):
        """Needs to be overridden by child classes.
        Should return Rays, probably limited by n.
        """


class TrivialSource(Source):

    """A very simple pointsource that sends out rays in one direction."""

    def generate(self, n=1):
        endpoints = zeros((n, 3))
        directions = ones((n, 3)) * self.axis
        rays = Rays(endpoints, directions, zeros(n))
        return self.globalize(rays)


class GaussianSource(Source):

    """A source that sends out rays according to a Gaussian distribution,
    in both origin and direction.

    FIXME: the divergence is only correct for small angles.
    """

    def __init__(self, size:Position=(0, 0, 0),
                 divergence:Position=(0, 0, 0),
                 random_seed:int=randint(0, maxsize),
                 *args, **kwargs):
        self.size = Position(size)
        self.divergence = Position(divergence)
        self.random_seed = random_seed
        random.seed(random_seed)

        Source.__init__(self, *args, **kwargs)

    def generate(self, n=1):

        sx, sy, sz = self.size
        s = array((zeros(n) if sx == 0 else random.normal(0, sx, n),
                   zeros(n) if sy == 0 else random.normal(0, sy, n),
                   zeros(n) if sz == 0 else random.normal(0, sz, n))).T

        dx, dy, dz = self.divergence
        d = array((zeros(n) if dx == 0 else random.normal(0, dx, n),
                   zeros(n) if dy == 0 else random.normal(0, dy, n),
                   zeros(n))).T + self.axis

        rays = self.globalize(Rays(endpoints=s, directions=d,
                                   wavelengths=ones((n,)) * self.wavelength))

        return rays
