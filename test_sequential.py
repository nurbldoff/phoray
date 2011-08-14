from math import *
import phoray
from vector import Vector
import beam4

def along(ray, dist):
    return ray.endpoint+ray.direction*dist

# Define a starting ray as optical axis, along Z direction
r = phoray.Ray(Vector(0,0,0), Vector(0,0,1))

# A simple plane to serve as mirrors
p = phoray.Plane()

# First mirror
d_m1 = 0.4
angle_m1 = radians(87)
m1=phoray.SimpleMirror(p, along(r, d_m1), Vector(angle_m1,0,0))
r1 = m1.propagate(r)
#print r1

# Grating
d_m2 = 0.2
angle_m2 = radians(-92.5)
m2=phoray.SimpleMirror(p, along(r1, d_m2), Vector(angle_m2,0,0))
r2 = m2.propagate(r1)
#print r2

# refoc mirror
d_m3 = 0.2
angle_m3 = radians(88)
m3=phoray.SimpleMirror(p, along(r2, d_m3), Vector(angle_m3,0,0))
r3 = m3.propagate(r2)
#print r3

# slit
d_sl = 0.4
angle_sl = -2
sl = phoray.SimpleMirror(p, along(r2, d_m3), Vector(angle_m3,0,0))


print beam4.make_beam4_table(
    ("X", "Y", "Z", "Tilt", "Pitch", "Roll",
     "Cx", "C", "Gy", "Ord", "Type", "Dx", "Dy", "Form"),
    (
        #m1
        (m1.position.x, m1.position.y, m1.position.z,
         degrees(m1.rotation.x), 0, 0,
         0, 0, None, None, "mirror", 0.05, 0.05, "S"),
        #m2
        (m2.position.x, m2.position.y, m2.position.z,
         degrees(m2.rotation.x), 0, 0,
         0, 0, None, None, "mirror", 0.05, 0.05, "S"),
        #m3
        (m3.position.x, m3.position.y, m3.position.z,
         degrees(m3.rotation.x), 0, 0,
         0, 0, None, None, "mirror", 0.05, 0.05, "S"),
        (sl.position.x, sl.position.y, sl.position.z,
         degrees(sl.rotation.x), 0, 0,
         0, 0, None, None, "exit", 0.05, 0.05, "S"),

        ),
    width=15
    )
