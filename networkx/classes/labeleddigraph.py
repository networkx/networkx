from digraph import DiGraph
from labeledgraph import LabeledGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class LabeledDiGraph(LabeledGraph,DiGraph):
    pass  # just use the inherited classes
