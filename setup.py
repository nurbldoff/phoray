from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

setup(ext_modules=cythonize(["phoray/solver.pyx", "phoray/vector.pyx",
                             "phoray/ray.pyx", "phoray/surface.pyx",
                             "phoray/element.pyx", "phoray/system.pyx"]))

setup(name='_transformations',
      ext_modules=[Extension('phoray/_transformations',
                             ['phoray/transformations.c'],
                             include_dirs=[numpy.get_include()])])

# setup(
#     cmdclass = {'build_ext': build_ext},
#     ext_modules = [Extension("solver", ["solver.pyx"]),
#                    Extension("vector", ["vector.pyx"])]
#                    #Extension("ray", ["ray.pyx"])]
# )
