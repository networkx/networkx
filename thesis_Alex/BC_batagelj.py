import networkx as nx
import graphs as g


def pretty_print(mtrx, name):
    mtrx_sort = dict(sorted(mtrx.items(), key=lambda item: item[0]))

    print("\nThe following is the output for the {} algorithm:".format(name))
    for values in mtrx_sort.values():
        print(dict(sorted(values.items(), key=lambda item: item[0])))
    print("------------------------------------------------------------ \n")


if __name__ == '__main__':
    G_1 = g.g_1()

    btwn_g1 = nx.betweenness_centrality(G_1, xtra_data=True)

    # GBC_G_1_1 = nx.group_betweenness_centrality(G_1, ['3', '7'], normalized=False)
    # print(GBC_G_1_1)
    #
    # GBC_G_1_2 = nx.group_betweenness_centrality(G_1, ['4', '8'], normalized=False)
    # print(GBC_G_1_2)


