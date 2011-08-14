from __future__ import division
from phoray import *
from math import *
from random import random


# Cylindrical mirror, vertical
#c = Cylinder(1.0, 1.0, 1.0)
R=14.47
d=0.4

s = Sphere(R, 1.0, 1.0)
p = Plane()
cm = Mirror(s, Vector(d,0,0), Vector(0,pi-radians(3) ,0), Vector(0,0,-R))

rays = []
image = []
footprint = []

r0 = Ray(Vector(0,0,0), Vector(1.0,0,0))

dev=.05

#d=disp/2
n=3
for i in range(n):
    a0 = r0.deviate(Vector(0, i*dev/n-dev/2, 0))
    a1 = cm.propagate(a0)
    rays.append([a0, a1])

    if a1 is not None:
        pt=cm.localize(a1).endpoint
        footprint.append([pt.x, pt.y])

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
