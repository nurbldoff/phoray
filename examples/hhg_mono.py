from __future__ import division
#import phoray as ph
from vector import Vector
import rowland, ray_graze
from math import *
from random import random

# Grating
altitude = radians(3)
rho = 400e3  # lines/m
#theta = lambda energy: asin(wl(energy)*rho/(2*sin(altitude)))
theta = radians(10)
d_source = 1.0
E = 100
deltaE = 1
wl = lambda E: 1.24e-6/E

theta_m = asin(1*wl(E)*rho/sin(altitude) - sin(theta))
print "theta_m (theory):", degrees(theta_m)

d_source=1.0

x_source = -d_source*sin(altitude)*cos(pi/2-theta)
y_source = d_source*sin(altitude)*sin(pi/2-theta)
z_source = -d_source*cos(altitude)

p = ph.Plane()
pg = ph.Grating(p, position=Vector(0., 0., 0.),
                rotation=Vector(0, 0, 0),
                surface_offset=Vector(0., 0., 0),
                d=1/rho, order=1)

det = ph.Mirror(p, position=Vector(-z_source,0,0),
                rotation=Vector(0,pi/2,0))

# r0 = ph.Ray(ph.Vector(x_source, y_source, z_source),
#             ph.Vector(-x_source, -y_source, -z_source), wl(E))

rays=[]

x_offset=0
y_offset=0
z_offset=0


for wavelength in np.arange(1.24e-8, 7.24e-8, 1.0e-8):
    a0 = ph.Ray(Vector(z_source+z_offset, x_source+x_offset, y_source+y_offset),
                Vector(-z_source, -x_source, -y_source), wl(E))
    #a0.wavelength = wl(energy)
    a0.wavelength = wavelength
    x_offset += 0
    print "a0:", a0
    a1 = pg.propagate(a0)
    print "a1:", a1
    a2 = det.propagate(a1)
    rays.append((a0, a1, a2))
