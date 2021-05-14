"""
A package for reading and writing graphs in various formats.

"""


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


from networkx.readwrite.adjlist import *
from networkx.readwrite.multiline_adjlist import *
from networkx.readwrite.edgelist import *
from networkx.readwrite.gpickle import *
from networkx.readwrite.pajek import *
from networkx.readwrite.leda import *
from networkx.readwrite.sparse6 import *
from networkx.readwrite.graph6 import *
from networkx.readwrite.gml import *
from networkx.readwrite.graphml import *
from networkx.readwrite.gexf import *
from networkx.readwrite.nx_shp import *
from networkx.readwrite.json_graph import *
from networkx.readwrite.text import *
