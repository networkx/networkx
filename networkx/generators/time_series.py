"""
Time Series Graphs
"""
import itertools

import networkx as nx

__all__ = ["visibility_graph"]


def visibility_graph(series):
    """
    Return a Visibility Graph of an input Time Series.

    It converts a time series into a graph. The constructed graph inherits several properties of the series in its
    structure. Thereby, periodic series convert into regular graphs, and random series do so into random graphs.
    Moreover, fractal series convert into scale-free networks [1]_.

    Parameters
    ----------
    series: list[float] | tuple[float] | list[int] | tuple[int]
       Time Series iterable of float or int values

    Returns
    -------
    NetworkX Graph
        The Visibility Graph of the input series

    Examples
    --------
    >>> import networkx as nx
    >>> series_list = [range(10), [2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3]]
    >>> for s in series_list:
    ...     g = nx.visibility_graph(s)
    ...     print(g)
    Graph with 10 nodes and 9 edges
    Graph with 12 nodes and 18 edges

    References
    ----------
    .. [1] Lacasa, Lucas, Bartolo Luque, Fernando Ballesteros, Jordi Luque, and Juan Carlos Nuno.
           "From time series to complex networks: The visibility graph." Proceedings of the
           National Academy of Sciences 105, no. 13 (2008): 4972-4975.
           https://www.pnas.org/doi/10.1073/pnas.0709247105
    """

    # TODO: Consider adding support for generator, numpy array, pandas series etc.
    if not isinstance(series, (list, tuple, range)):
        raise nx.NetworkXError(
            "Input series must be a sliceable Iterable, "
            "i.e. of one the following types: list, tuple or range"
        )

    # Sequential values are always connected
    G = nx.path_graph(len(series))
    nx.set_node_attributes(G, dict(enumerate(series)), "value")

    # Check all combinations of nodes n series
    for s1, s2 in itertools.combinations(enumerate(series), 2):
        n1, t1 = s1
        n2, t2 = s2
        # check if any value between obstructs line of sight
        slope = (t2 - t1) / (n2 - n1)
        constant = t2 - slope * n2

        obstructed = any(
            t >= constant + slope * n
            for n, t in enumerate(series[n1 + 1 : n2], start=n1 + 1)
        )

        if not obstructed:
            G.add_edge(n1, n2)

    return G
