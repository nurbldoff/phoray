from __future__ import division
from phoray import *
import rowland2
from math import *
from random import random, choice
import multiprocessing
import Queue


"""
Simulate a Rowland (spherical grating) spectrometer with optional entrance slit.
"""

# parameters for a Rowland spectrometer, SI units unless otherwise stated
angle = 2        # incidence angle on the grating (degrees)
energy = 500     # center energy of the incident light (eV)
wl = 1.24e-6/energy      # ...sloppily converted into wavelength
order = -1       # diffraction order to look at
R = 5.0          # radius of the grating
d = 1200e3       # grating line density, lines/m

# Grating, centered at origin
s = Sphere(5.0, 0.03, 0.05)
sg = Mirror(d=1/d, order=order, surface=s, position=Vector(0.,0.,0.),
            rotation=Vector(0.,0.,0.), surface_offset=Vector(0.,0.,5.0))

# Detector
p = Plane()
row = rowland2.Rowland(R_gr=R,
                       d_gr=d/1000,
                       theta_in=angle)
detx, dety = row.add_ray(energy, order, 0)   # calculate the focal point
pm = Detector(surface=p, position=Vector(0, detx, dety),
            rotation=Vector(2*atan(dety/detx),0.,0.))
system = (sg, pm)

# Incoming light distribution
dE = 1.0        # energy difference between lines
xdisp = 1.5     # dispersion angle in horizontal direction
ydisp = 0.1     # vertical dispersion
xslit = 0.      # horizontal entrance slit / source size
yslit = 0.      # vertical size

n_rays = 1000000   # number of rays

def trace(system, r0, wls, outq, n=10000):
    """This is the target function running in each process."""
    #s1, s2 = system
    results = []
    for i in xrange(n):
        newray = r0.deviate(Vector(ydisp*random()-ydisp/2,
                                   xdisp*random()-xdisp/2, 0)
                  ).translate(Vector(xslit*random()-xslit/2,
                                     yslit*random()-yslit/2, 0))
        newray.wavelength = choice(wls)
        for element in system:
            newray = element.propagate(newray)
        if newray is not None:
            pt = system[-1].localize(newray).endpoint
            results.append((pt.x, pt.y, newray.wavelength))
    outq.put(results)


if __name__ == '__main__':

    n_procs = 2
    wavelengths = [1.24e-6/E for E in (energy-dE, energy, energy+dE)]
    print wavelengths
    # Create an initial ray to start with
    r0 = Ray(origin = Vector(0, row.source_x, row.source_y),
              direction = Vector(0, cos(radians(angle)), -sin(radians(angle))),
              wavelength = wl)

    processes = []
    out_queue = multiprocessing.Queue()
    for i in xrange(n_procs):
        p = multiprocessing.Process(target=trace, args=(
            system, r0, wavelengths, out_queue, n_rays//n_procs))
        p.start()
        processes.append(p)

    results = []
    while processes:
        results += out_queue.get()
        for p in processes:
            if not p.is_alive():
                processes.remove(p)

    with open("rowland_test.dat", "w") as f:
        for point in results:
            f.write("%f\t%f\t%f\n" % point)
