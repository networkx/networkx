import networkx as nx
import random


def test_spanner_unweighted():
    n = 1000
    stretch = 3

    G = nx.complete_graph(n)
    spanner = nx.spanner(G, stretch)

    print(G.number_of_edges())
    print(spanner.number_of_edges())

    length_G = dict(nx.shortest_path_length(G))
    length_spanner = dict(nx.shortest_path_length(spanner))

    for u in G.nodes():
        for v in G.nodes():
            assert length_spanner[u][v] <= stretch * length_G[u][v]


def test_spanner_weighted():
    n = 100
    stretch = 10

    G = nx.complete_graph(n)
    for u, v in G.edges():
        G[u][v]['weight'] = random.random()
    spanner = nx.spanner(G, stretch, weight='weight')

    print(G.number_of_edges())
    print(spanner.number_of_edges())

    length_G = dict(nx.shortest_path_length(G, weight='weight'))
    length_spanner = dict(nx.shortest_path_length(spanner, weight='weight'))

    for u in G.nodes():
        for v in G.nodes():
            if length_spanner[u][v] > stretch * length_G[u][v]:
                print(length_G[u][v], length_spanner[u][v])
            # assert length_spanner[u][v] <= stretch * length_G[u][v]
