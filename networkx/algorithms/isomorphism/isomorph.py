"""
Graph isomorphism functions.

"""
__author__ = """Pieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import networkx as nx
from networkx.exception import NetworkXError

__all__ = ['could_be_isomorphic',
           'fast_could_be_isomorphic',
           'faster_could_be_isomorphic',
           'is_isomorphic']

def could_be_isomorphic(G1,G2):
    """Returns False if graphs are definitely not isomorphic.
    True does NOT guarantee isomorphism.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.

    Notes
    -----
    Checks for matching degree, triangle, and number of cliques sequences.
    """

    # Check global properties
    if G1.order() != G2.order(): return False

    # Check local properties
    d1=G1.degree()
    t1=nx.triangles(G1)
    c1=nx.number_of_cliques(G1)
    props1=[ [d1[v], t1[v], c1[v]] for v in d1 ]
    props1.sort()

    d2=G2.degree()
    t2=nx.triangles(G2)
    c2=nx.number_of_cliques(G2)
    props2=[ [d2[v], t2[v], c2[v]] for v in d2 ]
    props2.sort()

    if props1 != props2:
        return False

    # OK...
    return True

graph_could_be_isomorphic=could_be_isomorphic

def fast_could_be_isomorphic(G1,G2):
    """Returns False if graphs are definitely not isomorphic.
    True does NOT guarantee isomorphism.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.

    Notes
    -----
    Checks for matching degree and triangle sequences.
    """

    # Check global properties
    if G1.order() != G2.order(): return False

    # Check local properties
    d1=G1.degree()
    t1=nx.triangles(G1)
    props1=[ [d1[v], t1[v]] for v in d1 ]
    props1.sort()

    d2=G2.degree()
    t2=nx.triangles(G2)
    props2=[ [d2[v], t2[v]] for v in d2 ]
    props2.sort()

    if props1 != props2: return False

    # OK...
    return True

fast_graph_could_be_isomorphic=fast_could_be_isomorphic

def faster_could_be_isomorphic(G1,G2):
    """Returns False if graphs are definitely not isomorphic.
    True does NOT guarantee isomorphism.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.

    Notes
    -----
    Checks for matching degree sequences.
    """

    # Check global properties
    if G1.order() != G2.order(): return False

    # Check local properties
    d1=list(G1.degree().values())
    d1.sort()
    d2=list(G2.degree().values())
    d2.sort()

    if d1 != d2: return False

    # OK...
    return True

faster_graph_could_be_isomorphic=faster_could_be_isomorphic

def is_isomorphic(G1, G2, node_match=None, edge_match=None):
    """Returns True if the graphs G1 and G2 are isomorphic and False otherwise.

    Parameters
    ----------
    G1, G2: NetworkX graph instances
        The two graphs G1 and G2 must be the same type.

    node_match : callable
        A function that returns True iff node `n1` in `G1` and `n2` in `G2`
        should be considered equal during the isomorphism test. The
        function will be called like:

           node_match(G1.node[n1], G2.node[n2])

        That is, the function will receive the node attribute dictionaries
        of the nodes under consideration. If `None`, then no attributes are
        considered when testing for an isomorphism.

    edge_match : callable
        A function that returns True iff the edge attribute dictionary for
        the pair of nodes (u1, v1) in G1 and (u2, v2) in G2 should be
        considered equal during the isomorphism test. The function will be
        called like:

           edge_match(G1[u1][v1], G2[u2][v2])

        That is, the function will receive the edge attribute dictionaries
        of the edges under consideration. If `None`, then no attributes are
        considered when testing for an isomorphism.


    Notes
    -----
    Uses the vf2 algorithm.
    Works for Graph, DiGraph, MultiGraph, and MultiDiGraph.


    Examples
    --------
    >>> import networkx as nx
    >>> import networkx.isomorphism as nxiso

    For (di)graphs G1 and G2, using 'weight' edge attribute (default: 1)
    >>> em = nxiso.numerical_edge_match('weight', 1)
    >>> nx.is_isomorphic(G1, G2, edge_match=em)

    For (multi)(di)graphs G1 and G2, using 'fill' node attribute (default: '')
    >>> nm = nxiso.categorical_node_match('fill', 'red')
    >>> nx.is_isomorphic(G1, G2, node_match=nm)

    For multi(di)graphs G1 and G2, using 'weight' edge attribute (default: 2.3)
    >>> em = nxiso.numerical_multiedge_match('weight', 2.3)
    >>> nx.is_isomorphic(G1, G2, edge_match=em)

    For (di)graphs G1 and G2, using 'weight' and 'linewidth' edge attributes
    with default values 1 and 2.5. Also using 'fill' node attribute with
    default value 'red'.
    >>> em = nxiso.numerical_multiedge_match(['weight', 'lw'], [1, 2.5])
    >>> nm = nxiso.categorical_node_match('fill', 'red')
    >>> nx.is_isomorphic(G1, G2, edge_match=em, node_match=nm)


    See Also
    --------
    :mod:`isomorphvf2`, :mod:`matchelpers`
    numerical_node_match, numerical_edge_match, numerical_multiedge_match
    categorical_node_match, categorical_edge_match, categorical_multiedge_match

    """
    if G1.is_directed() and G2.is_directed():
        GM = nx.DiGraphMatcher
    elif (not G1.is_directed()) and (not G2.is_directed()):
        GM = nx.GraphMatcher
    else:
       raise NetworkXError("Graphs G1 and G2 are not of the same type.")

    gm = GM(G1, G2, node_match=node_match, edge_match=edge_match)

    return gm.is_isomorphic()

