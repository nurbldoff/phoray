#from __future__ import division
from phoray import *
import rowland
from math import *
from random import random



angle=2
energy = 500
dE = 1
wl = 1.24e-6/energy
row = rowland.Rowland(5.0, 1200, angle)
order = -1

# Grating
s=Sphere(5.0, 0.03, 0.05)
sg = Mirror(d=1/1200e3, order=order, surface=s, position=Vector(0.,0.,0.),
            rotation=Vector(0.,0.,0.), surface_offset=Vector(0.,0.,5.0))

# Detector
p = Plane()
detx, dety = row.add_ray(energy, order, 0)
pm = Detector(surface=p, position=Vector(0, detx, dety),
            rotation=Vector(2*atan(dety/detx),0.,0.))
           # Vector(pi/2, 0,0))
print 2*atan(dety/detx)
#r0 = Ray(Vector(0, row.source_x, row.source_y),
#         Vector(0, cos(radians(angle)), -sin(radians(angle))), wl)
#r1 = sg.propagate(r0)
#r2 = pm.propagate(r1)
xdisp = 1.5
ydisp = 0.1
xslit = 0.
yslit = 0.

rays = []
image =  []
footprint = []

for E in [energy-dE, energy, energy+dE]:
    wl = 1.24e-6/E
    r0 = Ray(Vector(0, row.source_x, row.source_y),
             Vector(0, cos(radians(angle)), -sin(radians(angle))), wl)
    for i in xrange(10000):
        #d=disp/2
        a0 = r0.deviate(Vector(ydisp*random()-ydisp/2,
                               xdisp*random()-xdisp/2, 0))
        a0 = a0.translate(Vector(xslit*random()-xslit/2, yslit*random()-yslit/2, 0))
        a1 = sg.propagate(a0)
        a2 = pm.propagate(a1)
        if not None in (a0, a1, a2):
            rays.append([(a0.endpoint.x, a0.endpoint.y, a0.endpoint.z),
                         (a1.endpoint.x, a1.endpoint.y, a1.endpoint.z),
                         (a2.endpoint.x, a2.endpoint.y, a2.endpoint.z)])
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

