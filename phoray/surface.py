# cython: profile=True

from __future__ import division
from math import *

from numpy import array, dot, cross, max, min
from numpy.linalg import norm
#from numba import autojit

from transformations import rotation_matrix
from ray import Ray, Rays
from solver import quadratic
from . import Length


class Surface(object):
    """
    An abstract 3D surface.
    Should not be instantiated but serves as a base class to be inherited.
    """

    def __init__(self, xsize=Length(1.0), ysize=Length(1.0)):
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
        xaxis = array((1, 0, 0))  # Note: Grating lines are always perp. to
                              # local X axis.
        a = cross(normal, xaxis)
        rot = rotation_matrix(pi/2, a)
        d = dot(normal, rot[:3, :3].T)
        # TODO: normalize?
        return d / norm(d)

    def reflect(self, rays):
        """
        Reflect the given ray in the surface, returning the reflected ray.
        """

        r = rays.directions
        P = self.intersect(rays)
        if P is None:
            return None
        else:
            normal = self.normal(P)
            refl = r - (normal * 2.0 * dot(r, normal.T))
            return Rays(P, refl)

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
            phi = acos(dot(r_ref, g))
            theta = acos(dot(r_ref, n) / sin(phi))
            #print "phi", phi, "theta", theta
            try:
                theta_m = asin(-order * ray.wavelength /
                                (d * sin(phi)) - sin(theta))
            except Exception as e:
                #print "Discarding ray:", str(e)
                return None
            #rotation = Mat.RotateAxis(-degrees(theta + theta_m), g)
            r_diff = dot(r_ref, rotation_matrix(theta + theta_m, g)[:3, :3].T)
            return Ray(P, r_diff, ray.wavelength)

    def refract(self, ray, i1, i2):
        """
        Refurns the refracted ray given an incident ray.
        Uses Snell's law. Does *not* simulate dispersion.

        FIXME: Check that this is correct.
        """
        P = self.intersect(ray)
        #print P
        if P is not None:
            r = ray.direction
            n = self.normal(P)
            dotp = dot(n, r)
            if dotp >= 0:
                n = -n
            theta_in = acos(dot(n, r))
            if sin(theta_in) == 0:
                return ray
            #print i1, i2, sin(theta_in)
            theta_out = asin((i1 / i2) * sin(theta_in))
            v = r % n
            r2 = dot(-n, rotation_matrix(theta_out, v)[:3, :3].T)
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

    def normal(self, ps):
        return array([(0, 0, 1, 0)] * len(ps))

    def intersect(self, rays):
        rx, ry, rz, _ = r = rays.directions.T

        # if rz < 0:  # backlit
        #     #print "backlit"
        #     return None

        ax, ay, az, _ = a = rays.endpoints.T
        bx, by, bz, _ = a + r

        if bz == az:  # parallel case
            print "parallel"
            return None
        else:
            t = -az / (bz - az)
            # if t < 0:
            #     # Backtracking the ray -> no intersection
            #     return None
            p = a + t * r
            # if (self.xsize is None and self.ysize is None) or \
            #         (-self.xsize / 2 <= p[0] <= self.xsize / 2 and
            #          -self.ysize / 2 <= p[1] <= self.ysize / 2):
            #     return p
            # else:
            #     print "outside"
            #     return None
            return p.T

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
    Half a sphere of radius R. If R > 0, it is the 'top' half (z > 0)
    and if R < 0 it is the 'bottom' half (z < 0).
    """

    def __init__(self, R=Length(1), *args, **kwargs):
        self.R = R
        if "xsize" in kwargs:
            kwargs["xsize"] = min((kwargs["xsize"], abs(R)))
        if "ysize" in kwargs:
            kwargs["ysize"] = min((kwargs["ysize"], abs(R)))
        Surface.__init__(self, *args, **kwargs)

    def normal(self, p):
        #return -Vec(p.x, p.y, p.z + self.R) / self.R
        return -(p + array((0, 0, self.R, 0))) / self.R

    def intersect(self, ray):

        rx, ry, rz, _ = r = ray.directions.T
        #if r.z * self.R <= 0:  # backlit
            #print "backlit"
            #return None
        ax, ay, az, _ = a = (ray.endpoints + array((0, 0, self.R, 0))).T
        t = quadratic(rz ** 2 + rx ** 2 + ry ** 2,
                      2 * az * rz + 2 * ax * rx + 2 * ay * ry,
                      az ** 2 + ax ** 2 + ay ** 2 - self.R ** 2)
        if t is None:  # no
            # intersection
            print "missed"
            return None
        else:
            # Figure out which intersection we should use
            if self.R > 0:
                if az + max(t) * rz > 0:
                    p = a + max(t) * r
                else:
                    p = a + min(t) * r
            else:
                if az + min(t) * rz < 0:
                    p = a + min(t) * r
                else:
                    p = a + max(t) * r
            # if (self.xsize is None and self.ysize is None) or (
            #         (-self.xsize / 2 <= p[0] <= self.xsize / 2) and
            #         (-self.ysize / 2 <= p[1] <= self.ysize / 2)):
            #     return p - array((0, 0, self.R))
            #     #return Vec(p.x, p.y, p.z)
            return p.T
            # else:
            #     print "outside"
            #     return None

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

    def __init__(self, R=Length(1.0), *args, **kwargs):
        self.R = R
        if "ysize" in kwargs:
            kwargs["ysize"] = min(kwargs["ysize"], abs(R * 1.5))
        Surface.__init__(self, *args, **kwargs)

    def normal(self, p):
        return array((0, -p[1], -p[2] - self.R)) / self.R

    def intersect(self, ray):
        rx, ry, rz = r = ray.direction

        if rz * self.R <= 0:  # backlit
            return None

        ax, ay, az = a = ray.endpoint + array((0, 0, self.R))
        bx, by, bz = a + r

        t = quadratic((bz - az) ** 2 + (by - ay) ** 2,
                      2 * az * (bz - az) + 2 * ay * (by - ay),
                      az ** 2 + ay ** 2 - self.R ** 2)

        if t is None:  # no intersection
            return None
        else:
            if self.R > 0:
                if az + max(t) * rz > 0:
                    p = a + max(t) * r
                else:
                    p = a + min(t) * r
            else:
                if az + min(t) * rz < 0:
                    p = a + min(t) * r
                else:
                    p = a + max(t) * r
            if (self.xsize is None and self.ysize is None) or (
                    -self.xsize / 2 <= p[0] <= self.xsize / 2 and
                    -self.ysize / 2 <= p[1] <= self.ysize / 2):
                return p - array((0, 0, self.R))
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

    def __init__(self, a=Length(1.0), b=Length(1.0), c=Length(1.0),
                 *args, **kwargs):
        self.a, self.b, self.c = a, b, c
        kwargs["xsize"] = min(kwargs["xsize"], abs(a))
        kwargs["ysize"] = min(kwargs["ysize"], abs(b))
        Surface.__init__(self, *args, **kwargs)

    def normal(self, p):
        """
        Surface normal at point p, calculated through the gradient
        """
        a, b, c = self.a, self.b, self.c
        n = array((-2 * p[0] / a ** 2,
                -2 * p[1] / b ** 2,
                -2 * (p[2] + c) / c ** 2))
        return n.normalize()

    def intersect(self, ray):
        a, b, c = self.a, self.b, self.c
        rx, ry, rz = r = ray.direction
        p0x, p0y, p0z = p0 = ray.endpoint + array((0, 0, c))

        t = quadratic(
            rz ** 2 + c ** 2 * rx ** 2 / a ** 2 +
                c ** 2 * ry ** 2 / b ** 2,
            2 * p0z * rz + c ** 2 * 2 * p0x * rx /
                a ** 2 + c ** 2 * 2 * p0y * ry / b ** 2,
            p0z ** 2 + c ** 2 * p0x ** 2 / a ** 2 + c ** 2 * p0y ** 2 /
                b ** 2 - c ** 2)

        if t is None:  # no intersection
            return None
        else:
            # Figure out which intersection we should use
            if self.a * self.b * self.c > 0:
                if p0z + max(t) * rz > 0:
                    p = p0 + max(t) * r
                else:
                    p = p0 + min(t) * r
            else:
                if p0z + min(t) * rz < 0:
                    p = p0 + min(t) * r
                else:
                    p = p0 + max(t) * r
            if (self.xsize is None and self.ysize is None) or (
                    (-self.xsize / 2 <= p[0] <= self.xsize / 2) and
                    (-self.ysize / 2 <= p[1] <= self.ysize / 2)):
                return array((px, py, pz - c))
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

    def __init__(self, a=Length(1.0), b=Length(1.0), c=Length(1.0),
                 *args, **kwargs):
        self.a = a
        self.b = b
        self.c = c
        Surface.__init__(self, *args, **kwargs)

        self.d = -2 * c / a ** 2
        self.e = -2 * c / b ** 2

        self.concave = a * b * c < 0

    def normal(self, p):
        px, py, pz = p
        f = sqrt((self.d * px) ** 2 + (self.e * py) ** 2 + 1)
        return array((self.d * px / f, self.e * py / f, 1 / f))

    def intersect(self, ray):
        rx, ry, rz = r = ray.direction
        px, py, pz = p = ray.endpoint
        a2, b2, c = self.a ** 2, self.b ** 2, self.c
        xsize, ysize = self.xsize, self.ysize
        t = quadratic(rx ** 2 / a2 + ry ** 2 / b2,
                      2 * px * rx / a2 + 2 * py * ry / b2 - rz / c,
                      px ** 2 / a2 + py ** 2 / b2 - pz / c)
        if t is None:  # no intersection
            return None
        else:
            if self.concave:
                ip = p + max(t) * r
            else:
                ip = p + min(t) * r
            if ((xsize is None and ysize is None)
                or (-xsize / 2 <= ip[0] <= xsize / 2
                    and -ysize / 2 <= ip[1] <= ysize / 2)):
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
