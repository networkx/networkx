"""
=======================
Distance-regular graphs
=======================
"""
#    Copyright (C) 2011 by 
#    Dheeraj M R <dheerajrav@gmail.com>
#    Aric Hagberg <aric.hagberg@gmail.com>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Dheeraj M R <dheerajrav@gmail.com>',
                            'Aric Hagberg <aric.hagberg@gmail.com>'])

__all__ = ['is_distance_regular','intersection_array','global_parameters']

def is_distance_regular(G):
    """Returns True if the graph is distance regular, False otherwise.

    A connected graph G is distance-regular if for any nodes x,y
    and any integers i,j=0,1,...,d (where d is the graph
    diameter), the number of vertices at distance i from x and
    distance j from y depends only on i,j and the graph distance
    between x and y, independently of the choice of x and y.

    Parameters
    ----------
    G: Networkx graph (undirected)

    Returns
    -------
    b,c: tuple of lists 

    Examples
    --------
    >>> nx.intersection_array(nx.hypercube_graph(6))
    ([6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6])
    """
    try:
        a=intersection_array(G)
        return True
    except nx.NetworkXError:
        return False

def global_parameters(ba,ca):
    """Return global parameters for a given intersection array.

    Parameters
    ----------
    b,c: tuple of lists 

    Returns
    -------
    p : list of three-tuples

    Examples
    --------

    References
    ----------
    .. [1] Weisstein, Eric W. "Global Parameters." 
       From MathWorld--A Wolfram Web Resource. 
       http://mathworld.wolfram.com/GlobalParameters.html 

    See Also
    --------
    intersection_array 
    """
    d=len(ba)
    ba.append(0)
    ca.insert(0,0)
    k = ba[0]
    aa = [k-x-y for x,y in zip(ba,ca)]
    return zip(*[ca,aa,ba])


def intersection_array(G):
    """Returns the intersection array of a distance-regular graph.

    Parameters
    ----------
    G: Networkx graph (undirected)

    Returns
    -------
    b,c: tuple of lists 

    Examples
    --------
    >>> nx.is_distance_regular(nx.hypercube_graph(6))
    True

    References
    ----------
    .. [1] Brouwer, A. E.; Cohen, A. M.; and Neumaier, A. 
        Distance-Regular Graphs. New York: Springer-Verlag, 1989.
    .. [2] Weisstein, Eric W. "Distance-Regular Graph." 
        http://mathworld.wolfram.com/Distance-RegularGraph.html

    See Also
    --------
    intersection_array, global_parameters
    """
    if G.is_multigraph() or G.is_directed():
        raise nx.NetworkxException('Not implemented for directed ',
                                   'or multiedge graphs.')
    # test for regular graph (all degrees must be equal)
    degree = G.degree_iter()
    (_,k) = next(degree)
    for _,knext in degree:
        if knext != k:
            raise nx.NetworkXError('Graph is not distance regular.')
        k = knext
    path_length = nx.all_pairs_shortest_path_length(G)  
    diameter = max([max(path_length[n].values()) for n in path_length])
    bint = {} # 'b' intersection array
    cint = {} # 'c' intersection array
    for u in G:
	for v in G:
            try:
                i = path_length[u][v]
            except KeyError:  # graph must be connected
                raise nx.NetworkXError('Graph is not distance regular.')
            # number of neighbors of v at a distance of i-1 from u
            c = len([n for n in G[v] if path_length[n][u]==i-1])
            # number of neighbors of v at a distance of i+1 from u
            b = len([n for n in G[v] if path_length[n][u]==i+1])
            # b,c are independent of u and v
            if cint.get(i,c) != c or bint.get(i,b) != b:
                raise nx.NetworkXError('Graph is not distance regular')
            bint[i] = b 
            cint[i] = c 
    return ([bint.get(i,0) for i in range(diameter)],
            [cint.get(i+1,0) for i in range(diameter)])


    
    
