import itertools

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ["is_perfect_graph"]


@nx._dispatchable
@not_implemented_for("directed")
@not_implemented_for("multigraph")
def is_perfect_graph(G):
    r"""Return True if G is a perfect graph, else False.

    A graph G is perfect if, for every induced subgraph H of G, the chromatic
    number of H equals the size of the largest clique in H.

    According to the **Strong Perfect Graph Theorem (SPGT)**:
    A graph is perfect if and only if neither the graph G nor its complement
    :math:`\overline{G}` contains an **induced odd hole** — an induced cycle of
    odd length at least five without chords.

    Parameters
    ----------
    G : NetworkX Graph
        The graph to check. Must be a finite, simple, undirected graph.

    Returns
    -------
    bool
        True if G is a perfect graph, else False.

    Notes
    -----
    1. **Algorithm Time Complexity**

       This function uses a direct approach: cycle enumeration to detect
       chordless odd cycles in G and :math:`\overline{G}`. This implementation
       runs in exponential time in the worst case, since the number of chordless
       cycles can grow exponentially. It is intended for small and medium-sized
       graphs.

    2. **Comparison to Polynomial Recognition**

       The perfect-graph recognition problem is theoretically solvable in
       polynomial time. Chudnovsky *et al.* (2006) proved it can be solved in
       :math:`O(n^9)` time via a complex structural decomposition [1]_, [2]_.
       This implementation opts for a direct, transparent check rather than
       implementing that high-degree polynomial-time decomposition algorithm.

    3. **Related Specialized Algorithms**

        Several subclasses of perfect graphs, such as chordal graphs, bipartite graphs,
        and comparability graphs, already have specialized recognition algorithms in
        NetworkX (see `nx.is_chordal` and `nx.is_bipartite`).
        This function provides a general-purpose SPGT-based check for arbitrary graphs.

    References
    ----------
    .. [1] M. Chudnovsky, N. Robertson, P. Seymour, and R. Thomas,
           *The Strong Perfect Graph Theorem*,
           Annals of Mathematics, vol. 164, no. 1, pp. 51–229, 2006.
           https://doi.org/10.4007/annals.2006.164.51
    .. [2] M. Chudnovsky, G. Cornuéjols, X. Liu, P. Seymour, and K. Vušković,
           *Recognizing Berge Graphs*,
           Combinatorica 25(2): 143–186, 2005.
           DOI: 10.1007/s00493-005-0003-8
           Preprint available at:
           https://web.math.princeton.edu/~pds/papers/algexp/Bergealg.pdf
    """

    for cycle in _find_all_chordless_cycles(G):
        if len(cycle) >= 5 and len(cycle) % 2 == 1:
            return False
    return True


def _find_all_chordless_cycles(G):
    """Yield chordless cycles from both G and its complement."""
    yield from itertools.chain(
        nx.chordless_cycles(G), nx.chordless_cycles(nx.complement(G))
    )
