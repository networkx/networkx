"""
*****
Pydot
*****

Import and export NetworkX graphs in Graphviz dot format using pydot.

Either this module or nx_pygraphviz can be used to interface with graphviz.  

See Also
--------
Pydot: http://code.google.com/p/pydot/
Graphviz:	   http://www.research.att.com/sw/tools/graphviz/
DOT Language:  http://www.graphviz.org/doc/info/lang.html
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from networkx.utils import open_file, make_str
import networkx as nx
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__all__ = ['write_dot', 'read_dot', 'graphviz_layout', 'pydot_layout',
           'to_pydot', 'from_pydot']

@open_file(1,mode='w')
def write_dot(G,path):
    """Write NetworkX graph G to Graphviz dot format on path.

    Path can be a string or a file handle.
    """
    try:
        import pydot
    except ImportError:
        raise ImportError("write_dot() requires pydot",
                          "http://code.google.com/p/pydot/")
    P=to_pydot(G)
    path.write(P.to_string())
    return

@open_file(0,mode='r')
def read_dot(path):
    """Return a NetworkX MultiGraph or MultiDiGraph from a dot file on path.


    Parameters
    ----------
    path : filename or file handle

    Returns
    -------
    G : NetworkX multigraph
        A MultiGraph or MultiDiGraph.  
    
    Notes
    -----
    Use G=nx.Graph(nx.read_dot(path)) to return a Graph instead of a MultiGraph.
    """
    try:
        import pydot
    except ImportError:
        raise ImportError("read_dot() requires pydot",
                          "http://code.google.com/p/pydot/")

    data=path.read()        
    P=pydot.graph_from_dot_data(data)
    return from_pydot(P)

def from_pydot(P):
    """Return a NetworkX graph from a Pydot graph.

    Parameters
    ----------
    P : Pydot graph
      A graph created with Pydot

    Returns
    -------
    G : NetworkX multigraph
        A MultiGraph or MultiDiGraph.  
    
    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> A=nx.to_pydot(K5)
    >>> G=nx.from_pydot(A) # return MultiGraph
    >>> G=nx.Graph(nx.from_pydot(A)) # make a Graph instead of MultiGraph

    """
    if P.get_strict(None): # pydot bug: get_strict() shouldn't take argument 
        multiedges=False
    else:
        multiedges=True
        
    if P.get_type()=='graph': # undirected
        if multiedges:
            create_using=nx.MultiGraph()
        else:
            create_using=nx.Graph()
    else:
        if multiedges:
            create_using=nx.MultiDiGraph()
        else:
            create_using=nx.DiGraph()

    # assign defaults        
    N=nx.empty_graph(0,create_using)
    N.name=P.get_name()

    # add nodes, attributes to N.node_attr
    for p in P.get_node_list():
        n=p.get_name().strip('"')
        if n in ('node','graph','edge'):
            continue
        N.add_node(n,**p.get_attributes())

    # add edges
    for e in P.get_edge_list():
        u=e.get_source().strip('"')
        v=e.get_destination().strip('"')
        attr=e.get_attributes()
        N.add_edge(u,v,**attr)

    # add default attributes for graph, nodes, edges
    N.graph['graph']=P.get_attributes()
    try:
        N.graph['node']=P.get_node_defaults()[0]
    except:# IndexError,TypeError:
        N.graph['node']={}
    try:
        N.graph['edge']=P.get_edge_defaults()[0]
    except:# IndexError,TypeError:
        N.graph['edge']={}
    return N        

def to_pydot(N, strict=True):
    """Return a pydot graph from a NetworkX graph N.

    Parameters
    ----------
    N : NetworkX graph
      A graph created with NetworkX
      
    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> P=nx.to_pydot(K5)

    Notes
    -----

    """
    try:
        import pydot
    except ImportError:
        raise ImportError('to_pydot() requires pydot: '
                          'http://code.google.com/p/pydot/')

    # set Graphviz graph type
    if N.is_directed():
        graph_type='digraph'
    else:
        graph_type='graph'
    strict=N.number_of_selfloops()==0 and not N.is_multigraph() 
    
    name = N.graph.get('name')
    graph_defaults=N.graph.get('graph',{})
    if name is None:
        P = pydot.Dot(graph_type=graph_type,strict=strict,**graph_defaults)
    else:
        P = pydot.Dot('"%s"'%name,graph_type=graph_type,strict=strict,
                      **graph_defaults)
    try:
        P.set_node_defaults(**N.graph['node'])
    except KeyError:
        pass
    try:
        P.set_edge_defaults(**N.graph['edge'])
    except KeyError:
        pass

    for n,nodedata in N.nodes_iter(data=True):
        str_nodedata=dict((k,make_str(v)) for k,v in nodedata.items())
        p=pydot.Node(make_str(n),**str_nodedata)
        P.add_node(p)

    if N.is_multigraph():
        for u,v,key,edgedata in N.edges_iter(data=True,keys=True):
            str_edgedata=dict((k,make_str(v)) for k,v in edgedata.items())
            edge=pydot.Edge(make_str(u),make_str(v),key=make_str(key),**str_edgedata)
            P.add_edge(edge)
        
    else:
        for u,v,edgedata in N.edges_iter(data=True):
            str_edgedata=dict((k,make_str(v)) for k,v in edgedata.items())
            edge=pydot.Edge(make_str(u),make_str(v),**str_edgedata)
            P.add_edge(edge)

    return P


def pydot_from_networkx(N):
    """Create a Pydot graph from a NetworkX graph."""
    from warnings import warn
    warn('pydot_from_networkx is replaced by to_pydot', DeprecationWarning)
    return to_pydot(N)

def networkx_from_pydot(D, create_using=None):
    """Create a NetworkX graph from a Pydot graph."""
    from warnings import warn
    warn('networkx_from_pydot is replaced by from_pydot', 
         DeprecationWarning)
    return from_pydot(D)

def graphviz_layout(G,prog='neato',root=None, **kwds):
    """Create node positions using Pydot and Graphviz.

    Returns a dictionary of positions keyed by node.

    Examples
    --------
    >>> G=nx.complete_graph(4)
    >>> pos=nx.graphviz_layout(G)
    >>> pos=nx.graphviz_layout(G,prog='dot')

    Notes
    -----
    This is a wrapper for pydot_layout.

    """
    return pydot_layout(G=G,prog=prog,root=root,**kwds)


def pydot_layout(G,prog='neato',root=None, **kwds):
    """Create node positions using Pydot and Graphviz.

    Returns a dictionary of positions keyed by node.

    Examples
    --------
    >>> G=nx.complete_graph(4)
    >>> pos=nx.pydot_layout(G)
    >>> pos=nx.pydot_layout(G,prog='dot')
    
    """
    try:
        import pydot
    except ImportError:
        raise ImportError('pydot_layout() requires pydot ',
                          'http://code.google.com/p/pydot/')

    P=to_pydot(G)
    if root is not None :
        P.set("root",make_str(root))

    D=P.create_dot(prog=prog)

    if D=="":  # no data returned
        print("Graphviz layout with %s failed"%(prog))
        print()
        print("To debug what happened try:")
        print("P=pydot_from_networkx(G)")
        print("P.write_dot(\"file.dot\")")
        print("And then run %s on file.dot"%(prog))
        return

    Q=pydot.graph_from_dot_data(D)

    node_pos={}
    for n in G.nodes():
        pydot_node = pydot.Node(make_str(n)).get_name().encode('utf-8')
        node=Q.get_node(pydot_node)

        if isinstance(node,list):
            node=node[0]
        pos=node.get_pos()[1:-1] # strip leading and trailing double quotes
        if pos != None:
            xx,yy=pos.split(",")
            node_pos[n]=(float(xx),float(yy))
    return node_pos

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import pydot
    except:
        raise SkipTest("pydot not available")
