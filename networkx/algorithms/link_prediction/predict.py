import itertools as it
import networkx as nx
import networkx.algorithms.link_prediction as lp


def predict_common_neighbors(G):
    """Predict links using common neighbors

    This function will return the number of common neighbors of all
    non-existent edges in the graph. Those values will be returned as
    a dictionary; non-existent edges as keys and the number of common
    neighbors as values.

    """
    return _predict(G, lp.functions.common_neighbors)


def predict_resource_allocation_index(G):
    """Predict links using resource allocation index (RA)

    This function will return the value of RA index of all non-existent
    edges in the graph. Those values will be returned as a dictionary;
    non-existent edges as keys and the number of common neighbors as
    values.

    """
    return _predict(G, lp.functions.resource_allocation_index)


def predict_cn_soundarajan_hopcroft(G):
    """Predict links using CN + community information

    This function will compute the value of CN1 function described in
    Soundarajan, et al (2012) of all pairs of nodes which have no edge
    connecting them.

    """
    return _predict(G, lp.functions.cn_soundarajan_hopcroft)


def predict_ra_index_soundarajan_hopcroft(G):
    """Predict links using RA index + community information

    This function will compute the value of RA1 function described in
    Soundarajan, et al (2012) of all pairs of nodes which have no edge
    connecting them.

    """
    return _predict(G, lp.functions.ra_index_soundarajan_hopcroft)


def _predict(G, function):
    """Helper function to predict links given the proximity function"""
    non_existent_edges = []
    for node in G.nodes():
        non_neighbors = list(nx.non_neighbors(G, node))
        repeated_nodes = it.repeat(node, len(non_neighbors))
        non_existent_edges.extend(zip(repeated_nodes, non_neighbors))
    res = {e: function(G, *e) for e in non_existent_edges}
    return res
