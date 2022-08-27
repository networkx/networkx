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


def compute_Ti(G1, G2, mapping, reverse_mapping):
    T1 = {nbr for node in mapping for nbr in G1[node] if nbr not in mapping}
    T2 = {
        nbr
        for node in reverse_mapping
        for nbr in G2[node]
        if nbr not in reverse_mapping
    }
    T1_out = {n1 for n1 in G1.nodes() if n1 not in mapping and n1 not in T1}
    T2_out = {n2 for n2 in G2.nodes() if n2 not in reverse_mapping and n2 not in T2}

    return T1, T2, T1_out, T2_out


def assign_labels(G1, G2, mapped=None, same=False):
    if same:
        for i, n in enumerate(G1.nodes()):
            G1.nodes[n]["label"] = "blue"
            if not (mapped is None):
                n = mapped[n]
            G2.nodes[n]["label"] = "blue"
        return

    labels = [
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
    for i, n in enumerate(G1.nodes()):
        G1.nodes[n]["label"] = labels[i % len(labels)]
        if not (mapped is None):
            n = mapped[n]
        G2.nodes[n]["label"] = labels[i % len(labels)]


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
