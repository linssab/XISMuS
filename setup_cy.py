from setuptools import setup
from setuptools import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy as np


setup(cmdclass={'build_ext': build_ext},
      ext_modules=[Extension('cy_funcs', ['cy_funcs.pyx'])],
      include_dirs=[np.get_include()])
