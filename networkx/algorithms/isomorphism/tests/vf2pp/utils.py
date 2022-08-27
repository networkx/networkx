import networkx as nx

labels_same = ["blue"]

labels_different = [
    "white",
    "red",
    "blue",
    "green",
    "orange",
    "black",
    "purple",
    "yellow",
    "brown",
    "cyan",
    "solarized",
    "pink",
    "none",
]


def get_labels(G1, G2, has_labels=False):
    if not has_labels:
        G1_labels, G2_labels = {}, {}
        G1_labels.update(G1.nodes(data=None, default=-1))
        G2_labels.update(G2.nodes(data=None, default=-1))
        return G1_labels, G2_labels

    return (
        nx.get_node_attributes(G1, "label"),
        nx.get_node_attributes(G2, "label"),
    )
