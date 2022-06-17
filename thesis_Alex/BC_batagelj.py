import networkx as nx
import networkx.algorithms.thesis_Alex.utils.graphs as g

if __name__ == '__main__':
    G_1 = g.g_1()

    btwn_g1 = nx.betweenness_centrality(G_1, xtra_data=True)

    # GBC_G_1_1 = nx.group_betweenness_centrality(G_1, ['3', '7'], normalized=False)
    # print(GBC_G_1_1)
    #
    # GBC_G_1_2 = nx.group_betweenness_centrality(G_1, ['4', '8'], normalized=False)
    # print(GBC_G_1_2)


