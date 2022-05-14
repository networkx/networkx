import networkx as nx
import pprint


def add_nodes_edges(G):
    for i in range(ord('A'),ord('M')+1):
        G.add_node(chr(i))

    edge_list = [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','E'), ('C','D'), ('C','E'),
                 ('D', 'E'), ('E','F'), ('F','G'), ('G','H'), ('H','I'), ('I','J'), ('I','K'),
                 ('I','L'), ('J','K'), ('J', 'M'), ('K', 'L'), ('K', 'M'), ('L', 'M')]

    for edge in edge_list:
        G.add_edge(*edge)


def generate_node_pairs():
    lttr_comb = []
    for i in range(ord('A'),ord('M')+1):
        for j in range(ord('B'),ord('M')+1):
            if j > i:
                lttr_comb.append([chr(i),chr(j)])
    return lttr_comb


def print_scores(lttr_comb, grp_btwn_cntr_all_pairs):
    for l_comb, grp_btwn in zip(lttr_comb, grp_btwn_cntr_all_pairs):
        print("The group {} has a group betweenness score of {}".format(l_comb, grp_btwn))


if __name__ == '__main__':
    G = nx.Graph()
    add_nodes_edges(G)

    btwn_centr = nx.algorithms.betweenness_centrality(G, normalized=False)
    pprint.pprint(btwn_centr)

    lttr_comb = generate_node_pairs()
    grp_btwn_cntr_all_pairs = nx.algorithms.group_betweenness_centrality(G, lttr_comb, normalized=False)

    # print_scores(lttr_comb,grp_btwn_cntr_all_pairs)

