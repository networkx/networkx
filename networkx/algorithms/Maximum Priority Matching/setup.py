from setuptools import setup
from Cython.Build import cythonize

setup(
    name="preparation",
    ext_modules=cythonize("preparation.pyx")
)