from __future__ import division

# import pyximport
# pyximport.install(pyimport=True)

import csv

from numpy import array

#from phoray.minivec import Vec
#from phoray.ray import Ray
from phoray.surface import Sphere, Plane
from phoray.element import ReflectiveGrating, Detector
from phoray.source import GaussianSource
from phoray.system import OpticalSystem
import rowland2
from math import *

"""
Simulate a Rowland (spherical grating) spectrometer
"""

# parameters for a Rowland spectrometer, SI units unless otherwise stated
angle = 2        # incidence angle on the grating (degrees)
energy = 500     # center energy of the incident light (eV)
wl = 1.24e-6/energy      # ...sloppily converted into wavelength
order = -1       # diffraction order to look at
R = 5.0          # radius of the grating
d = 1200e3       # grating line density, lines/m

# Grating, centered at origin
s = Sphere(5.0, xsize=0.1, ysize=0.1)
sg = ReflectiveGrating(d=1/d, order=order, geometry=s,
                       rotation=array((90, 0, 0)))

# Detector
p = Plane(xsize=0.1, ysize=0.1)
row = rowland2.Rowland(R_gr=R,
                       d_gr=d/1000,
                       theta_in=angle)
detx, dety = row.add_ray(energy, order, 0)   # calculate the focal
print "source pos:", row.source_x, row.source_y
print "detector pos:", detx, dety
det = Detector(geometry=p, position=array((0, dety, detx)),
               rotation=array((90-degrees(2*atan(dety/detx)), 0., 0.)))


# Incoming light distribution
dE = 1.0        # energy difference between lines
xdisp = 0.1     # divergence angle in horizontal direction (sigma)
ydisp = 0.1     # vertical divergence
xslit = 0.      # horizontal entrance slit / source size (sigma)
yslit = 0.      # vertical size

srcs = [GaussianSource(position=array((0, row.source_y, row.source_x)),
                       rotation=array((angle, 0, 0)),
                       size=array((xslit, yslit, 0)),
                       divergence=array((xdisp, ydisp, 0)),
                       wavelength=1.24e-6 / en)
        for en in [energy-dE, energy, energy+dE]]

os = OpticalSystem(elements=[sg, det], sources=srcs)

n_rays = 10000   # number of rays

for i, t in os.trace(n_rays):
    pass

print "done"

with open("rowland.dat", "w") as f:
    w = csv.writer(f, delimiter="\t")
    for energy in os.elements[-1].footprint.values():
        for pt in energy:
            w.writerow(pt)


# for E in
#     wl = 1.24e-6/E

#     # Create an initial ray to start with
#     r0 = Ray(origin = Vec(0, row.source_x, row.source_y),
#              direction = Vec(0, cos(radians(angle)), -sin(radians(angle))),
#              wavelength = wl)

#     # loop over each ray to calculate
#     for i in xrange(n_rays//3):
#         # Randomly distribute the initial ray over the slit and dispersion
#         # according to a simple box distribution (equal probability)
#         a0 = r0.deviate(Vec(ydisp*random()-ydisp/2,
#                                xdisp*random()-xdisp/2, 0))
#         a0 = a0.translate(Vec(xslit*random()-xslit/2, yslit*random()-yslit/2, 0))
#         a1 = sg.propagate(a0)
#         a2 = pm.propagate(a1)

#         # # Keep only the rays that make it to the detector
#         # if not None in (a0, a1, a2):
#         #     rays.append([(a0.endpoint.x, a0.endpoint.y, a0.endpoint.z),
#         #                  (a1.endpoint.x, a1.endpoint.y, a1.endpoint.z),
#         #                  (a2.endpoint.x, a2.endpoint.y, a2.endpoint.z)])

#         # # "footprint" image on the grating
#         # if a1 is not None:
#         #     pt=sg.localize(a1).endpoint
#         #     footprint.append([pt.x, pt.y, E])

#         # # detector image
#         # if a2 is not None:
#         #     pt=pm.localize(a2).endpoint
#         #     image.append([pt.x, pt.y, E])

#print len(image)

# Run the same thing in the RAY program, for comparison

# ray_graze.graze(xslit, yslit, 0.05, 0.01,
#                 energy, 2*dE,
#                 5.0, 1200e3, 2, 1,
#                 0.05, 0.03,
#                 0, 0, 0,
#                 4, 1,
#                 0.040, 0.0440,
#                 False,
#                 0,0,0,0,0,0,0,
#                 30000,
#                 0, True,
#                 "grazetest_")
