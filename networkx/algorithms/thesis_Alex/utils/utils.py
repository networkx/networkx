import copy

import networkx as nx

__all__ = [
    "compare_kourtellis_bc",
    "compare_kourtellis_D",
    "compare_kourtellis_SP",
    "compare_kourtellis_Delta",
    "compare_kourtellis_no_print",
    "sort_dict",
    "sort_ddict",
    "pretty_print",
]

def compare_kourtellis_bc(G, edge):
    G_new = copy.deepcopy(G)
    G_new.add_edge(edge[0], edge[1])

    bc1 = nx.betweenness_centrality(G, normalized=False)
    print("bc1: {}\n".format(bc1))

    bc2 = nx.betweenness_centrality(G_new, normalized=False)
    print("bc2: {}\n".format(bc2))

    G_dyn, bc3, D, SP, Delta = nx.kourtellis_dynamic_bc(G, edge, "add")
    print("bc3: {}\n\n".format(bc3))


def compare_kourtellis_D(G, edge):
    G_new = copy.deepcopy(G)
    G_new.add_edge(edge[0], edge[1])

    bc1, D1, SP1, Delta1 = nx.betweenness_centrality(G, normalized=False, xtra_data=True)
    print("D1:")
    pretty_print(D1)

    bc2, D2, SP2, Delta2 = nx.betweenness_centrality(G_new, normalized=False, xtra_data=True)
    print("D2:")
    pretty_print(D2)

    G_dyn, bc3, D3, SP3, Delta3 = nx.kourtellis_dynamic_bc(G, edge, "add")
    print("D3:")
    pretty_print(D3)


def compare_kourtellis_SP(G, edge):
    G_new = copy.deepcopy(G)
    G_new.add_edge(edge[0], edge[1])

    bc1, D1, SP1, Delta1 = nx.betweenness_centrality(G, normalized=False, xtra_data=True)
    print("SP1:")
    pretty_print(SP1)

    bc2, D2, SP2, Delta2 = nx.betweenness_centrality(G_new, normalized=False, xtra_data=True)
    print("SP2:")
    pretty_print(SP2)

    G_dyn, bc3, D3, SP3, Delta3 = nx.kourtellis_dynamic_bc(G, edge, "add")
    print("SP3:")
    pretty_print(SP3)


def compare_kourtellis_Delta(G, edge):
    G_new = copy.deepcopy(G)
    G_new.add_edge(edge[0], edge[1])

    bc1, D1, SP1, Delta1 = nx.betweenness_centrality(G, normalized=False, xtra_data=True)
    print("Delta 1:")
    pretty_print(Delta1)

    bc2, D2, SP2, Delta2 = nx.betweenness_centrality(G_new, normalized=False, xtra_data=True)
    print("Delta 2:")
    pretty_print(Delta2)

    G_dyn, bc3, D3, SP3, Delta3 = nx.kourtellis_dynamic_bc(G, edge, "add")
    print("Delta 3:")
    pretty_print(Delta3)


def compare_kourtellis_no_print(G, edge):
    G_new = copy.deepcopy(G)

    bc1 = nx.betweenness_centrality(G, normalized=False)

    bc2 = nx.betweenness_centrality(G_new, normalized=False)

    G_dyn, bc3, D, SP, Delta = nx.kourtellis_dynamic_bc(G, edge, "add")


def sort_dict(dictionary):
    return dict(sorted(dictionary.items(), key=lambda item: item[1]))


def sort_ddict(dict_of_dict):
    return {key: sorted(dict_of_dict[key]) for key in sorted(dict_of_dict)}


def pretty_print(mtrx):
    mtrx_sort = dict(sorted(mtrx.items(), key=lambda item: item[0]))
    for key, values in mtrx_sort.items():
        val_sort = dict(sorted(values.items(), key=lambda item: item[0]))
        print("{}: {}".format(key, val_sort))
    print("------------------------------------------------------------ \n")
