"""Node assortativity coefficients and correlation measures.
"""
from networkx.algorithms.assortativity.mixing import attribute_mixing_matrix
from networkx.algorithms.assortativity.pairs import node_attribute_xy, node_degree_xy

__all__ = [
    "degree_assortativity_coefficient",
    "discrete_assortativity_coefficient",
    "scalar_assortativity_coefficient",
]


def degree_assortativity_coefficient(G, x="out", y="in", weight=None, nodes=None):
    """Compute degree assortativity of graph.

    Assortativity measures the similarity of connections
    in the graph with respect to the node degree.

    Parameters
    ----------
    G : NetworkX graph

    x: string ('in','out')
       The degree type for source node (directed graphs only).

    y: string ('in','out')
       The degree type for target node (directed graphs only).

    weight: string or None, optional (default=None)
       The edge attribute that holds the numerical value used
       as a weight.  If None, then each edge has weight 1.
       The degree is the sum of the edge weights adjacent to the node.

    nodes: list or iterable (optional)
        Compute degree assortativity only for nodes in container.
        The default is all nodes.

    Returns
    -------
    r : float
       Assortativity of graph by degree.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> r = nx.degree_assortativity_coefficient(G)
    >>> print(f"{r:3.1f}")
    -0.5

    See Also
    --------
    attribute_assortativity_coefficient
    numeric_assortativity_coefficient
    degree_mixing_dict
    degree_mixing_matrix

    Notes
    -----
    This computes Eq. (21) in Ref. [1]_ , where e is the joint
    probability distribution (mixing matrix) of the degrees.  If G is
    directed than the matrix e is the joint probability of the
    user-specified degree type for the source and target.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    .. [2] Foster, J.G., Foster, D.V., Grassberger, P. & Paczuski, M.
       Edge direction and the structure of networks, PNAS 107, 10815-20 (2010)
    """
    import numpy as np

    xy = node_degree_xy(G, x=x, y=y, nodes=nodes, weight=weight)
    x, y = zip(*xy)
    return np.corrcoef(x, y)[0, 1]


def discrete_assortativity_coefficient(G, attribute, nodes=None):
    """Compute assortativity for discrete node attributes.

    Assortativity measures the similarity of connections
    in the graph with respect to the given attribute.

    Parameters
    ----------
    G : NetworkX graph

    attribute : string
        Node attribute key

    nodes: list or iterable (optional)
        Compute attribute assortativity for nodes in container.
        The default is all nodes.

    Returns
    -------
    r: float
       Assortativity of graph for given attribute

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_nodes_from([0, 1], color="red")
    >>> G.add_nodes_from([2, 3], color="blue")
    >>> G.add_edges_from([(0, 1), (2, 3)])
    >>> print(nx.discrete_assortativity_coefficient(G, "color"))
    1.0

    Notes
    -----
    This computes Eq. (2) in Ref. [1]_ , (trace(M)-sum(M^2))/(1-sum(M^2)),
    where M is the joint probability distribution (mixing matrix)
    of the specified attribute.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    """
    M = attribute_mixing_matrix(G, attribute, nodes, normalized=True)
    s = (M @ M).sum()
    t = M.trace()
    r = (t - s) / (1 - s)
    return r


def scalar_assortativity_coefficient(G, attribute, nodes=None):
    """Compute assortativity for scalar node attributes.

    Assortativity measures the similarity of connections
    in the graph with respect to the given scalar attribute.

    Parameters
    ----------
    G : NetworkX graph

    attribute : string
        Node attribute key.

    nodes: list or iterable (optional)
        Compute scalar assortativity only for attributes of nodes in
        container. The default is all nodes.

    Returns
    -------
    r: float
       Assortativity of graph for given attribute

    Examples
    --------
    >>> G = nx.Graph()
    >>> G.add_nodes_from([0, 1], size=2)
    >>> G.add_nodes_from([2, 3], size=3)
    >>> G.add_edges_from([(0, 1), (2, 3)])
    >>> print(nx.scalar_assortativity_coefficient(G, "size"))
    1.0

    Notes
    -----
    This computes Eq. (21) in Ref. [1]_ , which is the Pearson correlation
    coefficient of the specified (scalar valued) attribute across edges.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks
           Physical Review E, 67 026126, 2003
    """
    import numpy as np

    xy = node_attribute_xy(G, attribute, nodes=nodes)
    x, y = zip(*xy)
    return np.corrcoef(x, y)[0, 1]
