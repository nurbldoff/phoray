#from __future__ import division
import phoray as ph
#import rowland, ray_graze
from math import *
from random import random
import numpy as np

from rowland import lines_intersect

angle = radians(87)

# Ellipse
r1 = .700
r2 = 10-r1
a = (r1+r2)/2   # a is half-axis, always true for an ellipse
f = sqrt(r1**2 + r2**2 - 2*r1*r2*cos(2*angle)) / 2   # from law of cosines
b = sqrt(a**2-f**2)
c = 1.e9  # doesn't matter

theta = asin(r2*sin(2*angle)/(2*f))
phi = asin(r1*sin(2*angle)/(2*f))

energy = 500
dE = .5
wl = 1.24e-6/energy

# Elliptical mirror
e = ph.Ellipsoid(a,b,c)
em = ph.SimpleMirror(surface=e, position=ph.Vector(0,0,0), rotation=ph.Vector(0,0,0))

# Detector
p = ph.Plane()
#detx, dety = row.add_ray(energy, -order, 0)
det = ph.Detector(surface=p, position=ph.Vector(f, 0, 0),
                 rotation=ph.Vector(0, 0., pi/2-phi))

dthetas=np.linspace(radians(-.15), radians(.15), 3)

pts=[]
for dtheta in dthetas:
    a0 = ph.Ray(origin=ph.Vector(-f, 0, 0),
                direction=ph.Vector(cos(theta+dtheta), sin(theta+dtheta), 0), wavelength=wl)
    a1 = em.propagate(a0)
    #print "a0:", a0
    #print "a1:", a1
    a2=a1.endpoint+a1.direction*11.0
    pts.append([[a0.endpoint.x, a0.endpoint.y],
                [a1.endpoint.x, a1.endpoint.y],
                [a2.x, a2.y]])

pts2=[]
for dtheta in dthetas:
    a0 = ph.Ray(origin=ph.Vector(-f, 500e-6, 0),
                direction=ph.Vector(cos(theta+dtheta), sin(theta+dtheta), 0), wavelength=wl)
    a1 = em.propagate(a0)
    #print "a0:", a0
    #print "a1:", a1
    a2=a1.endpoint+a1.direction*11.0
    pts2.append([[a0.endpoint.x, a0.endpoint.y],
                [a1.endpoint.x, a1.endpoint.y],
                [a2.x, a2.y]])

pts3=[]
for dtheta in dthetas:
    a0 = ph.Ray(origin=ph.Vector(-f, -500e-6, 0),
                direction=ph.Vector(cos(theta+dtheta), sin(theta+dtheta), 0), wavelength=wl)
    a1 = em.propagate(a0)
    #print "a0:", a0
    #print "a1:", a1
    a2=a1.endpoint+a1.direction*11.0
    pts3.append([[a0.endpoint.x, a0.endpoint.y],
                [a1.endpoint.x, a1.endpoint.y],
                [a2.x, a2.y]])

#a2 = det.propagate(a1)

pts=np.array(pts)
cline = pts[len(pts)/2]

k0 = (cline[-1][1]-cline[-2][1]) / (cline[-1][0]-cline[-2][0])
m0 = cline[-2][1] - cline[-2][0]*k0
pts_foci = []

for line in pts:
    # find a reasonable approximation of the best focus...
    k1 = (line[-1][1]-line[-2][1]) / (line[-1][0]-line[-2][0])
    m1 = line[-2][1] - line[-2][0]*k1
    f = lines_intersect(k0,m0,k1,m1)
    if f is not None:
        pts_foci.append(np.array(f))
pts_foci = np.array(pts_foci).T


pts2=np.array(pts2)
cline = pts2[len(pts2)/2]

k0 = (cline[-1][1]-cline[-2][1]) / (cline[-1][0]-cline[-2][0])
m0 = cline[-2][1] - cline[-2][0]*k0
pts2_foci = []

for line in pts2:
    # find a reasonable approximation of the best focus...
    k1 = (line[-1][1]-line[-2][1]) / (line[-1][0]-line[-2][0])
    m1 = line[-2][1] - line[-2][0]*k1
    f = lines_intersect(k0,m0,k1,m1)
    if f is not None:
        pts2_foci.append(np.array(f))
pts2_foci = np.array(pts2_foci).T

pts3=np.array(pts3)
cline = pts3[len(pts3)/2]

k0 = (cline[-1][1]-cline[-2][1]) / (cline[-1][0]-cline[-2][0])
m0 = cline[-2][1] - cline[-2][0]*k0
pts3_foci = []

for line in pts3:
    # find a reasonable approximation of the best focus...
    k1 = (line[-1][1]-line[-2][1]) / (line[-1][0]-line[-2][0])
    m1 = line[-2][1] - line[-2][0]*k1
    f = lines_intersect(k0,m0,k1,m1)
    if f is not None:
        pts3_foci.append(np.array(f))
pts3_foci = np.array(pts3_foci).T



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
