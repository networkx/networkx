"""
A package for reading and writing graphs in various formats.

"""

from networkx.readwrite.adjlist import *
from networkx.readwrite.multiline_adjlist import *
from networkx.readwrite.edgelist import *
from networkx.readwrite.pajek import *
from networkx.readwrite.leda import *
from networkx.readwrite.sparse6 import *
from networkx.readwrite.graph6 import *
from networkx.readwrite.gml import *
from networkx.readwrite.graphml import *
from networkx.readwrite.gexf import *
from networkx.readwrite.json_graph import *
from networkx.readwrite.text import *


def __getattr__(name):
    if name == "p2g":
        import warnings

        warnings.warn(
            (
                "\n\nThe p2g module is deprecated and will be removed in NetworkX 3.9"
                "\n\nIf you rely on this functionality, please add a comment to"
                "\nhttps://github.com/networkx/networkx/issues/8195"
            ),
            DeprecationWarning,
            stacklevel=2,
        )
    raise AttributeError(f"module 'networkx.readwrite' has no attribute '{name}'")
