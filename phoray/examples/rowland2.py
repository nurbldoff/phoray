from __future__ import division
from math import *

def circle(x, R, a=0, b=0):
    return -sqrt(R**2-(x-a)**2)+b

def tangent(x, R):
    "Circle derivative"
    return x/sqrt(R**2-x**2)

def get_line( point, angle ):
    """
    returns the direction and the y axis intersection for the line that passes
    a point with an angle (in radians) to the x-axis.
    """
    x, y = point
    k = tan(angle)
    m = y - k*x
    return (k, m)

def line_circle_intersect(k, m, R, a=0, b=0, s=+1):
    """
    The line_circle_intersect point of a line (k, m) with a half-circle of radius R,
    centered at (a, b).
    """
    x = (-(2*k*(m-b)-2*a) + s*sqrt((2*k*(m-b)-2*a)**2-4*(1+k**2)*(a**2+(m-b)**2-R**2)))/ \
        (2*(1+k**2))
    y = circle(x, R, a, b)
    return (x, y)

def lines_intersect(k0, m0, k1, m1):
    if k1 != k0:
        x = (m1-m0)/(k0-k1)
        return (x, k0*x+m0)
    else:
        return None


class Rowland(object):
    """
    Define a rowland spectrometer.
    Standard origo is at the center of the grating.
    - R_gr = Grating radius in m
    - d_gr = Line density in mm^{-1}, or VLS parameter list
    - theta_in = incident angle in degrees
    - r_source = distance to source (0 means it is automatically positioned
                 on the rowland circle.)
    """
    def __init__(self, R_gr, d_gr, theta_in, source_d=0):
        self.R_gr = R_gr
        self.d_gr = d_gr
        self.theta_in = radians(theta_in)
        if source_d == 0:
            self.source_d = self.R_gr * sin(self.theta_in)
        else:
            self.source_d = source_d
        #self.source_d = -2*R_gr/2*tan(theta_in) / sqrt(1+tan(theta_in)**2)
        self.source_x = -self.source_d * cos(self.theta_in)
        self.source_y = self.source_d * sin(self.theta_in)
        self.rays = []
        self.fig = None


    def get_detector_position2(self, order, wavelength):
        theta_out = pi/2 - asin(-order*wavelength*self.d_gr +
                                sin(pi/2-radians(self.theta_in)))
        d_out = 2*self.R_gr/2*tan(theta_out) / sqrt(1+tan(theta_out)**2)
        x_det = d_out * cos(theta_out)
        y_det = d_out * sin(theta_out)
        return (x_det, y_det)

    def get_detector_position(self, order, wl):
        print order, wl, self.d_gr
        print "d:", order * wl * self.d_gr * 1000
        print "theta_in:", self.theta_in
        theta_out = acos(cos(self.theta_in) - order*wl*self.d_gr*1000)
        r_out = self.R_gr * sin(theta_out)
        return (theta_out, r_out)

    def get_line_density(self, x, y):
        """
        Given a point on the grating, calculate the local line density.
        For an ordinary grating, it is constant (d_gr).
        For a VLS grating, it is determined as
            d = d_gr[0] + d_gr[1]*t + d_gr[2]*t**2 + ...,
        where t is a parameter along the grating circle.
        """
        if hasattr(self.d_gr, '__iter__'):   # i.e. it's a VLS grating
            t = self.R_gr*1000 * acos((self.R_gr-y)/self.R_gr) * sign(x)
            #d = 0
            #for i,di in enumerate(self.d_gr):
            #    d += di * t**i
            #return d
            return polyval(list(reversed(self.d_gr)), t)
        else:
            return self.d_gr

    def add_ray(self, energy, diff_order, deviation):
        """
        Calculate the path of a photon ray with deviation from the
        "optical axis".
        """

        wavelength = 6.626068e-34*2.9979e8/(energy*1.60217e-19)

        # Center ray
        k0, m0 = get_line( (self.source_x, self.source_y), -self.theta_in )
        ## Calculate where the ray hits the grating.
        x0_inters, y0_inters = line_circle_intersect(k0, m0, self.R_gr, 0, self.R_gr)

        ## Get the reflection angle
        angle_gr0 = atan(tangent(x0_inters, self.R_gr))
        angle_in0 = atan(k0-tangent(x0_inters, self.R_gr))
        angle_out0 = angle_gr0 - angle_in0

        ## Add diffraction angle
        d0 = self.get_line_density(x0_inters, y0_inters)
        #print d0
        diff_angle0 = acos(diff_order*wavelength*d0*1000+cos(angle_in0))
        angle_out0 = angle_gr0 + diff_angle0

        k02, m02 = get_line( (x0_inters, y0_inters), angle_out0 )

        # Real ray
        k, m = get_line( (self.source_x, self.source_y), -self.theta_in+deviation/180*pi )

        ## Calculate where the ray hits the grating.
        x_inters, y_inters = line_circle_intersect(k, m, self.R_gr, 0, self.R_gr)

        ## Get the reflection angle
        angle_gr =atan(tangent(x_inters, self.R_gr))
        angle_in = atan(k-tangent(x_inters, self.R_gr))
        angle_out = angle_gr - angle_in

        ## Add diffraction angle
        d = self.get_line_density(x_inters, y_inters)
        diff_angle = acos(diff_order*wavelength*d*1000+cos(angle_in))
        angle_out = angle_gr + diff_angle

        k2, m2 = get_line( (x_inters, y_inters), angle_out )

        ## Get line_circle_intersect of reflected ray with rowland circle
        x_inters2, y_inters2 = line_circle_intersect(k2, m2, self.R_gr/2, 0, self.R_gr/2)

        ## Get line_circle_intersect with center ray
        focus = lines_intersect(k2, m2, k02, m02)

        self.rays.append((energy, (self.source_x, x_inters, x_inters2),
                          (self.source_y, y_inters, y_inters2), focus))

        return (x_inters2, y_inters2)


    def clean(self):
        self.rays=[]
