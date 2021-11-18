"""
Implementation of the unweighted strong connectivity augmentation algorithm
due to Eswaran and Tarjan, see ESWARAN, Kapali P; TARJAN, R Endre. Augmentation problems.
SIAM Journal on Computing. 1976, vol. 5, no. 4, pp. 653–665 and its correction, due to
RAGHAVAN, S. A note on Eswaran and Tarjan’s algorithm for the strong connectivity augmentation problem.
In: The Next Wave in Computing, Optimization, and Decision Technologies. Springer, 2005, pp. 19–26.
"""

from typing import List, Set

import networkx as nx
from networkx.utils.decorators import not_implemented_for
from networkx.algorithms import source, sink, isolate

__author__ = '\n'.join(['Tomas Jelinek <tomasjelinek96@gmail.com>'])

__all__ = ['eswaran_tarjan']

@not_implemented_for('undirected')
@not_implemented_for('multigraph')
def eswaran_tarjan(G: nx.DiGraph, is_condensation: bool = False, sourcesSinksIsolated=None) -> Set:
    """Returns a set of edges A such that G(V, E + A) is strongly connected.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    is_condensation : bool
        Generic value False, True if G has no strongly connected component.
        If False, strongly connected components will be computed.
    sourcesSinksIsolated : (Set, Set, Set)
        Sources, sinks and isolated vertices of G as defined in the original paper. If not provided, will be computed.
    Returns
    -------
    A : Set
       Set of directed edges (u, v) such that G(V, E + A) is strongly connected,
       returns an empty set for an empty graph.

    Raises
    ------
    NetworkX.NotImplemented:
        If G is undirected or a multigraph.
    Notes
    -----
    Modified version of Eswaran's and Tarjan's algorithm https://epubs.siam.org/doi/abs/10.1137/0205044
    and it's correction due to S. Raghavan https://link.springer.com/chapter/10.1007/0-387-23529-9_2
    """

    G_condensation: nx.DiGraph

    if not is_condensation:
        G_condensation = nx.algorithms.condensation(G)
    else:
        G_condensation = G

    if len(G_condensation.nodes) <= 1:  # The trivial case can be handled here
        return set()

    if sourcesSinksIsolated is None:
        isolated = set(isolate.isolates(G_condensation))
        sources = set(source.sources(G_condensation)) - isolated
        sinks = set(sink.sinks(G_condensation)) - isolated
    else:
        sources, sinks, isolated = sourcesSinksIsolated

    s: int = len(sources)  # Number of sinks
    t: int = len(sinks)  # Number ou sources
    q: int = len(isolated)  # Number of isolated vertices

    is_reversed = False

    # If G_condensation has more sources than sinks, algorithm does not work.
    # However, we can work on reversed graph and reverse edges in A later on.
    if s > t:
        is_reversed = True
        s, t = t, s
        sources, sinks = sinks, sources
        G_condensation = G_condensation.reverse(copy=False)

    v_list: List = []
    w_list: List = []

    def search(x):
        stack = [x]  # First vert to visit is x

        while len(stack) > 0:  # While there is a visited non-processed vertex
            y = stack.pop()
            unmarked.discard(y)
            if y in sinks:  # We discovered there is an unmarked x-y path
                return y

            for z in G_condensation[y]:
                if z in unmarked:  # No need to process already visited
                    stack.append(z)

        return None  # There is no unmarked x-w path, where w is a sink

    unmarked: Set = set(G_condensation.nodes)  # Initialize all nodes as unmarked
    unmarked_sources: Set = (set(G_condensation.nodes)).intersection(sources)

    while unmarked_sources:  # Some source is unmarked
        v = unmarked_sources.pop()  # Choose some unmarked source v
        w = search(v)
        if w is not None:  # None is returned when path to sink is blocked
            v_list.append(v)
            w_list.append(w)
            sources.remove(v)
            sinks.remove(w)

    p: int = len(v_list)  # This is equivalent with p proposed in the original algorithm

    # The edges not in v resp. w can be appended in an ambiguous ordering
    v_list.extend(sources)
    w_list.extend(sinks)
    x_list = list(isolated)

    #  We can choose any member of a strongly connected component as a representative
    if not is_condensation:  # But only if G is not a condensation itself
        v_list = list(map(lambda x: next(iter(G_condensation.nodes[x]['members'])), v_list))
        w_list = list(map(lambda x: next(iter(G_condensation.nodes[x]['members'])), w_list))
        x_list = list(map(lambda x: next(iter(G_condensation.nodes[x]['members'])), isolated))

    A: Set = set()

    for i in range(0, p - 1):  # Covers (w_0, v_1) ... (w_p-2, v_p-1)
        A.add((w_list[i], v_list[i + 1]))

    for i in range(p, s):  # Covers (w_p, v_p) ... (w_s-1, v_s-1)
        A.add((w_list[i], v_list[i]))

    for i in range(s, t - 1):  # Covers (w_s, w_s+1) ... (w_t-2, w_t-1)
        A.add((w_list[i], w_list[i + 1]))

    for i in range(0, q - 1):  # Covers (x_0, x_1) ... (x_q-2, x_q-1)
        A.add((x_list[i], x_list[i + 1]))

    if p == 0:  # This also ensures that s == t == 0 and q > 1
        A.add((x_list[q - 1], x_list[0]))  # Covers (x_q-1, x_0) closing the cycle
    else:  # p > 0, p > 0 iff s, t > 0
        if s == t:
            if q == 0:
                A.add((w_list[p - 1], v_list[0]))  # Covers (w_p-1, v_0) closing the cycle
            else:  # q > 0
                A.add((w_list[p - 1], x_list[0]))  # Covers (w_p-1, x_0)
                A.add((x_list[q - 1], v_list[0]))  # Covers (x_q-1, v_0) closing the cycle
        else:  # t > s
            A.add((w_list[p - 1], w_list[s]))  # Covers (w_p-1, w_s)
            if q == 0:
                A.add((w_list[t - 1], v_list[0]))  # Covers (w_t-1, v_0)
            else:  # q > 0
                A.add((w_list[t - 1], x_list[0]))  # Covers (w_t-1, x_0)
                A.add((x_list[q - 1], v_list[0]))  # Covers (x_q-1, v_0) closing the cycle

    if is_reversed:
        A = set(map(lambda e: (e[1], e[0]), A))  # We simply swap the edge direction

    return A
