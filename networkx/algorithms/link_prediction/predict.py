import networkx as nx
from networkx.exception import *
from networkx.utils.decorators import *
import networkx.algorithms.link_prediction.functions as lpfunc


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def predict_common_neighbors(G):
    """Predict links using common neighbors algorithm."""
    return _predict(G, lpfunc.common_neighbors)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def predict_resource_allocation_index(G):
    """Predict links using resource allocation index (RA) algorithm."""
    return _predict(G, lpfunc.resource_allocation_index)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def predict_cn_soundarajan_hopcroft(G):
    """Predict links using CN algorithm + community information.

    References
    ----------
    Sucheta Soundarajan and John Hopcroft. 2012. Using community
    information to improve the precision of link prediction methods.
    In Proceedings of the 21st international conference companion on
    World Wide Web (WWW '12 Companion). ACM, New York, NY, USA, 607-608.
    DOI=10.1145/2187980.2188150
    http://doi.acm.org/10.1145/2187980.2188150
    """
    return _predict(G, lpfunc.cn_soundarajan_hopcroft)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def predict_ra_index_soundarajan_hopcroft(G):
    """Predict links using RA index algorithm + community information.

    References
    ----------
    Sucheta Soundarajan and John Hopcroft. 2012. Using community
    information to improve the precision of link prediction methods.
    In Proceedings of the 21st international conference companion on
    World Wide Web (WWW '12 Companion). ACM, New York, NY, USA, 607-608.
    DOI=10.1145/2187980.2188150
    http://doi.acm.org/10.1145/2187980.2188150
    """
    return _predict(G, lpfunc.ra_index_soundarajan_hopcroft)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def predict_within_inter_cluster(G, delta=0.001):
    """Predict links using within-inter cluster (WIC) algorithm.

    This function will compute the ratio of W and IC. W and IC are
    defined as the number of within-cluster and inter-cluster common
    neighbors respectively.

    References
    ----------
    Jorge Carlos Valverde-Rebaza and Alneu de Andrade Lopes. 2012.
    Link prediction in complex networks based on cluster information.
    In Proceedings of the 21st Brazilian conference on Advances in
    Artificial Intelligence (SBIA'12), Leliane N. Barros, Marcelo
    Finger, Aurora T. Pozo, Gustavo A. Gimenénez-Lugo, and Marcos
    Castilho (Eds.). Springer-Verlag, Berlin, Heidelberg, 92-101.
    DOI=10.1007/978-3-642-34459-6_10
    http://dx.doi.org/10.1007/978-3-642-34459-6_10
    """
    if delta <= 0:
        raise NetworkXAlgorithmError()

    def func(G, u, v):
        return lpfunc.within_inter_cluster(G, u, v, delta)
    return _predict(G, func)


def _predict(G, function):
    """Helper function to predict links."""
    non_existent_edge = set()
    for u in G.nodes_iter():
        for v in nx.non_neighbors(G, u):
            if (u, v) not in non_existent_edge:
                non_existent_edge.add((u, v))
                non_existent_edge.add((v, u))
                p = function(G, u, v)
                yield (u, v, p)
