import networkx as nx
from networkx.algorithms.bipartite.matching import (
    eppstein_matching,
    hopcroft_karp_matching,
    maximum_matching,
    minimum_weight_full_matching,
    to_vertex_cover,
)


def main():
    G = nx.complete_bipartite_graph(3, 2)

    maximum_matching = hopcroft_karp_matching(G)
    X, Y = nx.bipartite.sets(G)
    unmatched_vertices = set(X) - set(maximum_matching)
    print(maximum_matching)
    # print(len(unmatched_vertices)==0)\
    print(unmatched_vertices)
    print(G)


main()
