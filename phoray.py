#from __future__ import division
from math import *
from vector import Vector

DEBUG=False

def debug(*args):
    if DEBUG:
        print(args)

def quadratic(a, b, c):
    """
    Solve a quadratic function ax^2 + by + c = 0
    """
    if a<0:
        return None
    delta = b**2 - 4*a*c
    if delta >= 0:
        x1 = (-b + sqrt(delta)) / (2*a)
        x2 = (-b - sqrt(delta)) / (2*a)
    else:
        x1 = complex(0, -b + sqrt(-delta)) / (2*a)
        x2 = complex(0, -b - sqrt(-delta)) / (2*a)
    return x1, x2


class Ray(object):
    """
    A ray is defined by its endpoint P0 Vector(X0,Y0,Z0) and its
    "direction cosines", a Vector(k,l,m).

    The vector equation of the line through points A and B is given by
    r = OA + tAB (where t is a scalar multiple)

    If a is vector OA and b is vector OB, then the equation of the
    line can be written: r = a + t(b - a)
    """

    def __init__(self, origin, direction, wavelength=1):
        self.endpoint = origin
        self.direction = direction
        self.wavelength = wavelength

    def translate(self, v):
        """Parallel movement of the Ray by vector v.
        Endpoint is moved, direction unchanged."""
        #self.endpoint += v
        return Ray(self.endpoint+v, self.direction, self.wavelength)

    def deviate(self, dtheta):
        """Rotate the Ray around the x, y, axes by angles theta_x, theta_y, theta_z"""
        #self.direction = self.direction.rotate(r)
        return Ray(self.endpoint, self.direction.rotate(dtheta), self.wavelength)

    def __repr__(self):
        return "%s, %s"%(self.endpoint,self.direction)


class Surface(object):
    """
    A general 3D surface.
    """
    def __init__(self, xsize=None, ysize=None, concave=True):
        self.xsize, self.ysize = xsize, ysize
        self.concave = concave

    def grating_direction(self, p):
        """
        Returns a vector oriented along the grating lines (if any).
        This vector always lies in the plane containing the normal and the local x-axis, and
        is tangential to the surface (i.e. perpendicular to the normal. It also always has
        a non-negative projection on the x-axis.

        [Danger: special case of n and x-axis parallel]
        """
        normal = self.normal(p)
        xaxis = Vector(1,0,0)
        a = normal.cross(xaxis).normalized()
        debug(a)
        return normal.rotate_around(a, pi/2)

    def reflect1(self, ray):
        """
        Returns the reflected ray given an incident ray.

        Method:
        1. find the intersection point P of surface S and ray R
        2. find the normal (n) of the surface at P
        3. find the normal n_m of the mirror plane, i.e. the plane in
           which the ray is mirrored
        4. project r onto n_m
        5. add 2*n_m to -r
        """
        r = ray.direction
        P = self.intersect(ray)
        if P is not None:
            n = self.normal(P)
            if cmp(-r/r.norm(), n/n.norm()) == 0:  # normal incidence
                debug( "normal incidence" )
                return Ray(P, n, ray.wavelength)
            n_m = (r.cross(n).cross(n))
            n_m /= n_m.norm()
            l = r.scalar(n_m) * n_m
            debug(l)
            return Ray(P, 2*l-r, ray.wavelength)
        else:
            return None

    def reflect(self, ray):
        """
        Returns the reflected ray given an incident ray.
        """
        r = ray.direction
        P = self.intersect(ray)
        if P is not None:
            n = self.normal(P)
            r_ref = -r.rotate_around(n, pi)
            return Ray(P, r_ref, ray.wavelength)
        else:
            return None


    def diffract(self, ray, d, order, line_spacing_function=None):
        r = ray.direction.normalized()
        P = self.intersect(ray)
        if P is not None:
            if d is None:   #VLS grating
                d = line_spacing_function(P)
                #print P.y, d
            n = self.normal(P)
            refl = self.reflect(ray)
            if order == 0 or d == 0:
                return refl
            r_ref = refl.direction
            #grdir = r.scalar(Vector(0,1,0))   # r . y
            #grdir /= abs(grdir)

            g = self.grating_direction(P)
            debug("g=", g)
            phi = acos(r_ref.scalar(g))
            debug("phi=", degrees(phi))
            theta = acos(r_ref.scalar(n)/sin(phi))
            debug("theta", degrees(theta))
            theta_m = asin(-order*ray.wavelength/(d*sin(phi)) - sin(theta))
            debug( "theta_m=", degrees(theta_m) )
            r_diff = r_ref.rotate_around(g, theta+theta_m)
            debug("r_diff=", r_diff)
            debug("r=", r)
            return Ray(P, r_diff, ray.wavelength)
        else:
            return None

    def refract(self, ray, i1, i2):
        """
        Refurns the refracted ray given an incident ray.
        Uses Snell's law.
        """
        r = ray.direction.norm()
        P = self.intersect(ray)
        if P is not None:
            n = self.normal(P)
            theta_in = acos((n.dot(r)))
        else:
            return None

class Plane(Surface):
    """
    A plane through the origin and perpendicular to z, i.e. z = 0.
    """
    def normal(self, p):
        return Vector(0,0,1)

    def intersect(self, ray):
        r = ray.direction
        a = ray.endpoint
        b = a + r

        if b.z == a.z:  # parallel case
            return None
        else:
            t = -a.z / (b.z - a.z)
            p = a + t*r

            if (self.xsize is None and self.ysize is None) or \
                    (-self.xsize/2 <= p.x <= self.xsize/2 and
                      -self.ysize/2 <= p.y <= self.ysize/2):
                return p
            else:
                return None


class Sphere(Surface):
    """
    The UPPER (z>0) half of a sphere of radius R, with center (0,0,0)
    """

    def __init__(self, R, *args):
        self.R = R
        Surface.__init__(self, *args)

    def normal(self, p):
        return -p/self.R

    def surface(self):
        coords = []
        for i in (-self.xsize/2, 0, self.xsize/2):
            for j in (-self.ysize/2, 0, self.ysize/2):
                coords.append( Vector(i, j, sqrt(self.R**2-i**2-j**2)) )
        return coords

    def intersect(self, ray, concave=True):
        r = ray.direction
        a = ray.endpoint
        b = a + r

        t = quadratic( (b.z-a.z)**2 + (b.x-a.x)**2 + (b.y-a.y)**2,
                       2*a.z*(b.z-a.z) + 2*a.x*(b.x-a.x) + 2*a.y*(b.y-a.y),
                       a.z**2 + a.x**2 + a.y**2 - self.R**2 )

        if t is None or type(t[0]) is complex or t<0:  # no intersection
            return None
        else:
            if concave:
                p = a + max(t)*r
            else:
                p = a + min(t)*r
            if (self.xsize is None and self.ysize is None) or \
                    (-self.xsize/2 <= p.x <= self.xsize/2 and
                      -self.ysize/2 <= p.y <= self.ysize/2):
                return p
            else:
                return None


class Cylinder(Surface):
    def __init__(self, R, *args):
        self.R = R
        Surface.__init__(self, *args)

    def normal(self, p):
        return (Vector(0, -p.y, -p.z))/sqrt(p.y**2 + p.z**2)

    def intersect(self, ray, concave=True):
        r = ray.direction
        a = ray.endpoint
        b = a+r

        t = quadratic( (b.z-a.z)**2 + (b.y-a.y)**2,
                       2*a.z*(b.z-a.z) + 2*a.y*(b.y-a.y),
                       a.z**2 + a.y**2 - self.R**2 )

        if t is None or type(t[0]) is complex or t<0:  # no intersection
            return None
        else:
            if concave:
                p = a + max(t)*r
            else:
                p = a + min(t)*r
            if (self.xsize is None and self.ysize is None) or \
                    (-self.xsize/2 <= p.x <= self.xsize/2 and
                      -self.ysize/2 <= p.y <= self.ysize/2):
                debug( p )
                return p
            else:
                return None


class Ellipsoid(Surface):

    def __init__(self, a, b, c, *args):
        self.a, self.b, self.c = a, b, c
        Surface.__init__(self, *args)

    def normal(self, p):
        """
        Surface normal at point p, calculated through the gradient
        """
        a,b,c =self.a, self.b, self.c
        #return -p/p.norm()
        #d = 1/(2*sqrt(c**2*(1-p.x**2/a**2-p.y**2/b**2))) * 2*c**2
        #return Vector(d*p.x/a**2, d*p.y/b**2)
        n = Vector(-2*p.x/a**2, -2*p.y/b**2, -2*p.z/c**2)
        return n.normalized()

    def intersect(self, ray, concave=True):
        r = ray.direction
        p0 = ray.endpoint
        p1 = p0 + r
        a, b, c = self.a, self.b, self.c

        t = quadratic(
            (p1.z-p0.z)**2 + c**2*(p1.x-p0.x)**2/a**2 + c**2*(p1.y-p0.y)**2/b**2,
            2*p0.z*(p1.z-p0.z) + c**2*2*p0.x*(p1.x-p0.x)/a**2 + c**2*2*p0.y*(p1.y-p0.y)/b**2,
            p0.z**2 + c**2*p0.x**2/a**2 + c**2*p0.y**2/b**2 - c**2 )

        if t is None or type(t[0]) is complex:  # no intersection
            return None
        else:
            if concave:
                p = p0 + max(t)*r
            else:
                p = p0 + min(t)*r
            if (self.xsize is None and self.ysize is None) or \
                    (-self.xsize/2 <= p.x <= self.xsize/2 and
                      -self.ysize/2 <= p.y <= self.ysize/2):
                return p
            else:
                return None

        # else:
        #     p = p0 + min(t)*r
        #     if (self.xsize is None and self.ysize is None ) or \
        #             (-self.xsize/2 <= p.x <= self.xsize/2 and
        #               -self.ysize/2 <= p.y <= self.ysize/2):
        #         return p
        #     else:
        #         return None

class Element(object):
    def __init__(self, surface, position, rotation=Vector(0,0,0), surface_offset=Vector(0,0,0), material=None):
        self.position = position
        self.rotation = rotation
        self.surface = surface
        self.surface_offset = surface_offset
        self.material = material

    def ray_to_center(self, p):
        """
        Doesn't work... think, damnit!
        """
        pl = self.localize_vector(p)
        return self.globalize(Ray(pl, -p))

    def localize_vector(self, v):
        return (v-self.position).rotate(-self.rotation)-self.surface_offset

    def localize(self, ray):
        """
        Transform a Ray in global coordinates into local coordinates
        """
        return Ray( (ray.endpoint-self.position).rotate(-self.rotation)-self.surface_offset,
                    ray.direction.rotate(-self.rotation), ray.wavelength )

    def globalize_vector(self, v):
        return (v+self.surface_offset).rotate(self.rotation)+self.position

    def globalize(self, ray):
        """
        Transform a local Ray into global coordinates
        """
        return Ray( (ray.endpoint+self.surface_offset).rotate(self.rotation)+self.position,
                    ray.direction.rotate(self.rotation), ray.wavelength )



class SimpleMirror(Element):

    def propagate(self, ray):
        """
        Takes a ray in global coordinates and tries to reflect it in the
        surface
        """
        if ray is not None:
            ray0 = self.localize(ray)
            reflected_ray = self.surface.reflect(ray0)
            if reflected_ray is None:
                return None
            else:
                return self.globalize(reflected_ray)
        else:
            return None


class Detector(Element):

    def propagate(self, ray):
        if ray is not None:
            ray0 = self.localize(ray)
            pos = self.globalize_vector(self.surface.intersect(ray0))
            return Ray(pos, Vector(0,0,0), ray.wavelength)
        else:
            return None

class Mirror(Element):

    # def __init__(self, d, order, *args, **kwargs):
    #     self.d = d
    #     self.order = order
    #     Element.__init__(self, *args, **kwargs)

    def __init__(self, d=0, order=0, *args, **kwargs):
        """
        Define a reflecting element with surface shape given by s.
        If d>0 it will work as a grating with line spacing d
        and lines in the xz-plane and diffraction order given by order. Otherwise it works
        as a plain mirror.
        """
        self.d=d
        self.order=order
        Element.__init__(self, *args, **kwargs)

    def propagate(self, ray):
        """
        Takes a ray in global coordinates and tries to reflect it in the
        surface
        """
        if ray is not None:
            ray0 = self.localize(ray)
            diffracted_ray = self.surface.diffract(
                ray0, self.d, self.order)
            if diffracted_ray is None:
                return None
            else:
                return self.globalize(diffracted_ray)
        else:
            return None

class SphericalVLSGrating(Mirror):

    def __init__(self, an, *args, **kwargs):
        self.an = an
        Mirror.__init__(self, *args, **kwargs)

    def get_line_distance(self, p):
        """
        Returns the local grating line density according to VLS parameters
        a(x) = a_0 + a_1*x + ... + a_n*x^n where x is the distance to the grating center.
        """
        y = 1000*p.y
        R = 1000*self.surface.R
        x = copysign(sqrt(y**2 + (R - sqrt(R**2-y**2))), y)
        x = 2*R*asin(x/(2*R))
        #x=y
        b=-x/sqrt(R**2-x**2)
        theta = atan(b)  # grating tangent angle
        print b,theta
        d = 0
        for n, a in enumerate( self.an ):
            d += a * x**n
        d*=cos(theta)
        return 1e-3/d

    def propagate(self, ray):
        """
        Takes a ray in global coordinates and tries to reflect it in the
        surface
        """
        if ray is not None:
            ray0 = self.localize(ray)
            diffracted_ray = self.surface.diffract(ray0, None, self.order,
                                                   self.get_line_distance)
            if diffracted_ray is None:
                return None
            else:
                return self.globalize(diffracted_ray)
        else:
            return None

