import networkx as nx
import pprint
import graphs as g


def generate_node_pairs():
    lttr_comb = []
    for a in range(1, 25):
        for b in range(2, 25):
            if b > a:
                lttr_comb.append(["{}".format(a), "{}".format(b)])
    return lttr_comb


def generate_node_pairs_triples():
    lttr_comb = []
    for a in range(1, 25):
        for b in range(2, 25):
            if b > a:
                for c in range(3,25):
                    if c > b:
                        lttr_comb.append(["{}".format(a), "{}".format(b), "{}".format(c)])
    return lttr_comb


def sort_dict(dictionary):
    return dict(sorted(dictionary.items(), key=lambda item: item[1]))


def scores_to_dict(lttr_comb, grp_btwn_cntr_all_pairs):
    dictionary = {}
    for l_comb, grp_btwn in zip(lttr_comb, grp_btwn_cntr_all_pairs):
        dictionary["{}".format(l_comb)] = grp_btwn
    return dictionary

def print_sanity():
    print("\n-----------------------------------------\n")


if __name__ == '__main__':
    G = g.strike_group_social()

    btwn_centr = nx.algorithms.betweenness_centrality(G, normalized=False)
    btwn_centr_sorted = sort_dict(btwn_centr)
    pprint.pprint(btwn_centr_sorted, sort_dicts=False)

    print_sanity()

    lttr_comb = generate_node_pairs()
    grp_btwn_cntr_all_pairs = nx.algorithms.group_betweenness_centrality(G, lttr_comb, normalized=False)

    grp_btwn_dict = scores_to_dict(lttr_comb, grp_btwn_cntr_all_pairs)
    grp_btwn_sorted = sort_dict(grp_btwn_dict)
    pprint.pprint(grp_btwn_sorted, sort_dicts=False)

    print_sanity()

    lttr_comb2 = generate_node_pairs_triples()
    grp_btwn_cntr_all_pairs2 = nx.algorithms.group_betweenness_centrality(G, lttr_comb2, normalized=False)

    grp_btwn_dict2 = scores_to_dict(lttr_comb2, grp_btwn_cntr_all_pairs2)
    grp_btwn_sorted2 = sort_dict(grp_btwn_dict2)
    pprint.pprint(grp_btwn_sorted2, sort_dicts=False)

    print_sanity()
