from random import seed, randint, gauss
from collections import OrderedDict

from numpy import array, dot
from transformations import euler_matrix

from member import Member
from ray import Ray



base_schema = OrderedDict([("wavelength", {"type": "length"}),
                           ("position", {"type": "position"}),
                           ("rotation", {"type": "rotation"}),
                           ("offset", {"type": "position"}),
                           ("alignment", {"type": "rotation"})])


class Source(Member):

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

    def __init__(self, size=array((0, 0, 0)),
                 divergence=array((0, 0, 0)),
                 random_seed=randint(0, 1000000),
                 *args, **kwargs):
        self.size = size
        self.divergence = divergence
        self.random_seed = random_seed
        seed(random_seed)

        Source.__init__(self, *args, **kwargs)

    def generate(self, n=1):

        sx, sy, sz = self.size
        dx, dy, dz = self.divergence

        for i in xrange(n):
            local_position = array((gauss(0, sx), gauss(0, sy), gauss(0, sz)))
            local_rotation = array((gauss(0, dy), gauss(0, dx), gauss(0, dz)))
            #rotation = Mat().rotate(local_rotation)
            rot = euler_matrix(*local_rotation)

            yield self.globalize(
                Ray(origin=local_position,
                    direction=dot(self.axis, rot[:3, :3].T),
                    wavelength=self.wavelength))
