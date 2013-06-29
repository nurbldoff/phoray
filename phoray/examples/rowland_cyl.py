from __future__ import division
import phoray as ph
import rowland, ray_graze
from math import *
from random import random

"""
Y is pointing up (=y in the rowland representation)
Z is horizontal, away from the sample. (=x in the rowland representation)
Origin is at the middle of the grating
"""

angle=2
energy = 500
dE = .5
wl = 1.24e-6/energy
row = rowland.Rowland(5.0, 1200, angle)
order = 1

# Grating
s=ph.Sphere(5.0, 0.03, 0.05)
#s = ph.Cylinder(5.0, 0.03, 0.05)
sg = ph.Grating(s, ph.Vector(0., 0., 0.), ph.Vector(pi/2, 0, 0.),
             ph.Vector(0., 0., -5.0), 1/1200e3, order)

# Detector
p = ph.Plane()
detx, dety = row.add_ray(energy, -order, 0)
pm = ph.Detector(p, ph.Vector(0, dety, detx),
                 #ph.Vector(0, 0., 0))
                 ph.Vector(pi/2-2*atan(dety/detx),0., 0))
           # Vector(pi/2, 0,0))
print 2*atan(dety/detx)
#r0 = Ray(Vector(0, row.source_x, row.source_y),
#         Vector(0, cos(radians(angle)), -sin(radians(angle))), wl)
#r1 = sg.propagate(r0)
#r2 = pm.propagate(r1)
xdisp = 0.1
ydisp = 0.007
xslit = 0.001
yslit = 0.00001

points = []
rays = []
image =  []
footprint = []

for E in [energy-dE, energy, energy+dE]:
    wl = 1.24e-6/E
    r0 = ph.Ray(ph.Vector(0, row.source_y, row.source_x),
             ph.Vector(0, -sin(radians(angle)), cos(radians(angle))), wl)
    for i in xrange(1000):
        #d=disp/2
        a0 = r0.deviate(ph.Vector(ydisp*random()-ydisp/2, xdisp*random()-xdisp/2, 0))
        a0 = a0.translate(ph.Vector(xslit*random()-xslit/2, yslit*random()-yslit/2, 0))
        a1 = sg.propagate(a0)
        a2 = pm.propagate(a1)
        if not None in (a0, a1):
            rays.append((a0, a1, a2))
            points.append([(a0.endpoint.y, a0.endpoint.z),
                         (a1.endpoint.y, a1.endpoint.z),
                         (a2.endpoint.y, a2.endpoint.z)])
        if a1 is not None:
            pt=sg.localize(a1).endpoint
            footprint.append([pt.x, pt.y, E])
        if a2 is not None:
            pt=pm.localize(a2).endpoint
            image.append([pt.x, pt.y, E])

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
