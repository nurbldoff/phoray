
from __future__ import division
from phoray import *
from math import *
from random import random

angle=10
s_dist = .500
energy = 100
dE = 5
wl = 1.24e-6/energy
order = 1

# Grating
p=Plane(0.3, 0.1)
pg = Mirror(p, Vector(0.,0.,0.), Vector(0.,0.,pi/2),
             Vector(0.,0.,0), 1/(400e3), order)

# Detector
p = Plane()
pm = Mirror(p, Vector(0, 0, 0.5),
            Vector(-pi/2, 0., 0.))
           # Vector(pi/2, 0,0))

#r0 = Ray(Vector(0, row.source_x, row.source_y),
#         Vector(0, cos(radians(angle)), -sin(radians(angle))), wl)
#r1 = sg.propagate(r0)
#r2 = pm.propagate(r1)
xdisp = 1.5/100
ydisp = 0.1/100
xslit = 0.0001
yslit = 0.0001

rays = []
image =  []
footprint = []

for E in [energy-dE, energy, energy+dE]:
    wl = 1.24e-6/E
    r0 = Ray(Vector(0.02*s_dist, s_dist*sin(radians(angle)), -s_dist*cos(radians(angle))),
             Vector(-0.02, -sin(radians(angle)), cos(radians(angle))), wl)
    for i in xrange(10000):
        #d=disp/2
        #a0 = r0.deviate(Vector(ydisp*random()-ydisp/2,
        #                       xdisp*random()-xdisp/2, 0))
        a0 = r0.translate(Vector(xslit*random()-xslit/2, yslit*random()-yslit/2, 0))
        a1 = pg.propagate(a0)
        a2 = pm.propagate(a1)
        if not None in (a0, a1, a2):
            rays.append([(a0.endpoint.x, a0.endpoint.y, a0.endpoint.z),
                         (a1.endpoint.x, a1.endpoint.y, a1.endpoint.z),
                         (a2.endpoint.x, a2.endpoint.y, a2.endpoint.z)])
        if a1 is not None:
            pt=pg.localize(a1).endpoint
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
