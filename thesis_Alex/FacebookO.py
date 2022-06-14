import networkx as nx
import utils as ut
import pprint
if __name__ == '__main__':
    G = nx.read_edgelist("C:/Users/alexannf/networkXsource/Datasets/facebook/0.edges")
    print(G.number_of_edges())
    print(G.number_of_nodes())

    btwn = nx.betweenness_centrality(G)
    btwn_sort = ut.sort_dict(btwn)
    pprint.pprint(btwn_sort, sort_dicts=False)

    grp_btwn_max2 = nx.prominent_group(G, 2)
    print(grp_btwn_max2)
    grp_btwn_max3 = nx.prominent_group(G, 3)
    print(grp_btwn_max3)
    grp_btwn_max4 = nx.prominent_group(G, 4)
    print(grp_btwn_max4)
