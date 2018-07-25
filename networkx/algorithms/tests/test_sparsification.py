import networkx as nx
import random

def test_spanner():
    k = 3

    G = nx.complete_graph(100)
    for u, v in G.edges():
        G[u][v]['weight'] = 200

    spanner = nx.spanner_guarantee(G, k, weight='weight')

    print(G.number_of_edges())
    print(spanner.number_of_edges())

    length_G = dict(nx.shortest_path_length(G, weight='weight'))
    length_spanner = dict(nx.shortest_path_length(spanner, weight='weight'))

    for u in G.nodes():
        for v in G.nodes():
            print(length_G[u][v], length_spanner[u][v])
            assert length_spanner[u][v] <= (2 * k - 1) * length_G[u][v]