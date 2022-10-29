"""
NetworkX
========

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

See https://networkx.org for complete documentation.
"""

__version__ = "3.0b2.dev0"

import lazy_loader as lazy

__getattr__, __stubdir__, __all__ = lazy.attach_stub(__name__, __file__)


def __dir__():
    return ["__version__"] + __all__
