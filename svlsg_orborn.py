"""
Osborn and Callcott, 1996
"""
from __future__ import division
from phoray import *
import rowland, ray_graze
from math import *
from random import random


angle=2
energy = 425
dE = 10
wl = 1.24e-6/energy
#row = rowland.Rowland(5.0, 1200, angle)
order = -1

# Source
d_gr = 0.5  #m
theta_gr = radians(2)
sx = -d_gr*cos(theta_gr)
sy = d_gr*sin(theta_gr)

# Grating
R = 14.3  #m
s=Sphere(R, 0.025, 0.06)
a0, a1, a2, a3 = 2200, 678e-2, 20.3e-3, 5.00e-5
sg = SphericalVLSGrating(an=(a0, a1, a2, a3), d=None, order=order,
                         surface=s, position=Vector(0.,0.,0.),
                         rotation=Vector(0.,0.,0.), surface_offset=Vector(0.,0.,R))

# Detector
def det_pos(photon_energy, R_gr, d_gr, theta_gr, a0, a1):
    """
    Calculate the detector position from energy and grating parameters
    """
    diff_order = 1

    R_gr *= 1000
    d_gr *= 1000

    wavelength = 1000 * 6.626068e-34*2.9979e8/(photon_energy*1.60217e-19)
    alpha = radians(90 - theta_gr)
    beta = asin( sin(alpha) - diff_order * wavelength * a0 )
    # d_det = np.cos(beta)**2 / ((np.cos(alpha) + np.cos(beta))/R_gr - np.cos(alpha)**2/d_gr +
    #                            (np.sin(alpha)-np.sin(beta))*a1/a0)
    d_det = cos(beta)**2 / ( (cos(alpha)+cos(beta))/R_gr - cos(alpha)**2/d_gr +
                             (sin(alpha)-sin(beta))/a0 * a1 )
                             #diff_order * wavelength * a1 )



    #d_det = cos(beta)**2 / (cos(beta)/R_gr+(sin(alpha)-sin(beta))*a1/a0)

    det_x = sin(beta)*d_det
    det_y = cos(beta)*d_det

    det_angle = atan( cos(beta) * 1/(2*sin(beta)-d_det*(tan(beta)/R_gr+a1/a0)))

    return (det_x/1000, det_y/1000, d_det/1000, beta, det_angle)

p = Plane()
detx, dety, r_det, beta, det_angle = det_pos(energy, R, d_gr, 2, a0, a1)
pm = Detector(surface=p, position=Vector(0, detx, dety),
            rotation=Vector((pi/2-beta+det_angle),0.,0.))
           # Vector(pi/2, 0,0))
print 2*atan(dety/detx)
#r0 = Ray(Vector(0, row.source_x, row.source_y),
#         Vector(0, cos(radians(angle)), -sin(radians(angle))), wl)
#r1 = sg.propagate(r0)
#r2 = pm.propagate(r1)
xdisp = 0.025
ydisp = 0.004
xslit = 15e-6
yslit = 15e-6

rays = []
image =  []
footprint = []

N = 10000

for E in [energy-dE, energy, energy+dE]:
    wl = 6.626068e-34*2.9979e8/(E*1.60217e-19)
    r0 = Ray(Vector(0, sx, sy),
             Vector(0, cos(theta_gr), -sin(theta_gr)), wl)
    for i in xrange(N):
        #d=disp/2
        a0 = r0.deviate(Vector(ydisp*random()-ydisp/2,
                               0, xdisp*random()-xdisp/2))
        a0 = a0.translate(Vector(xslit*random()-xslit/2, 0, yslit*random()-yslit/2))
        #a0 = r0
        a1 = sg.propagate(a0)
        a2 = pm.propagate(a1)
        #print "a0:",a0, "a1:",a1, "a2:",a2
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

print "N_succ:", len(rays)

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

