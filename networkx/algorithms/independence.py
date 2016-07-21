from networkx.algorithms.clique import enumerate_all_cliques
from networkx.algorithms.operators.unary import complement
from networkx.utils import not_implemented_for

__all__ = ['independence_number_sets']


@not_implemented_for('directed')
def independence_number_and_sets(G, independentsets=None):
    """ Returns the independence number and the independent sets in an undirected graph.

    An independent set is a set of vertices in a graph, no two of which are adjacent. 
    A maximum independent set is an independent set of largest possible size for a given graph G. 
    This size is called the independence number of G.
    
    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    independentsets :	List
                        A list of independent sets each of which is a list of nodes in
                        'G'. If not specified, the list of all independent sets is computed.
    Returns
    -------
    tuple : Containing the independence number (int) and the independent sets, a list each of which of is a 
            list of nodes in 'G'.

    Notes
    -----
    The fact that the cliques of the complement graph of G correspond to the independent sets of the graph G is
    being used for computing the independent sets.

    """
    if independentsets is None:
        independentsets = list(enumerate_all_cliques(complement(G)))

    return max([len(i) for i in independentsets]), independentsets
