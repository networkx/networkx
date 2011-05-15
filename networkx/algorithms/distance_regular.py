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
    bool
      True if the graph is Distance Regular, False otherwise

    Examples
    --------
    >>> G=nx.hypercube_graph(6)
    >>> nx.is_distance_regular(G)
    True
    
    See Also
    --------
    intersection_array, global_parameters

    Notes
    -----
    For undirected and simple graphs only

    References
    ----------
    .. [1] Brouwer, A. E.; Cohen, A. M.; and Neumaier, A. 
        Distance-Regular Graphs. New York: Springer-Verlag, 1989.
    .. [2] Weisstein, Eric W. "Distance-Regular Graph." 
        http://mathworld.wolfram.com/Distance-RegularGraph.html

    """
    try:
        a=intersection_array(G)
        return True
    except nx.NetworkXError:
        return False

def global_parameters(b,c):
    """Return global parameters for a given intersection array.

    Given a distance-regular graph G with integers b_i, c_i,i = 0,....,d
    such that for any 2 vertices x,y in G at a distance i=d(x,y), there
    are exactly c_i neighbors of y at a distance of i-1 from x and b_i
    neighbors of y at a distance of i+1 from x.
    
    Thus, a distance regular graph has the global parameters,
    [[c_0,a_0,b_0],[c_1,a_1,b_1],......,[c_d,a_d,b_d]] for the
    intersection array  [b_0,b_1,.....b_{d-1};c_1,c_2,.....c_d]
    where a_i+b_i+c_i=k , k= degree of every vertex.

    Parameters
    ----------
    b,c: tuple of lists 

    Returns
    -------
    p : list of three-tuples

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> b,c=nx.intersection_array(G)
    >>> list(nx.global_parameters(b,c))
    [(0, 0, 3), (1, 0, 2), (1, 1, 1), (1, 1, 1), (2, 0, 1), (3, 0, 0)]

    References
    ----------
    .. [1] Weisstein, Eric W. "Global Parameters." 
       From MathWorld--A Wolfram Web Resource. 
       http://mathworld.wolfram.com/GlobalParameters.html 

    See Also
    --------
    intersection_array 
    """
    d=len(b)
    ba=b[:]
    ca=c[:]
    ba.append(0)
    ca.insert(0,0)
    k = ba[0]
    aa = [k-x-y for x,y in zip(ba,ca)]
    return zip(*[ca,aa,ba])


def intersection_array(G):
    """Returns the intersection array of a distance-regular graph.

    Given a distance-regular graph G with integers b_i, c_i,i = 0,....,d
    such that for any 2 vertices x,y in G at a distance i=d(x,y), there
    are exactly c_i neighbors of y at a distance of i-1 from x and b_i
    neighbors of y at a distance of i+1 from x.

    A distance regular graph'sintersection array is given by, 
    [b_0,b_1,.....b_{d-1};c_1,c_2,.....c_d]

    Parameters
    ----------
    G: Networkx graph (undirected)

    Returns
    -------
    b,c: tuple of lists 

    Examples
    --------
    >>> G=nx.icosahedral_graph()
    >>> nx.intersection_array(G)
    ([5, 2, 1], [1, 2, 5])

    References
    ----------
    .. [1] Weisstein, Eric W. "Intersection Array." 
       From MathWorld--A Wolfram Web Resource. 
       http://mathworld.wolfram.com/IntersectionArray.html
    

    See Also
    --------
    global_parameters
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


