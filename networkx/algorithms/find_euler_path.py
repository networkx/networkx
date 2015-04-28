import networkx as nx

""" 
Find an eulerian path
"""
#    Copyright (C) 2015 by
#    Edwardo S. Rivera <edwardo.rivera@upr.edu>
#    All rights reserved.
#    BSD license. 



__author__ = """\n""".join(['Edwardo Rivera <edwardo.rivera@urp.edu>'])

__all__ = ['find_eulerian_path'] 

def find_eulerian_path(G):
    """Returns the edges of an Eulerian path in G, (if it exits).

    An Eulerian path is a path that crosses every edge in G
    exactly once.

    Parameters
    ----------
    G: NetworkX Graph, DiGraph, MultiGraph or MultiDiGraph 
        A directed or undirected Graph or MultiGraph.

    Returns
    -------
    edges: generator
        A generator that produces edges in the Eulerian path.

    Raises
    ------
    NetworkXError: If the graph does not have an eulerian path.

    Notes
    -----
    Linear time algorithm, adapted from [1]_ and [3]_.
    Information about euler paths in [2]_.
    Code for eulerian circuit in [3]_.

    Important: In [1], euler path is in reverse order,
    this implementation gives the path in correct order
    as in [3]_ for eulerian_circuit. The distinction for 
    directed graph is in using the in_degree neighbors, not the out
    ones. for undirected, it is using itemgetter(1) for get_vertex, 
    which uses the correct vertex for this order. Also, every graph
    has an even number of odd vertices by the Handshaking Theorem [4]_. 

    References
    ----------
    .. [1] http://www.graph-magics.com/articles/euler.php
    .. [2] http://en.wikipedia.org/wiki/Eulerian_path
    .. [3] https://github.com/networkx/networkx/blob/master/networkx/algorithms/euler.py
    .. [4] https://www.math.ku.edu/~jmartin/courses/math105-F11/Lectures/chapter5-part2.pdf
    
    Examples 
    --------
    >>> G = nx.Graph([('W', 'N'), ('N', 'E'), ('E', 'W'), ('W', 'S'), ('S', 'E')])
    >>> list(nx.find_eulerian_path(G))
    [('W', 'N'), ('N', 'E'), ('E', 'W'), ('W', 'S'), ('S', 'E')]

    >>> G = nx.Digraph([(1, 2), (2, 3)])
    >>> list(nx.find_eulerian_path(G))
    [(1,2),(2,3)]
    """
    from operator import itemgetter 

    # Verify that graph is connected, short circuit
    if G.is_directed() and not nx.is_weakly_connected(G):
        raise nx.NetworkXError("G is not connected.")    

    # is undirected
    if not G.is_directed() and not nx.is_connected(G):
        raise nx.NetworkXError("G is not connected.")

    # Now verify if has an eulerian circuit: even condition of all nodes is satified.
    if nx.is_eulerian(G):
        x = nx.eulerian_circuit(G) # generator of edges
        for i in x:
            yield i
        
    # Not all vertex have even degree, check if exactly two vertex have odd degrees.
    # If yes, then there is an Euler path. If not, raise an error (no euler path can be found)
    else:
        g = G.__class__(G)  # copy graph structure (not attributes)
        
        # list to check the odd degree condition, and a flag
        check_odd = []
        directed = False
    
        if g.is_directed():
            degree = g.in_degree
            out_degree = g.out_degree
            edges = g.in_edges_iter
            get_vertex = itemgetter(0)
            directed = True
        else:
            degree = g.degree
            edges = g.edges_iter
            get_vertex = itemgetter(1)
            
        # Verify if an euler path can be found. Complexity O(n) ?
        for vertex in g.nodes():
            deg = degree(vertex)
            # directed case
            if directed:
                outdeg = out_degree(vertex)
                if deg != outdeg:
                    # if we have more than 2 odd nodes, we do a raise (no euler path)
                    if len(check_odd) > 2:
                        raise nx.NetworkXError("G doesn't have an Euler Path.")
                # is odd and we append it. 
                    else:
                        check_odd.append(vertex)
            # undirected case        
            else:
                if deg % 2 != 0:
                    # if we have more than 2 odd nodes, we do a raise (no euler path)
                    if len(check_odd) > 2:
                        raise nx.NetworkXError("G doesn't have an Euler Path.")
                    # is odd and we append it. 
                    else:
                        check_odd.append(vertex)

        if directed:
            def verify_odd_cond(g,check_odd):
                first = check_odd[0]
                second = check_odd[1]
                if  g.out_degree(first) == g.in_degree(first) + 1 and g.in_degree(second) == g.out_degree(second) + 1:
                    return second
                elif g.out_degree(second) == g.in_degree(second) + 1 and g.in_degree(first)  == g.out_degree(first) + 1:
                    return first
                else:
                    return None
            start = verify_odd_cond(g,check_odd)
        else:
            start = check_odd[0]

        # if the odd condition is not meet, raise an error.
        if not start:
            raise nx.NetworkXError("G doesn't have an Euler Path")
        # Begin algorithm: 
        vertex_stack = [start]
        last_vertex = None

        while vertex_stack:

            current_vertex = vertex_stack[-1] #(4)
            # if no neighbors:
            if degree(current_vertex) == 0:
                # Special case, we cannot add a None vertex to the path.
                if last_vertex is not None:
                    yield (last_vertex, current_vertex)
                last_vertex = current_vertex
                vertex_stack.pop()
            # we have neighbors, so add the vertex to the stack (2), take any of its neighbors (1)
            # remove the edge between selected neighbor and that vertex,
            # and set that neighbor as the current vertex (4).
            else:
                random_edge = next(edges(current_vertex)) #(1)
                vertex_stack.append(get_vertex(random_edge)) #(2)
                g.remove_edge(*random_edge) #(3)

# tests
if __name__ == "__main__":

    # An example, undirected:
    G = nx.Graph()
    G.add_edge("W","N")
    G.add_edge("N","E")
    G.add_edge("E","S")
    G.add_edge("S","W")
    G.add_edge("W","E")
    x = find_eulerian_path(G)
    nodepath = [u for u, v in x]
    print nodepath

    G = nx.DiGraph([(1,2),(2,3)])
    print list(find_eulerian_path(G))

    # An example, directed:
    G = nx.DiGraph()
    G.add_edge("W","N")
    G.add_edge("N","E")
    G.add_edge("S","E")
    G.add_edge("W","S")
    G.add_edge("E","W")

    x = find_eulerian_path(G)
    nodepath = [(u,v) for u, v in x]
    print nodepath

     # An example, multidirected:  
    G = nx.MultiGraph()
    G.add_edge("W","N")
    G.add_edge("N","E")
    G.add_edge("E","W")
    G.add_edge("E","W")
    G.add_edge("W","S")
    G.add_edge("S","E")
    G.add_edge("S","E")
    G.add_edge("S","E")

    x = find_eulerian_path(G)
    nodepath = [(u,v) for u, v in x]
    print nodepath

    # An example, multidirected:  
    G = nx.MultiDiGraph()
    G.add_edge("W","N")
    G.add_edge("N","E")
    G.add_edge("S","E")
    G.add_edge("W","S")
    G.add_edge("E","W")
    G.add_edge("E","S")
    G.add_edge("S","E")
    G.add_edge("E","W")

    x = find_eulerian_path(G)
    nodepath = [(u,v) for u, v in x]
    print nodepath
