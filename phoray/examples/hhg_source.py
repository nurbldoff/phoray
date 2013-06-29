import beam4
import scipy
from math import *
from shay import wl
from quantities import m

E = 27.0
E2 = 28

fwhm = 30e-6

n=800


s1 = beam4.gaussian_source((0, 0, 0), (fwhm/2.35, fwhm/2.35, 0.01),
                           (0, 0, 1), (4e-3/2.35, 4e-3/2.35, 0.01),
                           E, 0.0,
                           n)
s2 = beam4.gaussian_source((0, 0, 0), (fwhm/2.35, fwhm/2.35, 0.01),
                           (0, 0, 1), (4e-3/2.35, 4e-3/2.35, 0.01),
                           E2, 0.0,
                           n)

s1 = zip(s1[0], s1[1], s1[2])
s2 = zip(s2[0], s2[1], s2[2])

p1 = []
p2 = []

for a in s1:
    line = []
    line.extend(a[0])
    line.extend(a[1])
    line.extend(((float(wl(a[2][0]).rescale(m)), "r"), 1, None, None, None))
    p1.append(line)

for a in s2:
    line = []
    line.extend(a[0])
    line.extend(a[1])
    line.extend(((float(wl(a[2][0]).rescale(m)), "b"), 1, None, None, None))
    p2.append(line)

r = beam4.make_beam4_table(
("X0", "Y0", "Z0", "U0", "V0", "W0", "@wavel", "Order", "Xfinal", "Yfinal", "Notes"),
p1+p2, 15
)
#print p1

print 2*n
print r
