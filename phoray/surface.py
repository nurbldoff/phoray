from __future__ import division
from math import *
#from collections import OrderedDict

from minivec import Vec, Mat
from ray import Ray
from solver import quadratic
#from . import debug


# base_schema = [("xsize", {"type": "length", "value": 1}),
#                ("ysize", {"type": "length", "value": 1})]


class Surface(object):
    """
    A general 3D surface. Should not be instantiated but serves as a base class
    to be inherited.
    """

    def __init__(self, xsize=1.0, ysize=1.0):
        self.xsize, self.ysize = xsize, ysize

    def intersect(self, r):
        """This method needs to be implemented by an actual surface.
        Shall return the point where Ray r intersects the surface.
        """
        pass

    def normal(self, p):
        """This method needs to be implemented by an actual surface.
        Shall return the normal to the surface at point p.
        """
        pass

    def grating_direction(self, p):
        """
        Returns a vector oriented along the grating lines (if any).
        This vector always lies in the plane containing the normal and
        the local x-axis, and is tangential to the surface (i.e.
        perpendicular to the normal. It also always has a non-negative
        projection on the x-axis.

        FIXME: special case of n and x-axis parallel
        """
        normal = self.normal(p)
        xaxis = Vec(1, 0, 0)
        a = normal.cross(xaxis)
        rotation = Mat().rotateAxis(90, a)
        return normal.transformDir(rotation).normalize()

    def reflect(self, ray):

        """
        Reflect the given ray in the surface, returning the reflected ray.
        """

        r = ray.direction
        P = self.intersect(ray)
        if P is None:
            return None
        else:
            return Ray(P, r.reflect(self.normal(P)))

    def diffract(self, ray, d, order, line_spacing_function=None):

        """
        Diffract the given ray in the surface, returning the diffracted ray.
        """

        P = self.intersect(ray)
        if P is None:
            return None
        else:
            refl = self.reflect(ray)
            if order == 0 or d == 0 or ray.wavelength == 0:
                return refl
            if d is None:
                if line_spacing_function is None:
                    return refl
                else:
                    # VLS grating
                    d = line_spacing_function(P)
            n = self.normal(P)
            r_ref = refl.direction
            g = self.grating_direction(P)
            # TODO: seems like there should be a simpler way to do
            # this. But remember that the direction of the grating
            # must be taken into account!
            phi = acos(r_ref.dot(g))
            theta = acos(r_ref.dot(n) / sin(phi))
            print "phi", phi, "theta", theta
            try:
                theta_m = asin(-order * ray.wavelength /
                                (d * sin(phi)) - sin(theta))
            except Exception as e:
                print "Discarding ray:", str(e)
                return None
            rotation = Mat.RotateAxis(-degrees(theta + theta_m), g)
            r_diff = r_ref.transformDir(rotation)
            return Ray(P, r_diff, ray.wavelength)

    def refract(self, ray, i1, i2):
        """
        Refurns the refracted ray given an incident ray.
        Uses Snell's law.

        FIXME: Incomplete, doesn't work
        """
        P = self.intersect(ray)
        print P
        if P is not None:
            r = ray.direction
            n = self.normal(P)
            dot = n.dot(r)
            if dot >= 0:
                n = -n
            theta_in = acos(n.dot(r))
            if sin(theta_in) == 0:
                return ray
            print i1, i2, sin(theta_in)
            theta_out = asin((i1 / i2) * sin(theta_in))
            v = r % n
            r2 = (-n).transformDir(Mat.RotateAxis(degrees(theta_out), v))
            return Ray(P, r2, ray.wavelength)
        else:
            return None

    def mesh(self, res):
        """
        This method needs to be implemented by an actual surface.
        Returns the vertices and faces of a mesh representing the surface.
        """
        pass


class Plane(Surface):
    """
    A plane through the origin and perpendicular to z, i.e. z = 0.
    """

    # schema = OrderedDict(base_schema)

    def normal(self, p):
        return Vec(0, 0, 1)

    def intersect(self, ray):
        r = ray.direction

        if ray.direction.z < 0:  # backlit
            print "backlit"
            return None

        a = ray.endpoint
        b = a + r

        if b.z == a.z:  # parallel case
            print "parallel"
            return None
        else:
            t = -a.z / (b.z - a.z)
            if t < 0:
                # Backtracking the ray -> no intersection
                return None
            p = a + t * r
            if (self.xsize is None and self.ysize is None) or \
                    (-self.xsize / 2 <= p.x <= self.xsize / 2 and
                     -self.ysize / 2 <= p.y <= self.ysize / 2):
                return p
            else:
                print "outside"
                return None

    def mesh(self, res=10):
        verts = []
        faces = []
        w = self.xsize
        h = self.ysize
        for i, x in enumerate(-w / 2 + d * w / res
                               for d in xrange(res + 1)):
            for j, y in enumerate(-h / 2 + d * h / res
                                   for d in xrange(res + 1)):
                verts.append((x, y, 0))
        for i in xrange(res):
            for j in xrange(res):
                current = i * (res + 1) + j
                faces.append((current, current + 1, current + 2 + res))
                faces.append((current, current + 2 + res, current + 1 + res))
        return verts, faces


class Sphere(Surface):
    """
    Half a sphere of radius R, with center (0,0,0). If R > 0, it is the top
    hapf (z > 0) and if R < 0 it is the lower half (z < 0).
    """

    # schema = OrderedDict([("R", {"type": "number", "value": 1})] + base_schema)

    def __init__(self, R=1, *args, **kwargs):
        self.R = R
        kwargs["xsize"] = min(kwargs["xsize"], abs(R))
        kwargs["ysize"] = min(kwargs["ysize"], abs(R))
        Surface.__init__(self, *args, **kwargs)

    def normal(self, p):
        return Vec(p.x, p.y, p.z - self.R) / self.R

    def intersect(self, ray):

        r = ray.direction
        if r.z * self.R <= 0:  # backlit
            print "backlit"
            return None

        #a = ray.endpoint
        a = ray.endpoint + Vec(0, 0, self.R)
        b = a + r
        #R = self.R

        t = quadratic((b.z - a.z) ** 2 + (b.x - a.x) ** 2 + (b.y - a.y) ** 2,
                      2 * a.z * (b.z - a.z) + 2 * a.x * (b.x - a.x) +
                      2 * a.y * (b.y - a.y),
                      a.z ** 2 + a.x ** 2 + a.y ** 2 - self.R ** 2)

        if t is None or type(t[0]) is complex or t < 0:  # no
            # intersection
            print "missed"
            return None
        else:
            # Figure out which intersection we should use
            if self.R > 0:
                if a.z + max(t) * r.z > 0:
                    p = a + max(t) * r
                else:
                    p = a + min(t) * r
            else:
                if a.z + min(t) * r.z < 0:
                    p = a + min(t) * r
                else:
                    p = a + max(t) * r
            if (self.xsize is None and self.ysize is None) or (
                    (-self.xsize / 2 <= p.x <= self.xsize / 2) and
                    (-self.ysize / 2 <= p.y <= self.ysize / 2)):
                return Vec(p.x, p.y, p.z - self.R)
                #return Vec(p.x, p.y, p.z)
            else:
                print "outside"
                return None

    def mesh(self, res=10):
        verts = []
        faces = []
        w = self.xsize
        h = self.ysize
        sgn = copysign(1, self.R)

        for x in (-w / 2 + d * w / res for d in xrange(res + 1)):
            for y in (-h / 2 + d * h / res for d in xrange(res + 1)):
                z = sgn * sqrt(self.R ** 2 - x ** 2 - y ** 2)
                verts.append((x, y, z - self.R))
        for i in xrange(res):
            for j in xrange(res):
                current = i * (res + 1) + j
                faces.append((current, current + 1, current + 2 + res))
                faces.append((current, current + 2 + res, current + 1 + res))
        return verts, faces


class Cylinder(Surface):

    # schema = OrderedDict([("R", {"type": "number", "value": 1})] + base_schema)

    def __init__(self, R=1, *args, **kwargs):
        self.R = R
        kwargs["ysize"] = min(kwargs["ysize"], abs(R * 1.5))
        Surface.__init__(self, *args, **kwargs)

    def normal(self, p):
        return (Vec(0, -p.y, -p.z - self.R)) / self.R

    def intersect(self, ray):
        r = ray.direction

        if r.z * self.R <= 0:  # backlit
            return None

        a = ray.endpoint + Vec(0, 0, self.R)
        b = a + r

        t = quadratic((b.z - a.z) ** 2 + (b.y - a.y) ** 2,
                      2 * a.z * (b.z - a.z) + 2 * a.y * (b.y - a.y),
                      a.z ** 2 + a.y ** 2 - self.R ** 2)

        if t is None or type(t[0]) is complex or t < 0:  # no intersection
            return None
        else:
            if self.R > 0:
                if a.z + max(t) * r.z > 0:
                    p = a + max(t) * r
                else:
                    p = a + min(t) * r
            else:
                if a.z + min(t) * r.z < 0:
                    p = a + min(t) * r
                else:
                    p = a + max(t) * r
            if (self.xsize is None and self.ysize is None) or (
                    -self.xsize / 2 <= p.x <= self.xsize / 2 and
                    -self.ysize / 2 <= p.y <= self.ysize / 2):
                return Vec(p.x, p.y, p.z - self.R)
            else:
                return None

    def mesh(self, res=10):
        verts = []
        faces = []
        w = self.xsize
        h = self.ysize
        sgn = copysign(1, self.R)
        for x in (-w / 2 + d * w / res for d in xrange(res + 1)):
            for y in (-h / 2 + d * h / res for d in xrange(res + 1)):
                z = sgn * sqrt(self.R ** 2 - y ** 2)
                verts.append((x, y, z - self.R))

        for i in xrange(res):
            for j in xrange(res):
                current = i * (res + 1) + j
                faces.append((current, current + 1, current + 2 + res))
                faces.append((current, current + 2 + res, current + 1 + res))
        return verts, faces


class Ellipsoid(Surface):

    # schema = OrderedDict([("a", {"type": "number", "value": 1}),
    #                       ("b", {"type": "number", "value": 1}),
    #                       ("c", {"type": "number", "value": 1})] + base_schema)

    def __init__(self, a=1, b=1, c=1, *args, **kwargs):
        self.a, self.b, self.c = a, b, c
        kwargs["xsize"] = min(kwargs["xsize"], abs(a))
        kwargs["ysize"] = min(kwargs["ysize"], abs(b))
        Surface.__init__(self, *args, **kwargs)

    def normal(self, p):
        """
        Surface normal at point p, calculated through the gradient
        """
        a, b, c = self.a, self.b, self.c
        n = Vec(-2 * p.x / a ** 2,
                 -2 * p.y / b ** 2,
                 -2 * p.z / c ** 2 - c)
        return n.normalize()

    def intersect(self, ray):
        a, b, c = self.a, self.b, self.c
        r = ray.direction
        p0 = ray.endpoint + Vec(0, 0, c)
        p1 = p0 + r

        t = quadratic(
            (p1.z - p0.z) ** 2 + c ** 2 * (p1.x - p0.x) ** 2 / a ** 2 +
                c ** 2 * (p1.y - p0.y) ** 2 / b ** 2,
            2 * p0.z * (p1.z - p0.z) + c ** 2 * 2 * p0.x * (p1.x - p0.x) /
                a ** 2 + c ** 2 * 2 * p0.y * (p1.y - p0.y) / b ** 2,
            p0.z ** 2 + c ** 2 * p0.x ** 2 / a ** 2 + c ** 2 * p0.y ** 2 /
                b ** 2 - c ** 2 )

        if t is None or type(t[0]) is complex:  # no intersection
            return None
        else:
            # Figure out which intersection we should use
            if self.a * self.b * self.c > 0:
                if p0.z + max(t) * r.z > 0:
                    p = p0 + max(t) * r
                else:
                    p = p0 + min(t) * r
            else:
                if p0.z + min(t) * r.z < 0:
                    p = p0 + min(t) * r
                else:
                    p = p0 + max(t) * r
            if (self.xsize is None and self.ysize is None) or (
                    (-self.xsize / 2 <= p.x <= self.xsize / 2) and
                    (-self.ysize / 2 <= p.y <= self.ysize / 2)):
                return Vec(p.x, p.y, p.z - c)
            else:
                return None

    def mesh(self, res=10):
        verts = []
        faces = []
        w, h = self.xsize, self.ysize
        a, b, c = self.a, self.b, self.c
        sgn = copysign(1, self.a * self.b * self.c)
        for x in (-w / 2 + d * w / res for d in xrange(res + 1)):
            for y in (-h / 2 + d * h / res for d in xrange(res + 1)):
                z = sgn * sqrt((c ** 2) * (
                        1 - x ** 2 / a ** 2 - y ** 2 / b ** 2))
                verts.append((x, y, z - c))
        for i in xrange(res):
            for j in xrange(res):
                current = i * (res + 1) + j
                faces.append((current, current + 1, current + 2 + res))
                faces.append((current, current + 2 + res, current + 1 + res))
        return verts, faces


class Paraboloid(Surface):
    """
    A paraboloid (rotated parabola) described by z/c = (x/a)^2 + (y/b)^2
    """

    # schema = OrderedDict([("a", {"type": "number", "value": 1}),
    #                       ("b", {"type": "number", "value": 1}),
    #                       ("c", {"type": "number", "value": 1})] + base_schema)

    def __init__(self, a=1, b=1, c=1, *args, **kwargs):
        self.a = a
        self.b = b
        self.c = c
        Surface.__init__(self, *args, **kwargs)

        self.d = -2 * c / a ** 2
        self.e = -2 * c / b ** 2

        self.concave = True

    def normal(self, p):
        f = sqrt((self.d * p.x) ** 2 + (self.e * p.y) ** 2 + 1)
        return Vec(self.d * p.x / f, self.e * p.y / f, 1 / f)

    def intersect(self, ray):
        r = ray.direction
        p = ray.endpoint
        a2, b2, c = self.a ** 2, self.b ** 2, self.c
        t = quadratic(r.x ** 2 / a2 + r.y ** 2 / b2,
                      2 * p.x * r.x / a2 + 2 * p.y * r.y / b2 - r.z / c,
                      p.x ** 2 / a2 + p.y ** 2 / b2 - p.z / c)
        if t is None or type(t[0]) is complex or t < 0:  # no intersection
            return None
        else:
            if self.concave:
                ip = p + max(t) * r
            else:
                ip = p + min(t) * r
            if (self.xsize is None and self.ysize is None) or (
                    (-self.xsize / 2 <= ip.x <= self.xsize / 2) and
                    (-self.ysize / 2 <= ip.y <= self.ysize / 2)):
                return ip
            else:
                return None

    def mesh(self, res=10):
        verts = []
        faces = []
        w = self.xsize
        h = self.ysize
        a, b, c = self.a, self.b, self.c
        for x in (-w / 2 + d * w / res for d in xrange(res + 1)):
            for y in (-h / 2 + d * h / res for d in xrange(res + 1)):
                verts.append((x, y, c * (x ** 2 / a ** 2 + y ** 2 / b ** 2)))
        for i in xrange(res):
            for j in xrange(res):
                current = i * (res + 1) + j
                faces.append((current, current + 1, current + 2 + res))
                faces.append((current, current + 2 + res, current + 1 + res))
        return verts, faces
