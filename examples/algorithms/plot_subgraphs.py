"""
=========
Subgraphs
=========
Example of partitioning a directed graph with nodes labeled as
supported and unsupported nodes into a list of subgraphs
that contain only entirely supported or entirely unsupported nodes.
Adopted from 
https://github.com/lobpcg/python_examples/blob/master/networkx_example.py
"""

import networkx as nx
import matplotlib.pyplot as plt


def graph_partitioning(G, plotting=True):
    """Partition a directed graph into a list of subgraphs that contain
    only entirely supported or entirely unsupported nodes.
    """
    # Determine indexes of all supported and unsupported nodes.
    node_supported_index = []
    node_unsupported_index = []
    for v in G.nodes(data=True):
        if v[1]["node_type"] == "supported":
            node_supported_index.append(v[0])
        if v[1]["node_type"] == "unsupported":
            node_unsupported_index.append(v[0])

    # Make a copy of the graph.
    H = G.copy()
    # Remove all edges connecting supported and unsupported nodes.
    H.remove_edges_from(
        (n, nbr, d)
        for n, nbrs in G.adj.items()
        if n in node_supported_index
        for nbr, d in nbrs.items()
        if nbr in node_unsupported_index
    )
    H.remove_edges_from(
        (n, nbr, d)
        for n, nbrs in G.adj.items()
        if n in node_unsupported_index
        for nbr, d in nbrs.items()
        if nbr in node_supported_index
    )
    H.graph.update(G.graph)

    G_minus_H = nx.DiGraph()
    # Collect all removed edges for reconstruction.
    G_minus_H.add_edges_from(
        (n, nbr, d)
        for n, nbrs in G.adj.items()
        if n in node_supported_index
        for nbr, d in nbrs.items()
        if nbr in node_unsupported_index
    )
    G_minus_H.add_edges_from(
        (n, nbr, d)
        for n, nbrs in G.adj.items()
        if n in node_unsupported_index
        for nbr, d in nbrs.items()
        if nbr in node_supported_index
    )
    G_minus_H.graph.update(G.graph)

    if plotting:
        # Plot the stripped graph with the edges removed.
        _node_color_list = [v[1]["node_color"] for v in H.nodes(data=True)]
        _pos = nx.spring_layout(H)
        plt.figure(figsize=(8, 8))
        nx.draw_networkx_edges(H, _pos, alpha=0.3, edge_color="k")
        nx.draw_networkx_nodes(H, _pos, node_color=_node_color_list)
        nx.draw_networkx_labels(H, _pos, font_size=14)
        plt.axis("off")
        plt.title("The stripped graph with the edges removed.")
        plt.show()
        # Plot the the edges removed.
        _pos = nx.spring_layout(G_minus_H)
        plt.figure(figsize=(8, 8))
        nx.draw_networkx_edges(G_minus_H, _pos, alpha=0.3, edge_color="k")
        Gn = G.nodes(data=True)
        Gmn = G_minus_H.nodes(data=True)
        nd = {v: dict(Gn[v]) for v in dict(Gn) if v in dict(Gmn)}
        ncl = [nd[v]["node_color"] for v in nd]
        nx.draw_networkx_nodes(G_minus_H, _pos, node_color=ncl)
        nx.draw_networkx_labels(G_minus_H, _pos, font_size=14)
        plt.axis("off")
        plt.title("The edges removed.")
        plt.show()

    # Find the connected componets in the stripped undirected graph.
    # And use the sets, specifying the components, to partition
    # the original directed graph into a list of directed subgraphs
    # that contain only entirely supported or entirely unsupported nodes.
    # Plot the resulting subgraphs.
    subgraphs = []
    for c in nx.connected_components(H.to_undirected()):
        H_c = H.subgraph(c).copy()
        subgraphs.append(H_c)
        if plotting:
            _pos = nx.spring_layout(H_c)
            plt.figure(figsize=(8, 8))
            nx.draw_networkx_edges(H_c, _pos, alpha=0.3, edge_color="k")
            _node_color_list_c = [v[1]["node_color"] for v in H_c.nodes(data=True)]
            nx.draw_networkx_nodes(H_c, _pos, node_color=_node_color_list_c)
            nx.draw_networkx_labels(H_c, _pos, font_size=14)
            plt.axis("off")
            plt.title("One of the subgraphs.")
            plt.show()

    return subgraphs, G_minus_H


###############################################################################
# Create an example directed graph.
# ---------------------------------
#
# This directed graph has one input node labeled `in` and plotted in blue color
# and one output node labeled `out` and plotted in magenta color.
# The other six nodes are classified as four `supported` plotted in green color
# and two `unsupported` plotted in red color. The goal is computing a list
# of subgraphs that contain only entirely `supported` or `unsupported` nodes.
G_ex = nx.DiGraph()
G_ex.add_nodes_from(["In"], node_type="input", node_color="b")
G_ex.add_nodes_from(["A", "C", "E", "F"], node_type="supported", node_color="g")
G_ex.add_nodes_from(["B", "D"], node_type="unsupported", node_color="r")
G_ex.add_nodes_from(["Out"], node_type="output", node_color="m")
G_ex.add_edges_from(
    [
        ("In", "A"),
        ("A", "B"),
        ("B", "C"),
        ("B", "D"),
        ("D", "E"),
        ("C", "F"),
        ("E", "F"),
        ("F", "Out"),
    ]
)

###############################################################################
# Plot the original graph.
# ------------------------
#
node_color_list = [v[1]["node_color"] for v in G_ex.nodes(data=True)]
pos = nx.spectral_layout(G_ex)
plt.figure(figsize=(8, 8))
nx.draw_networkx_edges(G_ex, pos, alpha=0.3, edge_color="k")
nx.draw_networkx_nodes(G_ex, pos, alpha=0.8, node_color=node_color_list)
nx.draw_networkx_labels(G_ex, pos, font_size=14)
plt.axis("off")
plt.title("The original graph.")
plt.show()

###############################################################################
# Calculate the subgraphs with plotting all results of intemediate steps.
# -----------------------------------------------------------------------
#
subgraphs_of_G_ex, removed_edges = graph_partitioning(G_ex, plotting=True)

###############################################################################
# Plot the results: every subgraph in the list.
# ---------------------------------------------
#
for subgraph in subgraphs_of_G_ex:
    _pos = nx.spring_layout(subgraph)
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(subgraph, _pos, alpha=0.3, edge_color="k")
    node_color_list_c = [v[1]["node_color"] for v in subgraph.nodes(data=True)]
    nx.draw_networkx_nodes(subgraph, _pos, node_color=node_color_list_c)
    nx.draw_networkx_labels(subgraph, _pos, font_size=14)
    plt.axis("off")
    plt.title("One of the subgraphs.")
    plt.show()

###############################################################################
# Put the graph back from the list of subgraphs
# ---------------------------------------------
#
G_ex_r = nx.DiGraph()
# Composing all subgraphs.
for subgraph in subgraphs_of_G_ex:
    G_ex_r = nx.compose(G_ex_r, subgraph)
# Adding the previously stored edges.
G_ex_r.add_edges_from(removed_edges.edges())

###############################################################################
# Check that the original graph and the reconstructed graphs are isomorphic.
# --------------------------------------------------------------------------
#
check = nx.is_isomorphic(G_ex, G_ex_r)
print("The reconstruction is", check)

###############################################################################
# Plot the reconstructed graph.
# -----------------------------
#
node_color_list = [v[1]["node_color"] for v in G_ex_r.nodes(data=True)]
pos = nx.spectral_layout(G_ex_r)
plt.figure(figsize=(8, 8))
nx.draw_networkx_edges(G_ex_r, pos, alpha=0.3, edge_color="k")
nx.draw_networkx_nodes(G_ex_r, pos, alpha=0.8, node_color=node_color_list)
nx.draw_networkx_labels(G_ex_r, pos, font_size=14)
plt.axis("off")
plt.title("The reconstructed graph.")
plt.show()


###############################################################################
# A unit test function for graph_partitioning.
# --------------------------------------------
#
def test_graph_partitioning():
    """Unit test for graph partitioning."""
    # Unit test example generator.
    G_u = nx.DiGraph()
    G_u.add_nodes_from(["In"], node_type="input", node_color="b")
    G_u.add_nodes_from(["A"], node_type="supported", node_color="g")
    G_u.add_nodes_from(["B", "D"], node_type="unsupported", node_color="r")
    G_u.add_nodes_from(["Out"], node_type="output", node_color="m")
    G_u.add_edges_from([("In", "A"), ("A", "B"), ("B", "D"), ("D", "Out")])

    G_us = nx.DiGraph()
    G_us.add_nodes_from(["In"], node_type="input", node_color="b")
    G_us.add_nodes_from(["A"], node_type="supported", node_color="g")
    G_us.add_edges_from([("In", "A")])

    G_uu = nx.DiGraph()
    G_uu.add_nodes_from(["B", "D"], node_type="unsupported", node_color="r")
    G_uu.add_nodes_from(["Out"], node_type="output", node_color="m")
    G_uu.add_edges_from([("B", "D"), ("D", "Out")])

    subgraphs_of_G_u_true = [G_us, G_uu]

    subgraphs_of_G_u, _removed_edges = graph_partitioning(G_u, plotting=False)

    _check = nx.is_isomorphic(
        subgraphs_of_G_u[0], subgraphs_of_G_u_true[0]
    ) and nx.is_isomorphic(subgraphs_of_G_u[1], subgraphs_of_G_u_true[1])

    # Putting the graph back from the list of subgraphs
    G_u_r = nx.DiGraph()
    # Composing all subgraphs.
    for _subgraph in subgraphs_of_G_u:
        G_u_r = nx.compose(G_u_r, _subgraph)
    # Adding the previously stored edges.
    G_u_r.add_edges_from(_removed_edges.edges())

    _check = _check and nx.is_isomorphic(G_u, G_u_r)

    assert _check


###############################################################################
# Run the unit test function for graph_partitioning.
# --------------------------------------------------
#
test_graph_partitioning()
