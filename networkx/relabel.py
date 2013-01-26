#    Copyright (C) 2006-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult (dschult@colgate.edu)'])
__all__ = ['convert_node_labels_to_integers', 'relabel_nodes']

def relabel_nodes(G, mapping, copy=True):
    """Relabel the nodes of the graph G.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    mapping : dictionary
       A dictionary with the old labels as keys and new labels as values.
       A partial mapping is allowed.

    copy : bool (optional, default=True)
       If True return a copy, or if False relabel the nodes in place.

    Examples
    --------
    >>> G=nx.path_graph(3)  # nodes 0-1-2
    >>> mapping={0:'a',1:'b',2:'c'}
    >>> H=nx.relabel_nodes(G,mapping)
    >>> print(sorted(H.nodes()))
    ['a', 'b', 'c']

    >>> G=nx.path_graph(26) # nodes 0..25
    >>> mapping=dict(zip(G.nodes(),"abcdefghijklmnopqrstuvwxyz"))
    >>> H=nx.relabel_nodes(G,mapping) # nodes a..z
    >>> mapping=dict(zip(G.nodes(),range(1,27)))
    >>> G1=nx.relabel_nodes(G,mapping) # nodes 1..26

    Partial in-place mapping:

    >>> G=nx.path_graph(3)  # nodes 0-1-2
    >>> mapping={0:'a',1:'b'} # 0->'a' and 1->'b'
    >>> G=nx.relabel_nodes(G,mapping, copy=False)

    print(G.nodes())
    [2, 'b', 'a']

    Mapping as function:

    >>> G=nx.path_graph(3)
    >>> def mapping(x):
    ...    return x**2
    >>> H=nx.relabel_nodes(G,mapping)
    >>> print(H.nodes())
    [0, 1, 4]

    Notes
    -----
    Only the nodes specified in the mapping will be relabeled.

    The keyword setting copy=False modifies the graph in place.
    This is not always possible if the mapping is circular.
    In that case use copy=True.

    See Also
    --------
    convert_node_labels_to_integers
    """
    # you can pass a function f(old_label)->new_label
    # but we'll just make a dictionary here regardless
    if not hasattr(mapping,"__getitem__"):
        m = dict((n,mapping(n)) for n in G)
    else:
        m=mapping
    if copy:
        return _relabel_copy(G,m)
    else:
        return _relabel_inplace(G,m)


def _relabel_inplace(G, mapping):
    old_labels=set(mapping.keys())
    new_labels=set(mapping.values())
    if len(old_labels & new_labels) > 0:
        # labels sets overlap
        # can we topological sort and still do the relabeling?
        D=nx.DiGraph(list(mapping.items()))
        D.remove_edges_from(D.selfloop_edges())
        try:
            nodes=nx.topological_sort(D)
        except nx.NetworkXUnfeasible:
            raise nx.NetworkXUnfeasible('The node label sets are overlapping '
                                        'and no ordering can resolve the '
                                        'mapping. Use copy=True.')
        nodes.reverse()  # reverse topological order
    else:
        # non-overlapping label sets
        nodes=old_labels

    multigraph = G.is_multigraph()
    directed = G.is_directed()

    for old in nodes:
        try:
            new=mapping[old]
        except KeyError:
            continue
        try:
            G.add_node(new,attr_dict=G.node[old])
        except KeyError:
            raise KeyError("Node %s is not in the graph"%old)
        if multigraph:
            new_edges=[(new,old == target and new or target,key,data)
                       for (_,target,key,data)
                       in G.edges(old,data=True,keys=True)]
            if directed:
                new_edges+=[(old == source and new or source,new,key,data)
                            for (source,_,key,data)
                            in G.in_edges(old,data=True,keys=True)]
        else:
            new_edges=[(new,old == target and new or target,data)
                       for (_,target,data) in G.edges(old,data=True)]
            if directed:
                new_edges+=[(old == source and new or source,new,data)
                            for (source,_,data) in G.in_edges(old,data=True)]
        G.remove_node(old)
        G.add_edges_from(new_edges)
    return G

def _relabel_copy(G, mapping):
    H=G.__class__()
    H.name="(%s)" % G.name
    if G.is_multigraph():
        H.add_edges_from( (mapping.get(n1,n1),mapping.get(n2,n2),k,d.copy())
                          for (n1,n2,k,d) in G.edges_iter(keys=True,data=True))
    else:
        H.add_edges_from( (mapping.get(n1,n1),mapping.get(n2,n2),d.copy())
                          for (n1,n2,d) in G.edges_iter(data=True))

    H.add_nodes_from(mapping.get(n,n) for n in G)
    H.node.update(dict((mapping.get(n,n),d.copy()) for n,d in G.node.items()))
    H.graph.update(G.graph.copy())

    return H


def convert_node_labels_to_integers(G, first_label=0, ordering="default",
                                    label_attribute=None):
    """Return a copy of the graph G with the nodes relabeled with integers.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    first_label : int, optional (default=0)
       An integer specifying the offset in numbering nodes.
       The n new integer labels are numbered first_label, ..., n-1+first_label.

    ordering : string
       "default" : inherit node ordering from G.nodes()
       "sorted"  : inherit node ordering from sorted(G.nodes())
       "increasing degree" : nodes are sorted by increasing degree
       "decreasing degree" : nodes are sorted by decreasing degree

    label_attribute : string, optional (default=None)
       Name of node attribute to store old label.  If None no attribute
       is created.

    Notes
    -----
    Node and edge attribute data are copied to the new (relabeled) graph.

    See Also
    --------
    relabel_nodes
    """
    N = G.number_of_nodes()+first_label
    if ordering == "default":
        mapping = dict(zip(G.nodes(),range(first_label,N)))
    elif ordering == "sorted":
        nlist = G.nodes()
        nlist.sort()
        mapping=dict(zip(nlist,range(first_label,N)))
    elif ordering == "increasing degree":
        dv_pairs=[(d,n) for (n,d) in G.degree_iter()]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        mapping = dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    elif ordering == "decreasing degree":
        dv_pairs = [(d,n) for (n,d) in G.degree_iter()]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        dv_pairs.reverse()
        mapping = dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    else:
        raise nx.NetworkXError('Unknown node ordering: %s'%ordering)
    H = relabel_nodes(G,mapping)
    H.name="("+G.name+")_with_int_labels"
    # create node attribute with the old label
    if label_attribute is not None:
        nx.set_node_attributes(H, label_attribute,
                               dict((v,k) for k,v in mapping.items()))
    return H
