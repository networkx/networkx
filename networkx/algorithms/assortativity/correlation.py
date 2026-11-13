"""Node assortativity coefficients and correlation measures."""

from collections import defaultdict
from math import fsum, sqrt
from numbers import Integral

import networkx as nx
from networkx.algorithms.assortativity.mixing import (
    degree_mixing_dict,
    mixing_dict,
)
from networkx.algorithms.assortativity.pairs import node_attribute_xy, node_degree_xy

__all__ = [
    "degree_pearson_correlation_coefficient",
    "degree_assortativity_coefficient",
    "attribute_assortativity_coefficient",
    "numeric_assortativity_coefficient",
]


@nx._dispatchable(edge_attrs="weight")
def degree_assortativity_coefficient(G, x="out", y="in", weight=None, nodes=None):
    """Compute degree assortativity of graph.

    Assortativity measures the similarity of connections
    in the graph with respect to the node degree.

    Parameters
    ----------
    G : NetworkX graph

    x : string ('in','out')
       The degree type for source node (directed graphs only).

    y : string ('in','out')
       The degree type for target node (directed graphs only).

    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used
       as a weight.  If None, then each edge has weight 1.
       The degree is the sum of the edge weights adjacent to the node.

    nodes : list or iterable (optional)
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
    user-specified degree type for the source and target. The coefficient is
    evaluated from nonzero joint counts without constructing a dense mixing
    matrix.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    .. [2] Foster, J.G., Foster, D.V., Grassberger, P. & Paczuski, M.
       Edge direction and the structure of networks, PNAS 107, 10815-20 (2010).
    """
    d = degree_mixing_dict(G, x=x, y=y, nodes=nodes, weight=weight)
    return _numeric_ac(d)


@nx._dispatchable(edge_attrs="weight")
def degree_pearson_correlation_coefficient(G, x="out", y="in", weight=None, nodes=None):
    """Compute degree assortativity of graph.

    Assortativity measures the similarity of connections
    in the graph with respect to the node degree.

    This is the same as degree_assortativity_coefficient but uses the
    potentially faster scipy.stats.pearsonr function.

    Parameters
    ----------
    G : NetworkX graph

    x : string ('in','out')
       The degree type for source node (directed graphs only).

    y : string ('in','out')
       The degree type for target node (directed graphs only).

    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used
       as a weight.  If None, then each edge has weight 1.
       The degree is the sum of the edge weights adjacent to the node.

    nodes : list or iterable (optional)
        Compute pearson correlation of degrees only for specified nodes.
        The default is all nodes.

    Returns
    -------
    r : float
       Assortativity of graph by degree.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> r = nx.degree_pearson_correlation_coefficient(G)
    >>> print(f"{r:3.1f}")
    -0.5

    Notes
    -----
    This calls scipy.stats.pearsonr.

    Returns ``nan`` if the graph has fewer than two ``(degree, degree)``
    pairs, since the Pearson correlation coefficient is undefined in
    that case.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks
           Physical Review E, 67 026126, 2003
    .. [2] Foster, J.G., Foster, D.V., Grassberger, P. & Paczuski, M.
       Edge direction and the structure of networks, PNAS 107, 10815-20 (2010).
    """
    import scipy as sp

    xy = list(node_degree_xy(G, x=x, y=y, nodes=nodes, weight=weight))
    if len(xy) < 2:
        return float("nan")
    x, y = zip(*xy)
    return float(sp.stats.pearsonr(x, y)[0])


@nx._dispatchable(node_attrs="attribute")
def attribute_assortativity_coefficient(G, attribute, nodes=None):
    """Compute assortativity for node attributes.

    Assortativity measures the similarity of connections
    in the graph with respect to the given attribute.

    Parameters
    ----------
    G : NetworkX graph

    attribute : string
        Node attribute key

    nodes : list or iterable (optional)
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
    >>> print(nx.attribute_assortativity_coefficient(G, "color"))
    1.0

    Notes
    -----
    This computes Eq. (2) in Ref. [1]_ , (trace(M)-sum(M^2))/(1-sum(M^2)),
    where M is the joint probability distribution (mixing matrix)
    of the specified attribute. The coefficient is evaluated using exact
    integer counts of matching endpoints and the two marginal distributions,
    without constructing a dense mixing matrix. It is undefined (NaN) when
    there are no observations or all endpoints have the same attribute.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    """
    marginals = defaultdict(lambda: [0, 0])
    total = matched = 0
    for x, y in node_attribute_xy(G, attribute, nodes):
        source = marginals[x]
        target = marginals[y]
        source[0] += 1
        target[1] += 1
        total += 1
        # Compare canonical records to retain dictionary-key semantics,
        # including identity matches for the same NaN category object.
        if source is target:
            matched += 1
    expected = sum(outgoing * incoming for outgoing, incoming in marginals.values())
    denominator = total * total - expected
    if not denominator:
        return float("nan")
    return (total * matched - expected) / denominator


@nx._dispatchable(node_attrs="attribute")
def numeric_assortativity_coefficient(G, attribute, nodes=None):
    """Compute assortativity for numerical node attributes.

    Assortativity measures the similarity of connections
    in the graph with respect to the given numeric attribute.

    Parameters
    ----------
    G : NetworkX graph

    attribute : string
        Node attribute key.

    nodes : list or iterable (optional)
        Compute numeric assortativity only for attributes of nodes in
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
    >>> print(nx.numeric_assortativity_coefficient(G, "size"))
    1.0

    Notes
    -----
    This computes Eq. (21) in Ref. [1]_ , which is the Pearson correlation
    coefficient of the specified (scalar valued) attribute across edges.
    The coefficient is evaluated from nonzero joint counts without constructing
    a dense mixing matrix. Centering and scaling the attribute values avoids
    squaring large values or subtracting nearly equal raw moments.

    Returns ``nan`` when no selected edge pairs exist or either endpoint
    distribution has zero variance.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks
           Physical Review E, 67 026126, 2003
    """
    nodes = set(G) if nodes is None else set(nodes)
    vals = {G.nodes[n][attribute] for n in nodes}
    # Preserve the support restriction of the previous mixing-matrix mapping.
    # A selected source can have an unselected neighbor with a selected value.
    xy = ((x, y) for x, y in node_attribute_xy(G, attribute, nodes) if y in vals)
    return _numeric_ac(mixing_dict(xy))


def attribute_ac(M):
    """Compute assortativity for attribute matrix M.

    Parameters
    ----------
    M : numpy.ndarray
        2D ndarray representing the attribute mixing matrix.

    Notes
    -----
    This computes Eq. (2) in Ref. [1]_ , (trace(e)-sum(e^2))/(1-sum(e^2)),
    where e is the joint probability distribution (mixing matrix)
    of the specified attribute.

    References
    ----------
    .. [1] M. E. J. Newman, Mixing patterns in networks,
       Physical Review E, 67 026126, 2003
    """
    if M.sum() != 1.0:
        M = M / M.sum()
    s = (M @ M).sum()
    t = M.trace()
    r = (t - s) / (1 - s)
    return float(r)


def _numeric_ac(mixing):
    """Pearson correlation from nonzero joint counts, without a dense matrix."""
    xcounts = {}
    ycounts = {}
    for x, row in mixing.items():
        for y, count in row.items():
            xcounts[x] = xcounts.get(x, 0) + count
            ycounts[y] = ycounts.get(y, 0) + count
    n = sum(xcounts.values())
    if not n:
        return float("nan")

    x = _normalized_marginal(xcounts, n)
    y = _normalized_marginal(ycounts, n)
    if x is None or y is None:
        return float("nan")
    r = fsum(
        count * x[u] * y[v] for u, row in mixing.items() for v, count in row.items()
    )
    # Roundoff can otherwise put a perfectly correlated result just outside
    # the mathematical bounds.
    return max(-1.0, min(1.0, r))


def _normalized_marginal(counts, n):
    """Center and normalize one marginal using O(number of values) storage."""
    import numpy as np

    # Subtract integer origins in Python, before converting to floating point.
    # This avoids both fixed-width overflow and loss of small differences
    # between large integer values.
    values = [v.item() if isinstance(v, np.generic) else v for v in counts]
    values = [int(v) if isinstance(v, Integral) else v for v in values]
    if any(not np.isfinite(v) for v in values if not isinstance(v, Integral)):
        return None
    origin = values[0]
    try:
        with np.errstate(over="ignore", invalid="ignore"):
            differences = [v - origin for v in values]
        finite = all(isinstance(d, Integral) or np.isfinite(d) for d in differences)
    except OverflowError:
        finite = False
    if not finite:
        # Two finite values can have a difference outside the floating-point
        # range. Compute only this uncommon case as exact ratios, then scale
        # it into [-1, 1] before converting to float.
        from fractions import Fraction

        ratios = [
            Fraction(v) if isinstance(v, Integral) else Fraction(*v.as_integer_ratio())
            for v in values
        ]
        differences = [v - ratios[0] for v in ratios]
    scale = max(abs(d) for d in differences)
    if not scale:
        return None
    offsets = [float(d / scale) for d in differences]
    mean = fsum(count * offset for count, offset in zip(counts.values(), offsets)) / n
    centered = [offset - mean for offset in offsets]
    norm = sqrt(fsum(count * d * d for count, d in zip(counts.values(), centered)))
    if not norm:
        return None
    return {v: d / norm for v, d in zip(counts, centered)}
