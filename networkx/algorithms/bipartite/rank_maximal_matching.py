import networkx as nx
from networkx.algorithms.bipartite import sets as bipartite_sets


def rank_maximal_matching(G, rank="rank", top_nodes=None):
    """Returns the rank maximal matching of the ranked bipartite graph `G`.

    A ranked graph is a graph in which every edge has a rank [1,r]
    (the algorithm ignores non-positive ranks)
    such that 1 is the highest rank, and then 2 is the next highest rank, and so on.
    A matching is a set of edges that do not share any nodes.
    A rank-maximal matching is one with the maximum
    possible number of edges with the first rank, and subject to that condition,
    the maximum possible number of edges with the second rank, and so on.

    Parameters
    ----------
    G : NetworkX graph
      Undirected weighted (the weight of every edge represents the rank) bipartite graph

    Returns
    -------
    M : dictionary
       The matching is returned as a dictionary, `matching`, such that
         ``matching[v] == w`` if node `v` is matched to node `w`. Unmatched
        nodes do not occur as a key in `matching`.

    Examples
    --------
    In the bipartite graph, G = (V,E). with the sets V1 as 0 and V2 as 1,
    and the weight of the edges as the ranks.
        >>> G = nx.Graph()
        >>> G.add_nodes_from(['a1', 'a2'], bipartite=0)
        >>> G.add_nodes_from(['p1', 'p2'], bipartite=1)
        >>> G.add_weighted_edges_from([('a1', 'p1', 2), ('a1', 'p2', 1), ('a2', 'p2', 2)])
        >>> M = rank_maximal_matching(G, rank="weight",top_nodes=['a1', 'a2'])
        >>> print(M)
        {'a1': 'p2', 'p2': 'a1'}
        >>> M['a1']
        'p2'

    explanation:                            2
                    G =             a1-----------p1
                                     \
                                      \
                                       \
                                        \
                                         \\ 1
                                          \
                                           \
                                            \
                                       2     \
                                a2-----------p2
     The matching M1 is {'a1':'p2', 'p2':'a1'} so O1, EV1 and U1 are  {a1,p2},{a2,p1},{} respectively.
     After removing the edges incident to O1 with the rank higher than 1 {(a1,p1),(a2,p2)} there are no more edges
     to add to G1, so an augmenting path doesn't exist and the algorithm ends returning M1.

    another example:
        >>> G = nx.Graph()
        >>> G.add_nodes_from(["a1", "a2"])
        >>> G.add_nodes_from(["p1", "p2"])
        >>> G.add_weighted_edges_from([("a1", "p2", 1), ("a1", "p1", 1), ("a2", "p2", 2)])
        >>> M = rank_maximal_matching(G, rank="weight", top_nodes=["a1", "a2"])
        >>> print(M=={"a1": "p1", "a2": "p2", "p1": "a1", "p2": "a2"})
        True
        >>> M['a1']
        'p1'

    Raises
    ------
    AmbiguousSolution
      Raised if the input bipartite graph is disconnected and no container
      with all nodes in one bipartite set is provided. When determining
      the nodes in each bipartite set more than one valid solution is
      possible if the input graph is disconnected.

    Notes
    -----
    This function uses the algorithm published in the article of Irving et al. (2006), "Rank maximal matching".
    See :mod:`bipartite documentation <networkx.algorithms.bipartite>`
    for further details on how bipartite graphs are handled in NetworkX.

    See Also
    --------
    maximum_matching
    hopcroft_karp_matching

    References
    ----------
    Irving, Robert W. and Kavitha, Telikepalli and Mehlhorn, Kurt and Michail, Dimitrios and Paluch, Katarzyna E.,
    "Rank-Maximal Matchings",ACM Trans. Algorithms,2006,Association for Computing Machinery**
       https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.92.6742&rep=rep1&type=pdf

    """

    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        return {}
    graph = nx.Graph(G)
    Gi = nx.Graph()
    Gi.add_nodes_from(G.nodes)
    max_rank, min_rank = get_max_and_min_rank(G, rank)
    create_Gi(graph, Gi, min_rank, rank=rank)
    left, right = bipartite_sets(G, top_nodes)
    M = nx.bipartite.hopcroft_karp_matching(Gi, left)
    matching_length = len(M)
    free_nodes = find_free_vertices(Gi, M)
    for i in range(min_rank, max_rank):
        even, odd, unreachable = divide_to_sets(Gi, M.items(), free_nodes)
        remove_edges(graph, odd, unreachable, i, rank=rank)
        create_Gi(graph, Gi, i + 1, rank=rank)
        M = nx.bipartite.hopcroft_karp_matching(Gi, top_nodes=left)
        if matching_length == len(M):
            return M
        matching_length = len(M)
    return M


def get_max_and_min_rank(G, rank="rank"):
    x = {d[rank] for (u, v, d) in G.edges(data=True)}
    return max(x), min(x)


def divide_to_sets(Gi, matched_edges, free_nodes):
    """
    Gi - is a graph with i' ranked edges
    return- EVi - set of even vertices
            Oi  -  set of odd vertices
            Ui  -  set of unreachable vertices
    """
    even = set()
    odd = set()
    unreachable = set(Gi.nodes)
    for u in free_nodes:
        if u not in unreachable:
            continue
        initial_depth = 0
        stack = [(u, iter(Gi[u]), initial_depth)]
        even.add(u)
        unreachable.remove(u)
        while stack:
            parent, children, depth = stack[-1]
            try:
                child = next(children)
                if child in unreachable:
                    if depth % 2 == 0 and (parent, child) not in matched_edges:
                        odd.add(child)
                        unreachable.remove(child)
                        stack.append((child, iter(Gi[child]), depth + 1))
                    elif depth % 2 == 1 and (parent, child) in matched_edges:
                        even.add(child)
                        unreachable.remove(child)
                        stack.append((child, iter(Gi[child]), depth + 1))
            except StopIteration:
                stack.pop()
    return even, odd, unreachable


def find_free_vertices(Gi: nx.Graph, M):
    """
    Gi - is a graph with i' ranked edges
    return - list_of_free_vertices
    """
    free_nodes = list(Gi.nodes)
    for key in M:
        free_nodes.remove(key)
    return free_nodes


def create_Gi(G, Gi, rank_i, rank="rank"):
    Gi.add_edges_from(
        [(u, v, d) for (u, v, d) in G.edges(data=True) if d[rank] == rank_i]
    )


def remove_edges(G, Oi, Ui, rank_i, rank="rank"):
    """
    remove edges from Oi or Ui with rank greater than rank_i
    remove OiUi edges
    remove OiOi edges
    """
    G.remove_edges_from(
        [
            (u, v)
            for (u, v, d) in G.edges(Oi.union(Ui), data=True)
            if d[rank] > rank_i  # remove rank> rank_i
        ]
    )
    G.remove_edges_from([(u, v) for (u, v) in G.edges(Oi) if v in Ui])  # remove OU
    G.remove_edges_from([(u, v) for (u, v) in G.edges(Oi) if v in Oi])  # remove OO
