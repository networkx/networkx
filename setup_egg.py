#!/usr/bin/env python
"""
An alternate setup.py script for setuptools.

If you have setuptools and run this as 

>>> python setup_egg.py bdist_egg

you will get a python egg.

Use

>>> python setup_egg.py nosetests

to run the tests.


"""
from setuptools import setup
from setup import *

if __name__ == "__main__":

    setup(
      name             = release.name,
      version          = release.version,
      author           = release.authors['Hagberg'][0],
      author_email     = release.authors['Hagberg'][1],
      description      = release.description,
      keywords         = release.keywords,
      long_description = release.long_description,
      license          = release.license,
      platforms        = release.platforms,
      url              = release.url,      
      download_url     = release.download_url,
      packages         = packages,
      data_files       = data,
      classifiers      = release.classifiers,
      package_data     = package_data,
#      include_package_data = True,
      install_requires=['setuptools'],
      test_suite       = 'nose.collector', 
      tests_require    = ['nose >= 0.10.1','networkx-nose-plugin>=0.1'] ,
      zip_safe = True
      )


