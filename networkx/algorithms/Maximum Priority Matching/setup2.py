from setuptools import setup
from Cython.Build import cythonize

setup(
    name="algo2_library",
    ext_modules=cythonize("algo2_library.pyx")
)