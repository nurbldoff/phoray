from math import *

from phoray.system import OpticalSystem
from phoray.element import ReflectiveGrating, Detector
from phoray.source import GaussianSource
from phoray.surface import Sphere, Plane
from phoray import Vec


class RowlandSpectrometer(OpticalSystem):

    """A system that simulates a Rowland spectrometer."""

    def __init__(self, radius=1.0, line_density=1.0e6, angle=10.0,
                 wavelength=1.0e-9, order=-1, sources=[], **kwargs):

        self.radius = radius
        self.line_density = line_density
        self.angle = angle
        self.wavelength = wavelength
        self.order = order

        entr_arm = radius * sin(radians(angle))
        sphere = Sphere(xsize=0.1, ysize=0.1, R=radius)
        grating = ReflectiveGrating(
            offset=Vec(0, 0, entr_arm),
            alignment=Vec(90 - angle, 0, 0),
            d=1. / line_density, order=order, geometry=sphere)

        exit_angle = degrees(acos(cos(radians(angle)) +
                                  order * wavelength * line_density))
        exit_arm = radius * sin(radians(exit_angle))
        plane = Plane(xsize=0.1, ysize=0.1)
        detector = Detector(
            # Setting position and rotation according to the grating...
            position=grating.offset, rotation=Vec(-(angle + exit_angle), 0, 0),
            # ...and using offset and alignment to position the detector
            # relative to the grating
            offset=Vec(0, 0, exit_arm), alignment=Vec(90 - exit_angle, 0, 0),
            geometry=plane)

        # This system will always consist of two elements; grating and
        # detector. They can only be changed by changing the system
        # properties.
        elements = [grating, detector]

        OpticalSystem.__init__(self, sources, **kwargs)
        for e in elements:
            self.add_element(e)
