"""
Transport Networks
"""
import itertools
import operator

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ("gradient_network",)


def _value_getter(value):
    return value() if callable(value) else value


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def gradient_network(
    G, scalar_field_value="value", scalar_field_distance="distance", ascending=True
):
    """
    Returns a Gradient Network graph of an input substrate network graph.

    In network science, a Gradient Network is a directed subnetwork of an undirected
    "substrate" network where each node has an associated scalar potential and one
    out-link that points to the node with the largest (or smallest) potential in its
    neighborhood, defined as the union of itself and its neighbors on the substrate
    network [2]_.

    Parameters
    ----------
    G: NetworkX Graph
        Substrate Network graph. Does not support directed graphs and multigraphs.
        The graph nodes should have an attribute as a source for the scalar field value.
        A node `value` attribute should be either a `Number` (e.g.int, float, etc.) or a
        `Callable` that returns a Number.
        The graph edges may have an attribute as a source of a `distance` value.
        An edge `distance` attribute may be either a `Number` or a `Callable` that
        returns a Number.
    scalar_field_value: str | Callable[[], int | float]. Default: 'value'.
        The attribute name for the source of the scalar field value.
    scalar_field_distance: str Callable[[], int | float]. Default: 'distance'.
        The attribute name for the source of the scalar field distance.
    ascending: bool
        Choose an ascending (True) or descending (False) gradient graph. Default: True.

    Returns
    -------
    NetworkX DiGraph
        The Gradient Network graph of the input substrate graph

    Examples
    --------

    References
    ----------
    .. [1] Toroczkai, Zoltán; Kozma, Balázs; Bassler, Kevin E; Hengartner, N W;
           Korniss, G (2008-04-02).
           "Gradient networks". Journal of Physics A: Mathematical and Theoretical.
           IOP Publishing. 41 (15): 155103. arXiv:cond-mat/0408262.
           Bibcode:2008JPhA...41o5103T. doi:10.1088/1751-8113/41/15/155103.
           ISSN 1751-8113. S2CID 118983053.
           https://arxiv.org/abs/cond-mat/0408262v1
           https://doi.org/10.48550/arXiv.cond-mat/0408262
    .. [2] Danila, Bogdan; Yu, Yong; Earl, Samuel; Marsh, John A.; Toroczkai, Zoltán;
           Bassler, Kevin E. (2006-10-19).
           "Congestion-gradient driven transport on complex networks".
           Physical Review E. 74 (4): 046114. arXiv:cond-mat/0603861.
           Bibcode:2006PhRvE..74d6114D. doi:10.1103/physreve.74.046114. ISSN 1539-3755.
           PMID 17155140. S2CID 16009613.
           https://arxiv.org/abs/cond-mat/0603861
           https://doi.org/10.48550/arXiv.cond-mat/0603861
           https://journals.aps.org/pre/abstract/10.1103/PhysRevE.74.046114
    """

    H = nx.DiGraph()

    scalar_operation = max if ascending else min
    for node, h in G.nodes(data=scalar_field_value, default=0):
        h = _value_getter(h)

        scalar_field_values = itertools.chain(
            (
                (n, _value_getter(G.nodes[n].get(scalar_field_value, 0)))
                for n in G.neighbors(node)
            ),
            ((node, h),),
        )
        neighbor, neighbor_h = scalar_operation(
            scalar_field_values, key=operator.itemgetter(1)
        )
        distance = (
            G.get_edge_data(node, neighbor, default={}).get(scalar_field_distance)
            or 1.0
        )
        H.add_edge(node, neighbor, size=abs(h - neighbor_h) / distance)
    return H
