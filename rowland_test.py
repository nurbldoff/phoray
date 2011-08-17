#from __future__ import division
from phoray import *
import rowland2
from math import *
from random import random

"""
Simulate a Rowland (spherical grating) spectrometer with optional entrance slit.
"""

# parameters for a Rowland spectrometer
angle = 2        # incidence angle on the grating
energy = 500     # center energy of the incident light (eV)
wl = 1.24e-6/energy      # ...sloppily converted into wavelength
order = -1       # diffraction order to look at
R = 5.0          # radius of the grating
d = 1200         # grating line density

# Grating, centered at origin
s = Sphere(5.0, 0.03, 0.05)
sg = Mirror(d=1/1200e3, order=order, surface=s, position=Vector(0.,0.,0.),
            rotation=Vector(0.,0.,0.), surface_offset=Vector(0.,0.,5.0))

# Detector
p = Plane()
row = rowland2.Rowland(R_gr=R,
                       d_gr=d,
                       theta_in=angle)
detx, dety = row.add_ray(energy, order, 0)   # calculate the focal point
pm = Detector(surface=p, position=Vector(0, detx, dety),
            rotation=Vector(2*atan(dety/detx),0.,0.))

# Incoming light distribution
dE = 1.0          # energy difference between lines
xdisp = 1.5     # dispersion angle in horizontal direction
ydisp = 0.1     # vertical dispersion
xslit = 0.      # horizontal entrance slit / source size
yslit = 0.      # vertical size

rays = []
image =  []
footprint = []
n_rays = 100000   # number of rays

for E in [energy-dE, energy, energy+dE]:
    wl = 1.24e-6/E

    # Create an initial ray to start with
    r0 = Ray(origin = Vector(0, row.source_x, row.source_y),
             direction = Vector(0, cos(radians(angle)), -sin(radians(angle))),
             wavelength = wl)

    # loop over each ray to calculate
    for i in xrange(n_rays):
        # Randomly distribute the initial ray over the slit and dispersion
        # according to a simple box distribution (equal probability)
        a0 = r0.deviate(Vector(ydisp*random()-ydisp/2,
                               xdisp*random()-xdisp/2, 0))
        a0 = a0.translate(Vector(xslit*random()-xslit/2, yslit*random()-yslit/2, 0))
        a1 = sg.propagate(a0)
        a2 = pm.propagate(a1)

        # Keep only the rays that make it to the detector
        if not None in (a0, a1, a2):
            rays.append([(a0.endpoint.x, a0.endpoint.y, a0.endpoint.z),
                         (a1.endpoint.x, a1.endpoint.y, a1.endpoint.z),
                         (a2.endpoint.x, a2.endpoint.y, a2.endpoint.z)])

        # "footprint" image on the grating
        if a1 is not None:
            pt=sg.localize(a1).endpoint
            footprint.append([pt.x, pt.y, E])

        # detector image
        if a2 is not None:
            pt=pm.localize(a2).endpoint
            image.append([pt.x, pt.y, E])


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

