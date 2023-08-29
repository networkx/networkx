"""
Time Series Graphs
"""
import itertools
from collections.abc import Iterable
from typing import Callable

import networkx as nx

__all__ = ["visibility_graph"]


def visibility_graph(series: Iterable[float]) -> nx.Graph:
    """
    Return a Visibility Graph of an input Time Series.

    It converts a time series into a graph. The constructed graph inherits several properties of the series in its
    structure. Thereby, periodic series convert into regular graphs, and random series do so into random graphs.
    Moreover, fractal series convert into scale-free networks.
    -- https://www.pnas.org/doi/10.1073/pnas.0709247105

    Parameters
    ----------
    series: Iterable[float]
       Time Series iterable of float values

    Returns
    -------
    NetworkX graph
        The Visibility Graph of series

    Examples
    --------
    >>> import random
    >>>
    >>> import networkx as nx
    >>> from matplotlib import pyplot
    >>>
    >>> series_list = [
    >>>     range(10),
    >>>     [2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3],
    >>>     random.sample(range(100), 100)
    >>> ]
    >>>
    >>> for s in series_list:
    >>>     g = nx.visibility_graph(s)
    >>>     print(g)
    >>>
    >>>     pos = [[x, 0] for x in range(len(s))]
    >>>     labels = nx.get_node_attributes(g, 'value')
    >>>     nx.draw_networkx_nodes(g, pos)
    >>>     nx.draw_networkx_labels(g, pos, labels=labels)
    >>>     nx.draw_networkx_edges(g, pos, arrows=True, connectionstyle='arc3,rad=-1.57079632679')
    >>>     pyplot.show()

    References
    ----------
    .. [1] Lucas Lacasa lucas@dmae.upm.es, Bartolo Luque, Fernando Ballesteros, Jordi Luque, and Juan Carlos Nuño,
       "From time series to complex networks: The visibility graph"
       Proceedings of the National Academy of Sciences,
       Vol. 105 | No. 1
       April 1, 2008
       PubMed: 18362361
       https://www.pnas.org/doi/10.1073/pnas.0709247105
    """

    def obstruction_predicate(
        n1: int, t1: float, n2: int, t2: float
    ) -> Callable[[int, float], bool]:
        slope = (t2 - t1) / (n2 - n1)
        constant = t2 - slope * n2

        def is_obstruction(n: int, t: float) -> bool:
            return t >= constant + slope * n

        return is_obstruction

    G = nx.Graph()
    # Check all combinations of nodes n series
    for s1, s2 in itertools.combinations(enumerate(series), 2):
        n1, t1 = s1
        n2, t2 = s2

        if n2 == n1 + 1:
            G.add_node(n1, value=t1)
            G.add_node(n2, value=t2)
            G.add_edge(n1, n2)
        else:
            is_obstruction = obstruction_predicate(n1, t1, n2, t2)
            obstructed = any(
                is_obstruction(n, t) for n, t in enumerate(series) if n1 < n < n2
            )
            if not obstructed:
                G.add_edge(n1, n2)

    return G
