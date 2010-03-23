"""
Ego graph.

"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Drew Conway <drew.conway@nyu.edu>',
                            'Aric Hagberg <hagberg@lanl.gov>'])
__all__ = ['ego_graph']

def ego_graph(G,n,center=True):
    """Returns induced subgraph of neighbors centered at node n. 
    
    Parameters
    ----------
    G : graph
      A NetworkX Graph or DiGraph

    n : node 
      A single node 

    center : bool, optional
      If False, do not include center node in graph 

    """
    nodes=set([n])  # add center node
    nodes.update(G.neighbors(n)) # extend with neighbors
    H=G.subgraph(nodes)
    if not center:
        H.remove_node(n)
    return  H
