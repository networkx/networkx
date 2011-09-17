# Cuthill McKee ordering of matrices
# Copyright (C) 2011 by 
# Aric Hagberg <aric.hagberg@gmail.com>
# BSD License
from operator import itemgetter
import networkx as nx
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)'])
__all__ = ['cuthill_mckee_ordering',
           'reverse_cuthill_mckee_ordering']

def cuthill_mckee_ordering(G, start=None):
    for g in nx.connected_component_subgraphs(G):
        for n in connected_cuthill_mckee_ordering(g, start):
            yield n

def reverse_cuthill_mckee_ordering(G, start=None):
    return reversed(list(cuthill_mckee_ordering(G, start=start)))

def connected_cuthill_mckee_ordering(G, start=None):
    if start is None:
        (_, start) = find_pseudo_peripheral_node_pair(G)
    yield start
    visited = set([start])
    stack = [(start, iter(G[start]))]
    while stack:
        parent,children = stack[0]
        if parent not in visited:
            yield parent
        try:
            child = next(children)
            if child not in visited:
                yield child
                visited.add(child)
                # add children to stack, sorted by degree (lowest first)
                nd = sorted(G.degree(G[child]).items(), key=itemgetter(1))
                children = (n for n,d in nd)
                stack.append((child,children))
        except StopIteration:
            stack.pop(0)

def find_pseudo_peripheral_node_pair(G, start=None):
    if start is None:
        u = next(G.nodes_iter())
    else:
        u = start
    lp = 0
    v = u 
    while True:
        spl = nx.shortest_path_length(G, v)
        l = max(spl.values())
        if l <= lp: 
            break
        lp = l
        farthest = [n for n,dist in spl.items() if dist==l]
        v, deg = sorted(G.degree(farthest).items(), key=itemgetter(1))[0]
    return u, v
    
if __name__=='__main__':
    import networkx as nx
    # example from 
    # http://www.boost.org/doc/libs/1_37_0/libs/graph/example/cuthill_mckee_ordering.cpp
    G = nx.Graph([(0,3),(0,5),(1,2),(1,4),(1,6),(1,9),(2,3),
            (2,4),(3,5),(3,8),(4,6),(5,6),(5,7),(6,7)])
    rcm = list(reverse_cuthill_mckee_ordering(G,start=0))    
    assert(rcm==[9, 1, 4, 6, 7, 2, 8, 5, 3, 0])
    rcm = list(reverse_cuthill_mckee_ordering(G))    
    assert(rcm==[0, 8, 5, 7, 3, 6, 4, 2, 1, 9])
    print "ordering",rcm
    # build low-bandwidth numpy matrix
    try:
        import numpy as np
        print "matrix"
        A = nx.to_numpy_matrix(G)
        print A
        x,y = np.nonzero(A)
        print("bandwidth:",np.abs(x-y).max())
        B = nx.to_numpy_matrix(G,nodelist=rcm)
        print("low-bandwidth matrix")
        print B
        x,y = np.nonzero(B)
        print("bandwidth:",np.abs(x-y).max())
    except:
        pass
