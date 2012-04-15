"""
Operations on many graphs.
"""
#    Copyright (C) 2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
try:
    from itertools import izip_longest as zip_longest
except ImportError: # Python3 has zip_longest
    from itertools import zip_longest
import networkx as nx
from networkx.utils import is_string_like

__author__ = """\n""".join([ 'Robert King <kingrobertking@gmail.com>',
                             'Aric Hagberg <aric.hagberg@gmail.com>'])

__all__ = ['union_all', 'compose_all', 'disjoint_union_all',
           'intersection_all']

def union_all(graphs, rename=(None,) , name=None):
    """Return the union of all graphs

    The graphs must be disjoint, otherwise an exception is raised.

    Parameters
    ----------
    graphs : list of graphs
       Multiple NetworkX graphs

    rename : bool , default=(None, None)
       Node names of G and H can be changed by specifying the tuple
       rename=('G-','H-') (for example).  Node "u" in G is then renamed
       "G-u" and "v" in H is renamed "H-v".

    name : string
       Specify the name for the union graph

    Returns
    -------
    U : A union of graph with the same type as the first graph.

    Notes
    -----
    To force a disjoint union with node relabeling, use
    disjoint_union_all(G,H) or convert_node_labels_to integers().

    Graph, edge, and node attributes are propagated supplied graphs
    to the union graph.  If a graph attribute is present in multiple
    graphs, then the first graph with that attribute takes priority.

    See Also
    --------
    union
    """
    graphs_names = zip_longest(graphs,rename)
    U, gname = next(graphs_names)
    for H,hname in graphs_names:
        U = nx.union(U, H, (gname,hname),name=name)
        gname = None
    return U

def disjoint_union_all(graphs):
    """ Return the disjoint union of graphs, forcing distinct integer
    node labels.

    Parameters
    ----------
    graphs : list
       Multiple NetworkX graph

    Returns
    -------
    U : A union of graph with the same type as the first graph.

    Notes
    -----
    A new graph is created, of the same class as the first graph.
    It is recommended that the graphs be either all directed or all undirected.
    """
    U = graphs.pop(0)
    for H in graphs:
        U = nx.disjoint_union(U, H)
    return U

def compose_all(graphs, name=None):
    """Return a new graph, the composition of supplied graphs

    Composition is the simple union of the node sets and edge sets.
    The node sets of the supplied graphs need not be disjoint.

    Parameters
    ----------
    graphs : list of graphs
       Multiple NetworkX graphs

    name : string
       Specify name for new graph

    Returns
    -------
    R : A new graph with the same type as the first graph

    Notes
    -----
    A new graph is returned, of the same class as the first graph in the list.
    It is recommended that the supplied graphs be either all directed or all
    undirected.  If a graph attribute is present in multiple graphs,
    then the first graph in the graphs_list with that attribute takes
    priority for that attribute
    """
    C = graphs.pop(0)
    for H in graphs:
        C = nx.compose(C, H, name=name)
    return C

def intersection_all(graphs):
    """Return a new graph that contains only the edges that exist in
    all graphs.

    All supplied graphs must have the same node set.

    Parameters
    ----------
    graphs_list : list
       Multiple NetworkX graphs.  Graphs must have the same node sets.

    Returns
    -------
    R : A new graph with the same type as the first graph

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.
    """
    R = graphs.pop(0)
    for H in graphs:
        R = nx.intersection(R, H)
    return R
