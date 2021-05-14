"""
NetworkX
========

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

See https://networkx.org for complete documentation.
"""

__version__ = "2.6rc1.dev0"


def __getattr__(name):
    """Remove functions and provide informative error messages."""
    if name == "nx_yaml":
        raise ImportError(
            "\nThe nx_yaml module has been removed from NetworkX.\n"
            "Please use the `yaml` package directly for working with yaml data.\n"
            "For example, a networkx.Graph `G` can be written to and loaded\n"
            "from a yaml file as:\n\n"
            "    import yaml\n"
            "    yaml.dump(G, path_to_yaml_file)\n"
            "    yaml.load(path_to_yaml_file, Loader=yaml.Loader)"
        )
    if name == "read_yaml":
        raise ImportError(
            "\nread_yaml has been removed from NetworkX, please use `yaml`\n"
            "directly:\n\n"
            "    ``yaml.load(path, Loader=yaml.Loader)``"
        )
    if name == "write_yaml":
        raise ImportError(
            "\nwrite_yaml has been removed from NetworkX, please use `yaml`\n"
            "directly:\n\n"
            "    ``yaml.dump(G_to_be_yaml, path_for_yaml_output, **kwds)``"
        )
    raise AttributeError(f"module {__name__} has no attribute {name}")


# These are import orderwise
from networkx.exception import *
import networkx.utils

import networkx.classes.filters
import networkx.classes
from networkx.classes import *

import networkx.convert
from networkx.convert import *

import networkx.convert_matrix
from networkx.convert_matrix import *


import networkx.relabel
from networkx.relabel import *

import networkx.generators
from networkx.generators import *

import networkx.readwrite
from networkx.readwrite import *

# Need to test with SciPy, when available
import networkx.algorithms
from networkx.algorithms import *

import networkx.linalg
from networkx.linalg import *

from networkx.testing.test import run as test

import networkx.drawing
from networkx.drawing import *
