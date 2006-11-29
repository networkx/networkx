"""
Interface to pygraphviz AGraph class.

Usage 

 >>> from networkx import *
 >>> G=complete_graph(5)
 >>> A=to_agraph(G)
 >>> H=from_agraph(A)

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__credits__ = """"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import os
import sys
from networkx.io import _get_fh
try:
    import pygraphviz
except ImportError:
    raise

def from_agraph(A,create_using=None):
    """Return a NetworkX XGraph or XDiGraph from a pygraphviz graph.

    >>> X=from_agraph(A)

    The XGraph X will have a dictionary X.graph_attr containing
    the default graphviz attributes for graphs, nodes and edges.

    Default node attributes will be in the dictionary X.node_attr
    which is keyed by node.

    Edge attributes will be returned as edge data in the graph X.

    If you want a Graph with no attributes attached instead of an XGraph
    with attributes use

    >>> G=Graph(X)

    """
    import networkx
    if A.is_strict():
        multiedges=False
        selfloops=False
    else:
        multiedges=True
        selfloops=True
        
    if create_using is None:        
        if A.is_undirected():
            create_using=networkx.XGraph(multiedges=multiedges,
                                         selfloops=selfloops)
        else:
            create_using=networkx.XDiGraph(multiedges=multiedges,
                                           selfloops=selfloops)

    # assign defaults        
    N=networkx.empty_graph(0,create_using)
    N.name=str(A)
    node_attr={}
    # add nodes, attributes to N.node_attr
    for n in A.nodes():
        N.add_node(n)
        node_attr[n]=n.attr

    # add edges, attributes attached to edge
    for e in A.edges():
        if len(e)==2:
            u,v=e
        else:
            u,v,k=e
        if hasattr(N,'allow_multiedges')==True: # XGraph
            N.add_edge(u,v,e.attr)
        else: # Graph
            N.add_edge(u,v)
        
    # add default attributes for graph, nodes, and edges       
    # hang them on N.graph_attr
    if hasattr(N,'allow_multiedges')==True: # XGraph
        N.graph_attr={}
        N.graph_attr['graph']=A.graph_attr
        N.graph_attr['node']=A.node_attr
        N.graph_attr['edge']=A.edge_attr
        N.node_attr=node_attr

    return N        

def to_agraph(N, graph_attr=None, node_attr=None, edge_attr=None,
              strict=True):
    """Return a pygraphviz graph from a NetworkX graph N.

    If N is a Graph or DiGraph, graphviz attributes can
    be supplied through the arguments

    graph_attr:  dictionary with default attributes for graph, nodes, and edges
                 keyed by 'graph', 'node', and 'edge' to attribute dictionaries

    node_attr: dictionary keyed by node to node attribute dictionary

    edge_attr: dictionary keyed by edge tuple to edge attribute dictionary

    If N is an XGraph or XDiGraph an attempt will be made first
    to copy properties attached to the graph (see from_agraph)
    and then updated with the calling arguments if any.

    """
    directed= N.is_directed()
    A=pygraphviz.AGraph(name=N.name,strict=strict,directed=directed)

    # default graph attributes            
    try:             
        A.graph_attr.update(N.graph_attr['graph'])
    except:
        pass
    try:
        A.graph_attr.update(graph_attr['graph'])
    except:
        pass
    # default node attributes            
    try:        
        A.node_attr.update(N.graph_attr['node'])
    except:
        pass
    try:
        A.node_attr.update(graph_attr['node'])
    except:
        pass
    # default edge attributes            
    try:        
        A.edge_attr.update(N.graph_attr['edge'])
    except:
        pass
    try:
        A.edge_attr.update(graph_attr['edge'])
    except:
        pass

    # add nodes
    for n in N.nodes_iter():
        A.add_node(n)
        node=pygraphviz.Node(A,n)
        # try node attributes attached to graph
        try:
            if n in N.node_attr:
                node.attr.update(N.node_attr[n])
        except:
            pass
        # update with attributes from calling parameters
        try:
            if n in node_attr:
                node.attr.update(node_attr[n])
        except:
            pass

    # loop over edges
    for e in N.edges_iter():
        if len(e)==2:
            (u,v)=e
            data=None
        else:
            (u,v,data)=e

        if data is None: # no data, just add edge
            A.add_edge(u,v)
            edge=pygraphviz.Edge(A,u,v)
        else: # could have list of edge data or single edge data
            try:
                N.allow_multiedges()==True
                dlist=N.get_edge(u,v)
            except:
                dlist=[N.get_edge(u,v)]
            for d in dlist:
                A.add_edge(u,v)
                edge=pygraphviz.Edge(A,u,v)
                if hasattr(d,"__getitem__"):
                    edge.attr.update(d)
        # update from calling argument
        try:  # e might not be hashable
            if (u,v) in edge_attr:
                edge.attr.update(edge_attr[(u,v)])
        except:
            pass

    return A

def write_dot(G,path):
    """Write NetworkX graph G to Graphviz dot format on path.

    Path can be a string or a file handle.
    """
    A=to_agraph(G)
    A.write(path)
    return

def read_dot(path,create_using=None):
    """Return a NetworkX XGraph or XdiGraph from a dot file on path.

    Path can be a string or a file handle.

    """
    A=pygraphviz.AGraph(file=path)
    return from_agraph(A)


def graphviz_layout(G,prog='neato',root=None, args=''):
    """
    Create layout using graphviz.
    Returns a dictionary of positions keyed by node.

    >>> from networkx import *
    >>> G=petersen_graph()
    >>> pos=graphviz_layout(G)
    >>> pos=graphviz_layout(G,prog='dot')
    
    This is a wrapper for pygraphviz_layout.

    """
    return pygraphviz_layout(G,prog=prog,root=root,args=args)

def pygraphviz_layout(G,prog='neato',root=None, args=''):
    """
    Create layout using pygraphviz and graphviz.
    Returns a dictionary of positions keyed by node.

    >>> from networkx import *
    >>> G=petersen_graph()
    >>> pos=pygraphviz_layout(G)
    >>> pos=pygraphviz_layout(G,prog='dot')
    
    """
    A=to_agraph(G)
    A.layout(prog=prog)
    node_pos={}
    for n in G.nodes():
        node=pygraphviz.Node(A,n)
        try:
            xx,yy=node.attr["pos"].split(',')
            node_pos[n]=(float(xx),float(yy))
        except:
            print "no position for node",n
            node_pos[n]=(0.0,0.0)
    return node_pos


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/drawing/nx_agraph.txt',package='networkx')
    return suite




if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())

