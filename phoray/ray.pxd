from __future__ import division
#from minivec import Vec, Mat

cimport numpy as np


cdef class Ray:
    cdef public np.ndarray endpoint, direction
    cdef public double wavelength

    cpdef Ray translate(self, np.ndarray v)

    cpdef Ray rotate(self, np.ndarray dtheta)

    cpdef np.ndarray along(self, double dist)
