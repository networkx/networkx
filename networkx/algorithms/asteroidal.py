"""
Algorithms for asteroidal triples and asteroidal numbers in graphs.

An asteroidal triple in a graph G is a set of three non-adjacent vertices
u, v and w such that there exist a path between any two of them that avoids
closed neighborhood of the third. More formally, v_j, v_k belongs to the same
connected component of G - N[v_i], where N[v_i] denotes the closed neighborhood
of v_i. A graph which does not contain any asteroidal triples is called
an AT-free graph. The class of AT-free graphs is a graph class for which
many NP-complete problems are solvable in polynomial time. Amongst them,
independent set and coloring.
"""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["is_at_free", "find_asteroidal_triple"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def find_asteroidal_triple(G):
    r"""Find an asteroidal triple in the given graph.

    An asteroidal triple is a triple of non-adjacent vertices such that
    there exists a path between any two of them which avoids the closed
    neighborhood of the third. It checks all independent triples of vertices
    and whether they are an asteroidal triple or not. This is done with the
    help of a data structure called a component structure.
    A component structure encodes information about which vertices belongs to
    the same connected component when the closed neighborhood of a given vertex
    is removed from the graph. The algorithm used to check is the trivial
    one, outlined in [1]_, which has a runtime of
    :math:`O(|V||\overline{E} + |V||E|)`, where the second term is the
    creation of the component structure.

    Parameters
    ----------
    G : NetworkX Graph
        The graph to check whether is AT-free or not

    Returns
    -------
    list or None
        An asteroidal triple is returned as a list of nodes. If no asteroidal
        triple exists, i.e. the graph is AT-free, then None is returned.

    Notes
    -----
    The component structure and the algorithm is described in [1]_. The current
    implementation implements the trivial algorithm for simple graphs.

    References
    ----------
    .. [1] Ekkehard Köhler,
       "Recognizing Graphs without asteroidal triples",
       Journal of Discrete Algorithms 2, pages 439-452, 2004.
       https://www.sciencedirect.com/science/article/pii/S157086670400019X
    """
    V = set(G)

    if len(V) < 6:
        # An asteroidal triple cannot exist in a graph with 5 or fewer vertices.
        return None

    component_structure = _create_component_structure(G)

    seen_u = set()
    for u, csu in component_structure.items():
        seen_u.add(u)
        seen_v = set()
        for v in (Vu := V - (G._adj[u].keys() | seen_u)):
            seen_v.add(v)
            csv = component_structure[v]
            for w in Vu - (G._adj[v].keys() | seen_v):
                csw = component_structure[w]
                # Check for each pair of vertices whether they belong to the
                # same connected component when the closed neighborhood of the
                # third is removed.
                if csu[v] == csu[w] and csv[u] == csv[w] and csw[u] == csw[v]:
                    return [u, v, w]
    return None


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def is_at_free(G):
    """Check if a graph is AT-free.

    The method uses the `find_asteroidal_triple` method to recognize
    an AT-free graph. If no asteroidal triple is found the graph is
    AT-free and True is returned. If at least one asteroidal triple is
    found the graph is not AT-free and False is returned.

    Parameters
    ----------
    G : NetworkX Graph
        The graph to check whether is AT-free or not.

    Returns
    -------
    bool
        True if G is AT-free and False otherwise.

    Examples
    --------
    >>> G = nx.Graph([(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (4, 5)])
    >>> nx.is_at_free(G)
    True

    >>> G = nx.cycle_graph(6)
    >>> nx.is_at_free(G)
    False
    """
    return find_asteroidal_triple(G) is None


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def _create_component_structure(G):
    r"""Create component structure for G.

    A *component structure* is an `nxn` array, denoted `c`, where `n` is
    the number of vertices,  where each row and column corresponds to a vertex.

    .. math::
        c_{uv} = \begin{cases} 0, if v \in N[u] \\
            k, if v \in component k of G \setminus N[u] \end{cases}

    Where `k` is an arbitrary label for each component. The structure is used
    to simplify the detection of asteroidal triples.

    Parameters
    ----------
    G : NetworkX Graph
        Undirected, simple graph.

    Returns
    -------
    component_structure : dictionary
        A dictionary of dictionaries, keyed by pairs of vertices.

    """
    V = set(G)
    ccfn = nx.connected_components  # To make the generator expression more readable.
    return {
        v: {
            u: i
            for i, cc in enumerate(ccfn(G.subgraph(V - (v_nbrs.keys() | {v}))))
            for u in cc
        }
        for v, v_nbrs in G.adjacency()
    }
