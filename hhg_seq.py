from math import *
import phoray
from vector import Vector
import beam4
from shay import wl

def along(ray, dist):
    return ray.endpoint+ray.direction*dist

r_m = 0.4
theta_m = radians(3)

#toroids
R1 = 1/((1/r_m)*cos(pi/2-theta_m)/2)
rho1 = 1/((1/r_m)*1/(2*cos(pi/2-theta_m)))
C1 = -1/R1
Cx1 = -1/rho1
asph1=None

#paraboloid
a1p = r_m*sin(2*theta_m)/(2*tan(theta_m)) - r_m*cos(2*theta_m)
A1p = 1/(2*r_m*sin(2*theta_m)*tan(theta_m))
C1p=-A1p
Cx1p=None
asph1p=-1

E = 38.75
E2 = 35.63
wavel1 = float(wl(E))*1e-9
alt = radians(3.5)
theta = degrees(asin(1*wavel1*400e3/(2*sin(radians(3.5)))))
m = 1
ldensity = 400e3

# Define a starting ray as optical axis, along Z direction
r = phoray.Ray(Vector(0,0,0), Vector(0,0,1))

# A simple plane to serve as mirrors
p = phoray.Plane()

# First mirror
d_m1 = 0.4
theta_m1 = radians(3)
angle_m1 = pi/2 - theta_m1
m1=phoray.SimpleMirror(p, along(r, d_m1), Vector(angle_m1,0,0))
r1 = m1.propagate(r)
#print r1

# Grating
d_m2 = 0.2
theta_m2 = radians(-3.5)
angle_m2 = -2*theta_m1-(pi/2+theta_m2)
m2=phoray.SimpleMirror(p, along(r1, d_m2), Vector(angle_m2,0,0))
r2 = m2.propagate(r1)
#print r2

# refoc mirror
d_m3 = 0.2
theta_m3 = radians(3)
#88
angle_m3 = -(2*theta_m1+2*theta_m2)+(pi/2-theta_m3)
m3=phoray.SimpleMirror(p, along(r2, d_m3), Vector(angle_m3,0,0))
r3 = m3.propagate(r2)
#print r3

# slit
d_sl = 0.4
angle_sl = radians(-5)
sl = phoray.SimpleMirror(p, along(r3, d_sl), Vector(angle_sl,0,0))

##### m4 (collim) ######

d_m4 = 0.5
theta_m4 = radians(7)
angle_m4 = -(2*theta_m1+2*theta_m2+2*theta_m3)+(pi/2-theta_m4)
angle_m4p = pi-(2*theta_m1+2*theta_m2+2*theta_m3+2*theta_m4)

#toroid
d_out4 = 1.05
R4 = 1/((1/d_m4+1/d_out4)*cos(pi/2-theta_m4)/2)
rho4 = 1/((1/d_m4+1/d_out4)*1/(2*cos(pi/2-theta_m4)))
C4 = -1/R4
Cx4 = -1/rho4
asph4=None

#paraboloid
a4p = d_m4*sin(2*theta_m4)/(2*tan(theta_m4)) - d_m4*cos(2*theta_m4)
A4p = 1/(2*d_m4*sin(2*theta_m4)*tan(theta_m4))
C4p=-1/(2*a4p)
Cx4p=None
asph4p=-1

m4=phoray.SimpleMirror(p, along(r3, d_sl+d_m4), Vector(angle_m4,0,0))
r4 = m4.propagate(r3)

###### m5 (refoc2) ######
d_m5 = 1.7
d2_m5 = 0.20
d_in5 = 10000000000
#theta_m5 = radians(176)
theta_m5 = radians(4)
angle_m5p = (2*theta_m1+2*theta_m2+2*theta_m3+2*theta_m4+2*theta_m5)

R5 = 1/((1/d_in5+1/d2_m5)*cos(pi/2-theta_m5)/2)
rho5 = 1/((1/d_in5+1/d2_m5)*1/(2*cos(pi/2-theta_m5)))
C5 = -1/R5
Cx5 = -1/rho5
asph5=None

#paraboloid
a5p = d_m5*sin(2*theta_m5)/(2*tan(theta_m5)) - d2_m5*cos(2*theta_m5)
A5p = 1/(2*d_m5*sin(2*theta_m5)*tan(theta_m5))
C5p=-1/(2*a5p)
Cx5p=None
asph5p=-1

theta_m5 = radians(174)
angle_m5 = -(2*theta_m1+2*theta_m2+2*theta_m3+2*theta_m4)+(pi/2-theta_m5)
m5=phoray.SimpleMirror(p, along(r4, d_m5), Vector(angle_m5,0,0))
r5 = m5.propagate(r4)

# detector
d_det = d2_m5
angle_det = -(2*theta_m1+2*theta_m2+2*theta_m3+2*theta_m4+2*theta_m5)
det = phoray.SimpleMirror(p, along(r5, d_det), Vector(angle_det,0,0))

print 7
print beam4.make_beam4_table(
    ("X", "Y", "Z", "Tilt", "Pitch", "Roll",
     "Cx", "C", "Asph", "Gx", "Ord", "Type", "Dx", "Dy", "offOy", "Form"),
    (
        #m1
        (m1.position.x, m1.position.y, m1.position.z,
         degrees(m1.rotation.x), 0, 0,
         Cx1, C1, asph1, None, None, "mirror", 0.01, 0.05, None, "S"),
        #m2/gr
        (m2.position.x, m2.position.y, m2.position.z,
         degrees(m2.rotation.x), theta, 0,
         None, None, None, ldensity, 1, "mirror", 0.01, 0.05, None, "S"),
        #m3
        (m3.position.x, m3.position.y, m3.position.z,
         degrees(m3.rotation.x), 0, 0,
         Cx1, C1, asph1, None, None, "mirror", 0.01, 0.05, None, "S"),
        # slit
        (sl.position.x, sl.position.y, sl.position.z,
         degrees(sl.rotation.x), 0, 0,
         0, 0, None, None, None, "iris", 50e-6, 0.05, None, "S"),
        #m4
        (sl.position.x, sl.position.y-a4p*sin(angle_m4p), sl.position.z+a4p*cos(angle_m4p),
         degrees(angle_m4p), 0, 0,
         Cx4p, C4p, asph4p, None, None, ("mirror", ">"), 0.01, 0.005, 0.121, "S"),
        #m5
        (m5.position.x, m5.position.y, m5.position.z,
         degrees(m5.rotation.x), 0, 0,
         Cx5, C5, asph5, None, None, "mirror", 0.01, 0.05, None, "S"),
        #det
        (det.position.x, det.position.y, det.position.z,
         degrees(det.rotation.x), 0, 0,
         0, 0, None,  None, None, "exit", 0.05, 0.05, None, None),

        ),
    width=15
    )
