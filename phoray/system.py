# Describes an optical system
from itertools import count
from math import *

import numpy as np

from member import Member
from ray import Ray


class OpticalSystem(Member):

    """An optical system consists of Sources and Elements.

    A Source is a generator of Rays. An Element is something that a
    Ray can interact with, for example a mirror that can reflect it.
    """

    def __init__(self, elements=[], sources=[], **kwargs):

        if elements is not None:
            self.elements = elements
        else:
            self.elements = []
        if sources is not None:
            self.sources = sources
        else:
            self.sources = []

        self.current_id = count()

        Member.__init__(self, **kwargs)

    def add_source(self, source):
        source._id = self.current_id.next()
        self.sources.append(source)

    def add_element(self, element):
        element._id = self.current_id.next()
        self.elements.append(element)

    def update(self):
        """This function gets run after the system has been defined. It may
        make changes to the system, e.g. apply geometrical constraints to the
        elements.
        """
        pass

    def propagate(self, rays, system):

        """The given ray is traced from a source through each element, until it
        misses one or none are left. It is up to each element how to
        propagate the incoming ray (e.g. reflect it), and return a new ray
        (or None).

        Returned is the trace; a list of the points where the rays changed
        direction.
        """

        trace = [rays]
        for el in self.elements:
            rays = el.propagate(rays, system)
            trace.append(rays)
        return trace

    def trace(self, n=1):
        """Generate some rays and propagate them through the system."""

        for element in self.elements:
            element.footprint.clear()

        results = []
        for i, source in enumerate(self.sources):
            rays = source.generate(n)
            trace = self.propagate(rays, i)
            results.append(trace)
        return results

    def axis(self, source=0):
        if self.sources:
            src = self.sources[0]
            r = Ray(src.position, src.globalize_direction(src.axis),
                    src.wavelength)
            axis = []
            for i in xrange(len(self.elements)):
                if r is None:
                    break
                axis.append(r.endpoint)
                r = self.elements[i].propagate(r)
            return axis
        else:
            return []


class Free(OpticalSystem):

    """A completely free system."""


class Sequential(OpticalSystem):

    """A system where each element is positioned relative to the previous.

    Still a work in progress. Not even sure exactly how it should behave.
    """

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

    # def update(self):
    #     print "update"
    #     if not self.sources:
    #         return
    #     source = self.sources[0]
    #     position = source.position
    #     rotation = source.rotation
    #     ray = Ray(origin=position,
    #               direction=source.globalize_direction(source.axis))
    #     for i, element in enumerate(self.elements):
    #         print "updating element %d" % i
    #         element.position = position
    #         element.rotation = rotation
    #         new_ray = element.propagate(ray)
    #         if new_ray is None:
    #             print "missed element %d" % i
    #             return False

    #         npor = ray.direction.cross(new_ray.direction)
    #         # normal to plane of reflection
    #         x_angle = ray.direction.angle(new_ray.direction)
    #         if npor.dot(element.x_axis()) > 0:
    #             x_angle = - x_angle
    #         print "angle", x_angle
    #         y_angle = element.rotation.y + element.alignment.y
    #         z_angle = element.rotation.z + element.alignment.z
    #         rot = Vec(x_angle, y_angle, z_angle)
    #         rotmat = Mat().rotate(rotation)
    #         rotmat2 = Mat().rotate(rot)
    #         position = element.position + element.offset.transform(rotmat)
    #         rotation += rot
    #         ray = new_ray

    def update(self):
        if not self.sources:
            return
        source = self.sources[0]
        position = source.position
        rotation = source.rotation
        ray = Ray(origin=position,
                  direction=source.globalize_direction(source.axis))
        for i, element in enumerate(self.elements):
            element.position = position
            element.rotation = rotation
            new_ray = element.propagate(ray)
            if new_ray is None:
                return
            npor = ray.direction.cross(new_ray.direction)
            angle = ray.direction.angle(new_ray.direction)
            #position = element.position + element.offset.transform(Mat().rotate(rotation))
            #rotation = rotation + Mat().rotateAxis(angle, npor).decompose()[1]

            ray = new_ray
