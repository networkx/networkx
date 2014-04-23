import itertools as it
import networkx as nx
import networkx.algorithms.link_prediction.functions as lpfunc


def predict_common_neighbors(G):
    """Predict links using common neighbors

    This function will return the number of common neighbors of all
    non-existent edges in the graph. Those values will be returned as
    a dictionary; non-existent edges as keys and the number of common
    neighbors as values.

    """
    return _predict(G, lpfunc.common_neighbors)


def predict_resource_allocation_index(G):
    """Predict links using resource allocation index (RA)

    This function will return the value of RA index of all non-existent
    edges in the graph. Those values will be returned as a dictionary;
    non-existent edges as keys and the number of common neighbors as
    values.

    """
    return _predict(G, lpfunc.resource_allocation_index)


def predict_cn_soundarajan_hopcroft(G):
    """Predict links using CN + community information

    This function will compute the value of CN1 function described in
    Soundarajan, et al (2012) of all pairs of nodes which have no edge
    connecting them.

    """
    return _predict(G, lpfunc.cn_soundarajan_hopcroft)


def predict_ra_index_soundarajan_hopcroft(G):
    """Predict links using RA index + community information

    This function will compute the value of RA1 function described in
    Soundarajan, et al (2012) of all pairs of nodes which have no edge
    connecting them.

    """
    return _predict(G, lpfunc.ra_index_soundarajan_hopcroft)


def _predict(G, function):
    """Helper function to predict links given the proximity function"""
    non_existent_edge = set()
    for u in G.nodes_iter():
        for v in nx.non_neighbors(G, u):
            if (u, v) not in non_existent_edge:
                non_existent_edge.add((u, v))
                non_existent_edge.add((v, u))
                p = function(G, u, v)
                yield (u, v, p)
