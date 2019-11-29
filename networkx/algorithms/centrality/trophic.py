"""Trophic levels"""
import networkx as nx
import numpy as np

from networkx.utils import not_implemented_for

__all__ = ['trophic_levels']


@not_implemented_for('undirected')
def trophic_levels(G, weight='weight'):
    """Compute the trophic levels of nodes.

    The trophic level of a node $i$ is

    .. math::

        s_i = 1 + \frac{1}{k_^{in}_i \sum_{j} a_{ij} s_j

    where $k_^{in}_i$ is the in-degree of i

    .. math::

        k^{in}_i = \sum_{j} a_{ij}

    and nodes with $k_^{in}_i = 0$ have $s_i = 1$ by convention.

    These are calculated using the method outlined in Stephen Levine (1980) J. theor. Biol. 83, 195-207

    Parameters
    ----------
    G : DiGraph
        A directed networkx graph

    Returns
    -------
    nodes : dict
        Dictionary of nodes with trophic level as the vale.
    """
    # defensive copy is required - we plan to drop nodes
    G = G.copy()

    # drop nodes of in-degree zero, keep a list of ids
    z = [nid for nid, d in G.in_degree if d == 0]
    for nid in z:
        G.remove_node(nid)

    # find adjacency matrix
    q = nx.linalg.graphmatrix.adjacency_matrix(G, weight=weight).T

    # must be square, size of number of nodes
    assert len(q.shape) == 2
    assert q.shape[0] == q.shape[1]
    assert q.shape[0] == len(G)

    nn = q.shape[0]

    i = np.eye(nn)
    n = np.linalg.inv(i - q)
    y = np.dot(np.asarray(n), np.ones(nn)) + 1

    levels = {}

    # all nodes with degree zero have trophic level == 1
    for nid in z:
        levels[nid] = 1

    # all other nodes have levels as calculated
    for i, nid in enumerate(G.nodes):
        levels[nid] = y[i]

    return levels


# trophic_difference for each edge is $x_ij = s_i - s_j$
# trophic_coherence is the standard deviation of trophic distances
