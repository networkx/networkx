"""
***************
Graphviz AGraph
***************

Interface to pygraphviz AGraph class.

Examples
--------
>>> G=nx.complete_graph(5)
>>> A=nx.to_agraph(G)
>>> H=nx.from_agraph(A)

See Also
--------
Pygraphviz: http://networkx.lanl.gov/pygraphviz


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__all__ = ['from_agraph', 'to_agraph', 
           'write_dot', 'read_dot', 
           'graphviz_layout',
           'pygraphviz_layout']

import os
import sys
import networkx
from networkx.utils import _get_fh,is_string_like


try:
    from peak.util.imports import lazyModule
except:
    from networkx.util.imports import lazyModule

pygraphviz=lazyModule('pygraphviz')


def from_agraph(A,create_using=None):
    """Return a NetworkX Graph or DiGraph from a PyGraphviz graph.

    Parameters
    ----------
    A : PyGraphviz AGraph
      A graph created with PyGraphviz
      
    create_using : NetworkX graph class instance      
      The output is created using the given graph class instance

    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> A=nx.to_agraph(K5)
    >>> G=nx.from_agraph(A)
    >>> G=nx.from_agraph(A)


    Notes
    -----
    The Graph G will have a dictionary G.graph_attr containing
    the default graphviz attributes for graphs, nodes and edges.

    Default node attributes will be in the dictionary G.node_attr
    which is keyed by node.

    Edge attributes will be returned as edge data in G.  With
    edge_attr=False the edge data will be the Graphviz edge weight
    attribute or the value 1 if no edge weight attribute is found.

    """
    if create_using is None:        
        if A.is_directed():
            if A.is_strict():
                create_using=networkx.DiGraph()
            else:
                create_using=networkx.MultiDiGraph()
        else:
            if A.is_strict():
                create_using=networkx.Graph()
            else:
                create_using=networkx.MultiGraph()

    # assign defaults        
    N=networkx.empty_graph(0,create_using)
    N.name=str(A)
    node_attr={}
    # add nodes, attributes to N.node_attr
    for n in A.nodes():
        N.add_node(str(n),**dict(n.attr))

    # add edges, assign edge data as dictionary of attributes
    for e in A.edges():
        u,v=str(e[0]),str(e[1])
        attr=dict(e.attr)
        if e.key is not None:
            attr.update(key=e.key)
        N.add_edge(u,v,attr)
        
    # add default attributes for graph, nodes, and edges       
    # hang them on N.graph_attr
    N.graph['graph']=A.graph_attr
    N.graph['node']=A.node_attr
    N.graph['edge']=A.edge_attr
    return N        

def to_agraph(N):
    """Return a pygraphviz graph from a NetworkX graph N.

    Parameters
    ----------
    N : NetworkX graph
      A graph created with NetworkX
      
    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> A=nx.to_agraph(K5)

    Notes
    -----
    If N has an dict N.graph_attr an attempt will be made first
    to copy properties attached to the graph (see from_agraph)
    and then updated with the calling arguments if any.

    """
    directed=N.is_directed()
    strict=N.number_of_selfloops()==0 and not N.is_multigraph() 
    A=pygraphviz.AGraph(name=N.name,strict=strict,directed=directed)

    # default graph attributes            
    A.graph_attr.update(N.graph.get('graph',{}))
    A.node_attr.update(N.graph.get('node',{}))
    A.edge_attr.update(N.graph.get('edge',{}))

    # add nodes
    for n,nodedata in N.nodes(data=True):
        A.add_node(n)
        node=pygraphviz.Node(A,n)
        node.attr.update(nodedata)

    # loop over edges

    if N.is_multigraph():
        for u,v,key,edgedata in N.edges_iter(data=True):
            A.add_edge(u,v,key=key,**edgedata)
    else:
        for u,v,edgedata in N.edges_iter(data=True):
            A.add_edge(u,v,**edgedata)


    return A

def write_dot(G,path):
    """Write NetworkX graph G to Graphviz dot format on path.

    Parameters
    ----------
    G : graph
       A networkx graph
    path : filename
       Filename or file handle to write.  

    """
    A=to_agraph(G)
    A.write(path)
    return

def read_dot(path,create_using=None):
    """Return a NetworkX graph from a dot file on path.

    Parameters
    ----------
    path : file or string
       File name or file handle to read.
    create_using : Graph container, optional       
       Use specified Graph container to build graph.  The default is
       nx.Graph().

    """
    A=pygraphviz.AGraph(file=path)
    return from_agraph(A)


def graphviz_layout(G,prog='neato',root=None, args=''):
    """Create node positions for G using Graphviz.

    Parameters
    ----------
    G : NetworkX graph
      A graph created with NetworkX
    prog : string
      Name of Graphviz layout program 
    root : string, optional
      Root node for twopi layout
    args : string, optional
      Extra arguments to Graphviz layout program

    Returns : dictionary      
      Dictionary of x,y, positions keyed by node.

    Examples
    --------
    >>> G=nx.petersen_graph()
    >>> pos=nx.graphviz_layout(G)
    >>> pos=nx.graphviz_layout(G,prog='dot')
    
    Notes
    -----
    This is a wrapper for pygraphviz_layout.

    """
    return pygraphviz_layout(G,prog=prog,root=root,args=args)

def pygraphviz_layout(G,prog='neato',root=None, args=''):
    """Create node positions for G using Graphviz.

    Parameters
    ----------
    G : NetworkX graph
      A graph created with NetworkX
    prog : string
      Name of Graphviz layout program 
    root : string, optional
      Root node for twopi layout
    args : string, optional
      Extra arguments to Graphviz layout program

    Returns : dictionary      
      Dictionary of x,y, positions keyed by node.

    Examples
    --------
    >>> G=nx.petersen_graph()
    >>> pos=nx.graphviz_layout(G)
    >>> pos=nx.graphviz_layout(G,prog='dot')
    
    """
    A=to_agraph(G)
    if root is not None:
        args+="-Groot=%s"%root
    A.layout(prog=prog,args=args)
    node_pos={}
    for n in G:
        node=pygraphviz.Node(A,n)
        try:
            xx,yy=node.attr["pos"].split(',')
            node_pos[n]=(float(xx),float(yy))
        except:
            print "no position for node",n
            node_pos[n]=(0.0,0.0)
    return node_pos

