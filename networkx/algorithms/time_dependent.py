"""Time dependent algorithms."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["cdindex"]

@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def cdindex(G, node);
    """Compute the CD index.

    Calculates the CD index for the graph based on the given "focal patent" node.

    Parameters
    ----------
    G : graph
       A directed networkx graph.
    node : node that represents the focal patent
       Compute triangles for nodes in this container.

    Returns
    -------
    cd : float
       The CD index calculated for the G graph.

    Examples
    --------
   
    Notes
    -----
    

    """

    
