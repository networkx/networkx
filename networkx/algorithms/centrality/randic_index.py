"""Randic Index measures"""
import networkx as nx
import numpy as np

from networkx.utils import not_implemented_for

__all__ = ["randic_index"]

@not_implemented_for("directed")
def randic_index(G):
    #TODO: Finish documentation
    #TODO: Add randic algorithm to documentation
    
    """Compute the Randic index of the graph.

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    Returns
    -------
    index: int
      The integer value of the Randic index for the graph.
        

    Raises
    ------
    

    Examples
    --------
    >>> G = nx.erdos_renyi_graph(n=50, p=0.5)
    >>> print(nx.randic_index(G))
    25

    Notes
    -----
    ***Notes regarding bounds of Randic index go here***

    See Also
    --------
    
    """
    #TODO: add edge weights to graph? 
    #      Return graph with edges or just randic index?
    #      Is there a way to store the randic index in the graph?
    
    deg_dict = G.degree(G.nodes)
    index = np.sum([(1/np.sqrt(deg_dict[edge[0]]*deg_dict[edge[1]])) for edge in G.edges])
    
    return index