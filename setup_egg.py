
#!/usr/bin/env python
"""
An alternate setup.py script that uses setuptools.

You can install networkx with

python setup_egg.py install

If you have setuptools and run this as 

python setup_egg.py bdist_egg

you will get a Python egg.

Use

python setup_egg.py nosetests

to run the tests.


"""
# local import, might need modification for 2.6/3.0
from setup import *

# must occur after local import to override distutils.core.setup
from setuptools import setup


if __name__ == "__main__":

    setup(
        name             = release.name.lower(),
        version          = version,
        maintainer       = release.maintainer,
        maintainer_email = release.maintainer_email,
        author           = release.authors['Hagberg'][0],
        author_email     = release.authors['Hagberg'][1],
        description      = release.description,
        keywords         = release.keywords,
        long_description = release.long_description,
        license          = release.license,
        platforms        = release.platforms,
        url              = release.url,      
        download_url     = release.download_url,
        classifiers      = release.classifiers,
        packages         = packages,
        data_files       = data,
        package_data     = package_data,
        install_requires=['setuptools'],
        test_suite       = 'nose.collector', 
        tests_require    = ['nose >= 0.10.1'] ,
        zip_safe = False
      )


