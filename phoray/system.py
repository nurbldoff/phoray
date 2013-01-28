# Describes an optical system
from collections import OrderedDict
from math import *

from minivec import Vec, Mat
from ray import Ray

base_schema = OrderedDict()


class OpticalSystem(object):

    """An optical system consists of Sources and Elements.

    A Source is a generator of Rays. An Element is something that a
    Ray can interact with, for example a mirror that can reflect it.
    """

    def __init__(self, elements=None, sources=None):
        if elements is not None:
            self.elements = elements
        else:
            self.elements = []
        if sources is not None:
            self.sources = sources
        else:
            self.sources = []

    def update(self):
        """This function gets run after the system has been defined. It may
        make changes to the system, e.g. apply geometrical constraints to the
        elements.
        """
        pass

    def propagate(self, ray):

        """The given ray is traced from a source through each element, until it
        misses one or none are left. It is up to each element how to
        propagate the incoming ray (e.g. reflect it), and return a new ray
        (or None).

        Returned is the trace; a list of the points where the rays changed
        direction.
        """

        trace = [ray]
        for el in self.elements:
            ray = el.propagate(ray)
            if ray is None:
                break
            else:
                trace.append(ray)
        return trace

    def trace(self, n=1):
        """Generate some rays and propagate them through the system."""
        for source in self.sources:
            for ray in source.generate(n):
                yield self.propagate(ray)

    def axis(self, source=0):
        if self.sources:
            src = self.sources[0]
            r = Ray(src.position, src.globalize_direction(src.axis),
                    src.wavelength)
            axis = [src.position]
            for i in xrange(len(self.elements)):
                r = self.elements[i].propagate(r)
                if r is None:
                    break
                else:
                    axis.append(r.endpoint)
            return axis
        else:
            return []


class Free(OpticalSystem):

    """A completely free system."""

    schema = base_schema


class Sequential(OpticalSystem):

    schema = base_schema

    def get_axis(self, source=0):
        """Return the directions of the segments of the optical axis"""
        s = self.sources[source]
        r = Ray(s.position, s.axis, s.wavelength)  # Starting ray
        axis = [r]
        for i in xrange(len(self.elements)):
            r = self.elements[i].propagate(r)
            axis.append(r)
        return axis

    # def update(self):
    #     print "update"
    #     position = self.sources[0].position
    #     rotation = self.sources[0].rotation
    #     for i, element in enumerate(self.elements):
    #         print "Updating element %d" % i
    #         print "position", position, "rotation", rotation
    #         rotmat = Mat().rotate(rotation)
    #         element.position = position
    #         position = position + (element.offset).transform(rotmat)
    #         element.rotation = rotation
    #         rotation = rotation + element.alignment

    def update(self):
        print "update"
        source = self.sources[0]
        position = source.position
        rotation = source.rotation
        ray = Ray(origin=position,
                  direction=source.globalize_direction(source.axis))
        for i, element in enumerate(self.elements):
            print "updating element %d" % i
            element.position = position
            element.rotation = rotation
            new_ray = element.propagate(ray)
            if new_ray is None:
                print "missed element %d" % i
                return False
            else:
                x_angle = ray.direction.angle(new_ray.direction)
                print "angle", x_angle
                y_angle = element.rotation.y + element.alignment.y
                z_angle = element.rotation.z + element.alignment.z
                rot = Vec(x_angle, y_angle, z_angle)
                rotmat = Mat().rotate(rotation)
                rotmat2 = Mat().rotate(rot)
                position = element.position + element.offset.transform(rotmat)
                #rotation += rot
                ray = new_ray
