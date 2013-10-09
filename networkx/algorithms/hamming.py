# -*- coding: utf-8 -*-
"""
Hamming Distance between two graphs and related comparisons.
"""

__all__ = ['hamming_distance', 'generalized_hamming_distance', '2d_generalized_hamming_distance',
        'diversity']

def hamming_distance(G, H):
    """Return the Hamming distance between two (possibly directed) graphs.

    The Hamming distance is the number of edges contained in one
    but not the other graph.

    Parameters
    ----------
    G, H : NetworkX graph/digraph
       The graphs to be compared

    Returns
    -------
    count : integer
      The hamming distance.
    """
    count = 0
    for e in G.edges_iter():
        if not H.has_edge(*e):
            count+=1
    for e in H.edges_iter():
        if not G.has_edge(*e):
            count+=1
    return count


def generalized_hamming_distance(G, H, no_edge_cost=0.5, default=0):
    """Return the Generalized Hamming distance between two (possibly directed and weighted) graphs.

    The Generalized Hamming distance is the difference in weights between each of the edges contained in two graphs, with a special cost for edges that exist in one of the graphs, but not the other.

    Parameters
    ----------
    G, H : NetworkX graph/digraph (with weighted edges, where the relevant edge attribute is "weight")
       The graphs to be compared

    no_edge_cost : float
    the extra cost that is attributed to comparing an edge that exists in one graph with a missing edge in the other graph.

    Returns
    -------
    count : float
      The generalized hamming distance.
    """

    count=0
    for e in G.edges_iter():
        try:
            if H.has_edge(*e):
                count+= abs(nx.get_edge_attributes(G, 'weight')[e]-nx.get_edge_attributes(H, 'weight')[e])

            else:
                count+= (abs(nx.get_edge_attributes(G, 'weight')[e]) + no_edge_cost)
        except: print '%s does not have a weight!' % str(e)

    #And now for the edges that are in H but not in G:
    for e in H.edges_iter():
        if not G.has_edge(*e):
            try: count+= (abs(nx.get_edge_attributes(H, 'weight')[e]) + no_edge_cost)
            except: print '%s does not have a weight!' % str(e)

    return count

def two_d_generalized_hamming_distance(G, H, no_edge_params=(0, 2)):
    """Return the Two-Dimensional Generalized Hamming distance between two (possibly directed) graphs, where each link has information on two dimensions (interpreted, for example, as mean and variance).

    The Two-Dimensional Generalized Hamming distance is the summation of Euclidean distances between two dimensional weights for each of the edges contained in two graphs, with assumed parameters for edges that do not exist in a graph, in order to compare these non-existing edges with existing ones in the other graph.

    Parameters
    ----------
    G, H : NetworkX graph/digraph (with weighted edges, where the relevant edge attribute is "weight")
       The graphs to be compared

    no_edge_params : tuple of two floats or integers
    the assumed two dimensional parameter that is used to compare a non-existing edge for one graph with an existing one in the other graph.

    Returns
    -------
    count : float
      The generalized hamming distance.
    """

    from numpy import sqrt
    count=0
    for e in G.edges_iter():
        if H.has_edge(*e):
            try: count+= sqrt((nx.get_edge_attributes(G, 'mu')[e]-nx.get_edge_attributes(H, 'mu')[e])**2 + (nx.get_edge_attributes(G, 'sigma')[e]-nx.get_edge_attributes(H, 'sigma')[e])**2)


            except: print '%s does not have a mu or a sigma!' % str(e)
        else:
            try: count+= sqrt((nx.get_edge_attributes(G, 'mu')[e]-no_edge_params[0])**2 + (nx.get_edge_attributes(G, 'sigma')[e]-no_edge_params[1])**2)
            except: print '%s does not have a mu or a sigma!' % str(e)

    #And now for the edges that are in H but not in G:
    for e in H.edges_iter():
        if not G.has_edge(*e):
            try: count+= sqrt((nx.get_edge_attributes(H, 'mu')[e]-no_edge_params[0])**2 + (nx.get_edge_attributes(H, 'sigma')[e]-no_edge_params[1])**2)

            except: print '%s does not have a mu or a sigma!' % str(e)

    return count

# problem with edges not having mu and sigma. Have to attach edges differently!

def diversity(obj_set, distance=two_d_generalized_hamming_distance):
    """Return the Weitzman diversity measure (Weitzman 1992) of a set of objects with a distance function defined over any
    two objects in the set.

    The Diversity of a collection of graphs is calculated and returned, according to the algorithm suggested by Martin Weitzman in 1992.

    Parameters
    ----------
    obj_set : A set containing NetworkX graphs/digraphs or any other objects with a distance metric.
       The set of objects for which the diversity is to be calculated

    distance : a function
    a distance function for any two objects.

    Returns
    -------
    count : float
      The diversity of a collection of objects.
    """

    '''
    This function calculates the Weitzman diversity measure (Weitzman 1992) of a set of objects with a distance function defined over any
    two objects in the set.
    '''
    S=set()
    divers=0
    g=obj_set.pop() #Step1: randomly pick an object from the object set
    S.add(g)
    while obj_set:
        set_distance=min([distance(g, h) for g in S for h in obj_set])
        min_elem=[elem for elem in obj_set if min([distance(elem, g) for g in S])==set_distance].pop()

        S.add(min_elem) #Step2: add closest member of the object set to the set, S
        obj_set.remove(min_elem) #and remove it from the object set
        divers+=set_distance #Step3: increment the diversity by the distance between the set S, and the new member.

    #Normalize the diversity by the number of objects:
        #make a distance matrix where the distances don't have to be recalculated (memoization)
    return float(divers)/len(S)
