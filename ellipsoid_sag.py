from __future__ import division
import phoray as ph
import rowland, ray_graze
from math import *
from random import random
import numpy as np

"""
"""

angle = radians(3)

# Ellipse, sagittal focusing
r1 = .700
r2 = 10.0-r1

a = 1e19   # ~plane ellipse
b = sin(angle)*(r1+r2)/2
f = b-r1*sin(angle)
c = sqrt(b**2-f**2)

#theta = asin(r2*cos(2*angle)/(2*f))
#phi = asin(r1*cos(2*angle)/(2*f))

energy = 500
dE = .5
wl = 1.24e-6/energy

# Elliptical mirror
e = ph.Ellipsoid(a,b,c)
em = ph.Mirror(surface=e, position=ph.Vector(0,0,0), rotation=ph.Vector(0,0,0))

# Detector
p = ph.Plane()
# detx, dety = row.add_ray(energy, -order, 0)
det = ph.Detector(surface=p, position=ph.Vector(cos(angle)*(r1+r2)-100e-6, -f, 0),
                  rotation=ph.Vector(0, pi/2-angle, 0))

dthetas=np.linspace(radians(-.025), radians(.025), 20)

pts=[]
pts2=[]
img=[]
img2=[]
for dtheta in dthetas:
    a0 = ph.Ray(origin=ph.Vector(0, f, 0),
                direction=ph.Vector(cos(angle), sin(angle), sin(dtheta)), wavelength=wl)
    a1 = em.propagate(a0)
    print "a0:", a0
    print "a1:", a1
    a2 = det.propagate(a1)
    print "a2:", a2
    pts.append([[a0.endpoint.x, a0.endpoint.y, a0.endpoint.z],
                [a1.endpoint.x, a1.endpoint.y, a1.endpoint.z],
                [a2.endpoint.x, a2.endpoint.y, a2.endpoint.z]])
    pt=det.localize(a2).endpoint
    img.append([pt.x, pt.y, pt.z])


for dtheta in dthetas:
    a0 = ph.Ray(origin=ph.Vector(0, f, 50e-6),
                direction=ph.Vector(cos(angle), sin(angle), sin(dtheta)), wavelength=wl)
    a1 = em.propagate(a0)
    print "a0:", a0
    print "a1:", a1
    a2 = det.propagate(a1)
    print "a2:", a2
    pts2.append([[a0.endpoint.x, a0.endpoint.y, a0.endpoint.z],
                [a1.endpoint.x, a1.endpoint.y, a1.endpoint.z],
                [a2.endpoint.x, a2.endpoint.y, a2.endpoint.z]])
    pt=det.localize(a2).endpoint
    img2.append([pt.x, pt.y, pt.z])


# pts1=[]
# for dtheta in dthetas:
#     a0 = ph.Ray(origin=ph.Vector(-5, f, 50e-6),
#                 direction=ph.Vector(cos(angle), sin(angle), sin(dtheta)), wavelength=wl)
#     a1 = em.propagate(a0)
#     print "a0:", a0
#     print "a1:", a1
#     a2 = det.propagate(a1)
#     #a2=a1.endpoint+a1.direction*11.0
#     print "a2:", a2
#     pts1.append([[a0.endpoint.x, a0.endpoint.z],
#                 [a1.endpoint.x, a1.endpoint.z],
#                 [a2.endpoint.x, a2.endpoint.z]])
#     pt=det.localize_vector(a2.endpoint)
#     img.append([pt.x, pt.y])


#a2 = det.propagate(a1)

pts=np.array(pts)
pts2=np.array(pts2)
img=np.array(img)
img2=np.array(img2)

xdisp = 0.
ydisp = 0.
xslit = 0.0
yslit = 0.0

points = []
rays = []
image =  []
footprint = []

# for i in xrange(3):
#     #d=disp/2
#     #a0 = r0.deviate(ph.Vector(ydisp*random()-ydisp/2, xdisp*random()-xdisp/2, 0))
#     #a0 = a0.translate(ph.Vector(xslit*random()-xslit/2, yslit*random()-yslit/2, 0))
#     a0 = r0
#     a1 = em.propagate(a0)
#     print "a1:", a1
#     a2 = det.propagate(a1)
#     print "a2:", a2
#     if not None in (a0, a1, a2):
#         rays.append((a0, a1, a2))
#         points.append([(a0.endpoint.x, a0.endpoint.y),
#                        (a1.endpoint.x, a1.endpoint.y),
#                        (a2.endpoint.x, a2.endpoint.y),])

#     if a2 is not None:
#         pt=det.localize(a2).endpoint
#         image.append([pt.x, pt.y, 0])

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
