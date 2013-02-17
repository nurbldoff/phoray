from random import seed, randint, gauss
from collections import OrderedDict

from member import Member
from ray import Ray
from minivec import Vec, Mat


base_schema = OrderedDict([("wavelength", {"type": "length"}),
                           ("position", {"type": "position"}),
                           ("rotation", {"type": "rotation"}),
                           ("offset", {"type": "position"}),
                           ("alignment", {"type": "rotation"})])


class Source(Member):

    def __init__(self, wavelength=0.0,
                 position=Vec(0, 0, 0),
                 rotation=Vec(0, 0, 0),
                 offset=Vec(0, 0, 0),
                 alignment=Vec(0, 0, 0)):
        Member.__init__(self, position, rotation, offset, alignment)
        self.wavelength = wavelength

        self.axis = Vec(0., 0., 1.0)

    def generate(self, n):
        """Needs to be overridden by child classes.
        Should return a list of Rays, probably limited by n.
        """


class TrivialSource(Source):

    """A very simple pointsource that sends out rays in one direction."""

    # schema = base_schema

    def generate(self, n=1):
        for i in xrange(n):
            yield self.globalize(Ray(direction=self.axis,
                                     wavelength=self.wavelength))


class GaussianSource(Source):

    """A source that sends out rays according to a Gaussian distribution,
    in both origin and direction.
    """

    # schema = OrderedDict([("size", {"type": "position"}),
    #                       ("divergence", {"type": "rotation"})] +
    #                      base_schema.items())

    def __init__(self, size=Vec(0, 0, 0),
                 divergence=Vec(0, 0, 0),
                 random_seed=randint(0, 1000000),
                 *args, **kwargs):
        self.size = Vec(size)
        self.divergence = Vec(divergence)
        self.random_seed = random_seed
        seed(random_seed)

        Source.__init__(self, *args, **kwargs)

    def generate(self, n=1):

        for i in xrange(n):
            local_position = Vec(gauss(0, self.size.x),
                                 gauss(0, self.size.y),
                                 gauss(0, self.size.z))
            local_rotation = Vec(gauss(0, self.divergence.y),
                                 gauss(0, self.divergence.x),
                                 gauss(0, self.divergence.z))
            rotation = Mat().rotate(local_rotation)

            yield self.globalize(
                Ray(origin=local_position,
                    direction=self.axis.transformDir(rotation),
                    wavelength=self.wavelength))
