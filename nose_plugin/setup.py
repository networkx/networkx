"""
An example of how to create a simple nose plugin.

"""
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='networkx nose plugin',
    version='0.1',
    author='Aric Hagberg',
    author_email = 'hagberg@lanl.gov',
    description = 'NetworkX nose plugin',
    license = 'BSD',
    py_modules = ['networkxdoctest'],
    entry_points = {
        'nose.plugins.0.10': [
            'networkxdoctest = networkxdoctest:NetworkXDoctest'
            ]
        },
    )
