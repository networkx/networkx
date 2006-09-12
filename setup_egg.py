#!/usr/bin/env python
"""
An alternate setup.py script that uses setuptools.

If you have setuptools and run this as e.g.
python setup_egg.py bdist_egg
you will get a python egg.

"""
from setuptools import setup, Extension
execfile('setup.py')

