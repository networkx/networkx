"""
Graph products.
"""
#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import is_string_like
from itertools import product
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'
                            'Ben Edwards(bedwards@cs.unm.edu)'])
__all__ = ['cartesian_product', 'tensor_product',
           'lexicographic_product', 'strong_product']

def _dict_product(d1,d2):
    prod_dict = {}
    for k in list(d1.keys()) + list(d2.keys()):
        if k in d1 and k in d2:
            prod_dict[k] = (d1[k],d2[k])
        elif k in d1 and not k in d2:
            prod_dict[k] = (d1[k],None)
        elif not k in d1 and k in d2:
            prod_dict[k] = (None,d2[k])
    return prod_dict


"""A bunch of generators for producting graph products"""
def _node_product(G,H):
    for ((u_G,d_G),(u_H,d_H)) in product(G.nodes_iter(data=True),
                                       H.nodes_iter(data=True)):
        yield ((u_G,u_H),_dict_product(d_G,d_H))
        
def _directed_edges_cross_edges(G,H):
    if not G.is_multigraph() and not H.is_multigraph():
        for (u_G,v_G,d_G) in G.edges_iter(data=True):
            for (u_H,v_H,d_H) in H.edges_iter(data=True):
                yield ((u_G,u_H),(v_G,v_H),_dict_product(d_G,d_H))
    if not G.is_multigraph() and H.is_multigraph():
        for (u_G,v_G,d_G) in G.edges_iter(data=True):
            for (u_H,v_H,k_H,d_H) in H.edges_iter(data=True,keys=True):
                yield ((u_G,u_H),(v_G,v_H),k_H,_dict_product(d_G,d_H))
    if G.is_multigraph() and not H.is_multigraph():
        for (u_G,v_G,k_G,d_G) in G.edges_iter(data=True,keys=True):
            for (u_H,v_H,d_H) in H.edges_iter(data=True):
                yield ((u_G,u_H),(v_G,v_H),k_G,_dict_product(d_G,d_H))
    if G.is_multigraph() and H.is_multigraph():
        for (u_G,v_G,k_G,d_G) in G.edges_iter(data=True,keys=True):
            for (u_H,v_H,k_H,d_H) in H.edges_iter(data=True,keys=True):
                yield ((u_G,u_H),(v_G,v_H),(k_G,k_H),_dict_product(d_G,d_H))

def _undirected_edges_cross_edges(G,H):
    if not G.is_multigraph() and not H.is_multigraph():
        for (u_G,v_G,d_G) in G.edges_iter(data=True):
            for (u_H,v_H,d_H) in H.edges_iter(data=True):
                yield ((v_G,u_H),(u_G,v_H),_dict_product(d_G,d_H))
    if not G.is_multigraph() and H.is_multigraph():
        for (u_G,v_G,d_G) in G.edges_iter(data=True):
            for (u_H,v_H,k_H,d_H) in H.edges_iter(data=True,keys=True):
                yield ((v_G,u_H),(u_G,v_H),k_H,_dict_product(d_G,d_H))
    if G.is_multigraph() and not H.is_multigraph():
        for (u_G,v_G,k_G,d_G) in G.edges_iter(data=True,keys=True):
            for (u_H,v_H,d_H) in H.edges_iter(data=True):
                yield ((v_G,u_H),(u_G,v_H),k_G,_dict_product(d_G,d_H))
    if G.is_multigraph() and H.is_multigraph():
        for (u_G,v_G,k_G,d_G) in G.edges_iter(data=True,keys=True):
            for (u_H,v_H,k_H,d_H) in H.edges_iter(data=True,keys=True):
                yield ((v_G,u_H),(u_G,v_H),(k_G,k_H),_dict_product(d_G,d_H))

def _edges_cross_nodes(G,H):
    if G.is_multigraph():
        for (u_G,v_G,k_G,d_G) in G.edges_iter(data=True,keys=True):
            for x in H.nodes_iter():
                yield ((u_G,x),(v_G,x),k_G,d_G)
    else:
        for (u_G,v_G,d_G) in G.edges_iter(data=True):
            for x in H.nodes_iter():
                if H.is_multigraph():
                    yield ((u_G,x),(v_G,x),None,d_G)
                else:
                    yield ((u_G,x),(v_G),d_G)


def _nodes_cross_edges(G,H):
    if H.is_multigraph():
        for x in G.nodes_iter():
            for (u_H,v_H,k_H,d_H) in H.edges_iter(data=True,keys=True):
                yield ((x,u_H),(x,v_H),k_H,d_H)
    else:
        for x in G.nodes_iter():
            for (u_H,v_H,d_H) in H.edges_iter(data=True):
                if G.is_multigraph():
                    yield ((x,u_H),(x,v_H),None,d_H)
                else:
                    yield ((x,u_H),(x,v_H),d_H)

def _edges_cross_nodes_and_nodes(G,H):
    if G.is_multigraph():
        for (u_G,v_G,k_G,d_G) in G.edges_iter(data=True,keys=True):
            for u_H in H.nodes_iter():
                for v_H in H.nodes_iter():
                    yield ((u_G,u_H),(v_G,v_H),k_G,d_G)
    else:
        for (u_G,v_G,d_G) in G.edges_iter(data=True):
            for u_H in H.nodes_iter():
                for v_H in H.nodes_iter():
                    if H.is_multigraph():
                        yield ((u_G,u_H),(v_G,v_H),None,d_G)
                    else:
                        yield((u_G,u_H),(v_G,v_H),d_G)

def tensor_product(G,H):
    """Return the Tensor product of G and H.

    Sometimes referred to as the Categorical Product. If GH =
    tensor_product(G,H), ((u_G,u_H),(v_G,v_H)) is an edge in GH if and
    only if (u_G,v_G) is in G and (u_H,v_H) is in H.

    Parameters
    ----------
    G,H: graph
     A NetworkX Graph

    Returns
    -------
    GH: NetworkX graph
     The tensor product of G and H. GH will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if both G and H are directed,
     and undirected if G and H are both undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Tested with Graph Class
    This produces nodes which have attributes that have the 'product'
    of the G and H's nodes attributes. For example
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> GH = nx.tensor_product(G,H)
    >>> GH.nodes(data=True)
    [((0,'a'),{'a1':(True,True),'a2':(None,'Spam')})]

    Edge attributs are also copied, as well as Multigraph edge keys.
    """
    if not G.is_directed() == H.is_directed():
        raise nx.NetworkXError("G and H must be both directed or",
                               "both undirected")

    if G.is_directed():
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiDiGraph()
        else:
            GH = nx.DiGraph()
    else:
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiGraph()
        else:
            GH = nx.Graph()

    GH.add_nodes_from(_node_product(G,H))
    
    GH.add_edges_from(_directed_edges_cross_edges(G,H))
    if not GH.is_directed():
        GH.add_edges_from(_undirected_edges_cross_edges(G,H))

    GH.name = "Tensor product("+G.name+","+H.name+")"
    return GH

def cartesian_product(G,H):
    """Return the Cartesian product of G and H.

    If GH = cartesian_product(G,H), ((u_G,u_H),(v_G,v_H)) is an edge
    in GH if and only if (u_G,v_G) is an edge in G and u_H==v_H or
    (u_H,v_H) is an edge in H and u_G==v_G.

    Parameters
    ----------
    G,H: graph
     A NetworkX Graph

    Returns
    -------
    GH: NetworkX graph
     The cartesian product of G and H. GH will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if both G and H are directed,
     and undirected if G and H are both undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Tested with Graph Class
    This produces nodes which have attributes that have the 'product'
    of the G and H's nodes attributes. For example
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> GH = nx.cartesian_product(G,H)
    >>> GH.nodes(data=True)
    [((0,'a'),{'a1':(True,True),'a2':(None,'Spam')})]

    Edge attributs are also copied, as well as Multigraph edge keys.
    """
    if not G.is_directed() == H.is_directed():
        raise nx.NetworkXError("G and H must be both directed or",
                               "both undirected")

    if G.is_directed():
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiDiGraph()
        else:
            GH = nx.DiGraph()
    else:
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiGraph()
        else:
            GH = nx.Graph()

    GH.add_nodes_from(_node_product(G,H))
    
    GH.add_edges_from(_edges_cross_nodes(G,H))

    GH.add_edges_from(_edges_cross_nodes(H,G))

    GH.name = "Cartesian product("+G.name+","+H.name+")"
    return GH

def lexicographic_product(G,H):
    """Return the lexicographic product of G and H.

    If GH = lexicographic_product(G,H), ((u_G,u_H),(v_G,v_H)) is an
    edge in GH if and only if (u_G,v_G) is in G or u_G==v_G and
    (u_H,v_H) is an edge in H.

    Parameters
    ----------
    G,H: graph
     A NetworkX Graph

    Returns
    -------
    GH: NetworkX graph
     The lexicographic product of G and H. GH will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if both G and H are directed,
     and undirected if G and H are both undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Tested with Graph Class
    This produces nodes which have attributes that have the 'product'
    of the G and H's nodes attributes. For example
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> GH = nx.lexicographic_product(G,H)
    >>> GH.nodes(data=True)
    [((0,'a'),{'a1':(True,True),'a2':(None,'Spam')})]

    Edge attributs are also copied, as well as Multigraph edge keys.
    """

    if not G.is_directed() == H.is_directed():
        raise nx.NetworkXError("G and H must be both directed or",
                               "both undirected")

    if G.is_directed():
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiDiGraph()
        else:
            GH = nx.DiGraph()
    else:
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiGraph()
        else:
            GH = nx.Graph()

    GH.add_nodes_from(_node_product(G,H))
    
    # Edges in G regardless of H designation
    GH.add_edges_from(_edges_cross_nodes_and_nodes(G,H))
                
    # For each x in G, only if there is an edge in H
    GH.add_edges_from(_nodes_cross_edges(G,H))
                                            
    GH.name = "Lexographic product("+G.name+","+H.name+")"
    return GH

def strong_product(G,H):
    """Return the strong product of G and H.

    If GH = strong_product(G,H), ((u_G,u_H),(v_G,v_H)) is an edge in
    GH if and only if ((u_G,v_G) is in G and u_H==v_H) or (u_G==v_G
    and (u_H,v_H) is an edge in H) or ((u_G,v_G) is an edge in G and
    (u_H,v_H) is an edge in H).

    Parameters
    ----------
    G,H: graph
     A NetworkX Graph

    Returns
    -------
    GH: NetworkX graph
     The strong product of G and H. GH will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if both G and H are directed,
     and undirected if G and H are both undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.
    Notes
    -----
    Tested with Graph Class
    This produces nodes which have attributes that have the 'product'
    of the G and H's nodes attributes. For example
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> GH = nx.strong_product(G,H)
    >>> GH.nodes(data=True)
    [((0,'a'),{'a1':(True,True),'a2':(None,'Spam')})]

    Edge attributs are also copied, as well as Multigraph edge keys.
    """
    
    if not G.is_directed() == H.is_directed():
        raise nx.NetworkXError("G and H must be both directed or",
                               "both undirected")

    if G.is_directed():
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiDiGraph()
        else:
            GH = nx.DiGraph()
    else:
        if G.is_multigraph() or H.is_multigraph():
            GH = nx.MultiGraph()
        else:
            GH = nx.Graph()

    GH.add_nodes_from(_node_product(G,H))


    GH.add_edges_from(_nodes_cross_edges(G,H))
    GH.add_edges_from(_nodes_cross_edges(H,G))

    GH.add_edges_from(_undirected_edges_cross_edges(G,H))
    GH.add_edges_from(_undirected_edges_cross_edges(H,G))

    if not GH.is_directed():
        GH.add_edges_from(_directed_edges_cross_edges(G,H))

    GH.name = "Strong product("+G.name+","+H.name+")"
    return GH
