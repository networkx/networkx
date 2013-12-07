"""
A package for generating various graphs in networkx. 

"""
import sys

if not sys.platform.startswith('java'):
    # only import atlas if the interpreter is not Jython. This is
    # because in Java the maximum allowed size for a method is 64k,
    # and graph_atlas_g is larger than that.
    from networkx.generators.atlas import *
from networkx.generators.bipartite import *
from networkx.generators.classic import *
from networkx.generators.degree_seq import *
from networkx.generators.directed import *
from networkx.generators.ego import *
from networkx.generators.geometric import *
from networkx.generators.hybrid import *
from networkx.generators.line import *
from networkx.generators.random_graphs import *
from networkx.generators.small import *
from networkx.generators.stochastic import *
from networkx.generators.social import *
from networkx.generators.threshold import *
from networkx.generators.intersection import *
from networkx.generators.random_clustered import *

