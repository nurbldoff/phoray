from math import *
import phoray
from vector import Vector
import beam4
from shay import wl
#from quantities import m, mm, radian, degree, sin, cos, tan

def along(ray, dist):
    return ray.endpoint+ray.direction*dist

def angleto(ray, angle):
    if angle < 0:
        return -pi/2 - atan(ray.direction.y/ray.direction.z) - angle
    else:
        return pi/2 - atan(ray.direction.y/ray.direction.z) - angle

def paraboloid(r, alpha):
    #ap = r*sin(2*alpha)/(2*tan(alpha)) - r*cos(2*alpha)
    Ap = 1/(2*r*sin(2*alpha)*tan(alpha))   # z = Ap*x^2
    a = r*sin(2*alpha)/(2*tan(alpha)) - r*cos(2*alpha) #shortest distance focus - mirror
    return 1/(4*Ap), -2*Ap  # Ap = C/2 (see BEAM4 manual p.31)

def standa_params(d, theta, L, a):
    CA = L*sin(theta)
    ZR = d*sin(2*theta)
    PFL = a
    return PFL, ZR, CA

E = 38.75
E2 = 35.63
wavel1 = float(wl(E))*1e-9

# Define a starting ray as optical axis, along Z direction
r = phoray.Ray(Vector(0,0,0), Vector(0,0,1))

# A simple plane to serve as mirrors
p = phoray.Plane()

# --------- M1
d_m1 = 0.4
alpha_m1 = radians(3)

a1, C1 = paraboloid(d_m1, alpha_m1)
#a1 *= 2
tilt_m1 = 2*alpha_m1

theta_m1 = pi/2 + alpha_m1
m1 = phoray.SimpleMirror(p, along(r, d_m1), Vector(angleto(r, -alpha_m1),0,0))
r1 = m1.propagate(r)


###print r1

# --------- GR
d_gr = 0.2
alpha_gr = radians(3.5)
tilt_gr = pi/2-(tilt_m1-alpha_gr)


alt = radians(3.5)
m = 1
ldensity = 400e3
theta = degrees(asin(m*wavel1*ldensity/(2*sin(alt))))


#theta_gr = -(pi/2 + alpha_gr)
gr = phoray.SimpleMirror(p, along(r1, d_gr), Vector(angleto(r1, alpha_gr), 0, 0))
r2 = gr.propagate(r1)

#print r2

# --------- M2
d_m2 = 0.2
f_m2 = 0.2
alpha_m2 = radians(3)
a2, C2 = paraboloid(f_m2, alpha_m2)
#a2 *= 2
tilt_m2 = tilt_m1-2*alpha_gr
m2 = phoray.SimpleMirror(p, along(r2, d_m2), Vector(angleto(r2, -alpha_m2),0,0))
r3 = m2.propagate(r2)


# --------- SL
d_sl = f_m2
sl = phoray.SimpleMirror(p, along(r3, d_sl), Vector(angleto(r3,pi/2),0,0))

#print r3


# --------- M3
d_m3 = 0.6
alpha_m3 = radians(7)

a3, C3 = paraboloid(d_m3, alpha_m3)
#a3 *= 2
tilt_m3 = tilt_m2+2*alpha_m2-2*alpha_m3

theta_m1 = pi/2 + alpha_m1
m3 = phoray.SimpleMirror(p, along(r3, d_sl+d_m3), Vector(angleto(r3, alpha_m3),0,0))
r4 = m3.propagate(r3)

# --------- M4
d_m4 = 2.0
f_m4 = 0.4
alpha_m4 = radians(7)
a4, C4 = paraboloid(f_m4, alpha_m4)
#a4 *= 2
tilt_m4 = tilt_m3
m4 = phoray.SimpleMirror(p, along(r4, d_m4), Vector(angleto(r4, -alpha_m4),0,0))
r5 = m4.propagate(r4)

#print r3

# --------- detector
d_det = f_m4
det = phoray.SimpleMirror(p, along(r5, d_det), Vector(angleto(r5, pi/2),0,0))

##Standa parameters
# print "M1: "+", ".join(["%s = %.5E"%x for x in zip(["PFL", "ZR", "CA"], standa_params(d_m1, alpha_m1, 0.075, a1))])
# print "M2: "+", ".join(["%s = %.5E"%x for x in zip(["PFL", "ZR", "CA"], standa_params(f_m2, alpha_m2, 0.075, a2))])
# print "M3: "+", ".join(["%s = %.5E"%x for x in zip(["PFL", "ZR", "CA"], standa_params(d_m3, alpha_m3, 0.075, a3))])
# print "M4: "+", ".join(["%s = %.5E"%x for x in zip(["PFL", "ZR", "CA"], standa_params(f_m4, alpha_m4, 0.075, a4))])



print 7
print beam4.make_beam4_table(
    ("X", "Y", "Z", "Tilt", "Pitch", "Roll",
     "Cx", "C", "Asph", "Gx", "Ord", "Type", "Dx", "Dy", "offOy", "Form"),
    (
        #m1
        (r.endpoint.x, r.endpoint.y+a1*sin(tilt_m1), r.endpoint.z-a1*cos(tilt_m1),
         degrees(tilt_m1), 0, 0,
         None, -C1, -1, None, None, "mirror", 0.01, 0.10, None, "S"),
        #gr
        (gr.position.x, gr.position.y, gr.position.z,
         degrees(gr.rotation.x), theta, 0,
         None, None, None, ldensity, 1, "mirror", 0.01, 0.05, None, "S"),
        #m2
        (sl.position.x, sl.position.y-a2*sin(tilt_m2), sl.position.z+a2*cos(tilt_m2),
         degrees(tilt_m2), 0, 0,
         None, C2, -1, None, None, "mirror", 0.01, 0.05, None, "S"),
        # slit
        (sl.position.x, sl.position.y, sl.position.z,
         degrees(sl.rotation.x), 0, 0,
         0, 0, None, None, None, "iris", 50e-6, 0.05, None, "S"),
        #m3
        (sl.position.x, sl.position.y+a3*sin(tilt_m3), sl.position.z-a3*cos(tilt_m3),
         degrees(tilt_m3), 0, 0,
         None, -C3, -1, None, None, ("mirror", ">"), 0.01, 0.35, None, "S"),
        #m4
        (det.position.x, det.position.y-a4*sin(tilt_m4), det.position.z+a4*cos(tilt_m4),
         degrees(tilt_m4), 0, 0,
         None, C4, -1, None, None, "mirror", 0.01, 0.25, None, "S"),
        # #det
        (det.position.x, det.position.y, det.position.z,
         degrees(det.rotation.x), 0, 0,
         0, 0, None,  None, None, "exit", 0.05, 0.05, None, None),
        ),
    width=15
    )
