"""
*****
Pydot
*****

Import and export NetworkX graphs in Graphviz dot format using pydot.

Either this module or nx_pygraphviz can be used to interface with graphviz.  

References:
 - pydot Homepage: http://www.dkbza.org/pydot.html
 - Graphviz:	   http://www.research.att.com/sw/tools/graphviz/
 - DOT Language:   http://www.research.att.com/~erg/graphviz/info/lang.html

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__all__ = ['write_dot', 'read_dot', 'graphviz_layout', 'pydot_layout',
           'to_pydot', 'from_pydot']

import sys
from networkx.utils import _get_fh
try:
    import pydot
except ImportError:
    raise

def write_dot(G,path):
    """Write NetworkX graph G to Graphviz dot format on path.

    Path can be a string or a file handle.
    """
    fh=_get_fh(path,'w')
    P=to_pydot(G)
    fh.write(P.to_string())
    fh.flush() # might be a user filehandle so leave open (but flush)
    return

def read_dot(path):
    """Return a NetworkX Graph or DiGraph from a dot file on path.

    Path can be a string or a file handle.

    """
    fh=_get_fh(path,'r')
    data=fh.read()        
    P=pydot.graph_from_dot_data(data)
    return from_pydot(P)


def from_pydot(P,edge_attr=True):
    """Return a NetworkX graph from a Pydot graph.

    Parameters
    ----------
    P : Pydot graph
      A graph created with Pydot

    edge_attr : bool, optional
       If True use a dictionary of attributes for edge data.
       If False use the Graphviz edge weight attribute or 
       default 1 if the edge has no specified weight.

    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> A=nx.to_pydot(K5)
    >>> G=nx.from_pydot(A)
    >>> G=nx.from_pydot(A,edge_attr=False)
    Notes
    -----
    The Graph G will have a dictionary G.graph_attr containing
    the default graphviz attributes for graphs, nodes and edges.

    Default node attributes will be in the dictionary G.node_attr
    which is keyed by node.

    Edge attributes will be returned as edge data in G.  With
    edge_attr=False the edge data will be the Graphviz edge weight
    """
    import networkx

    if P.get_strict(None): # pydot bug: get_strict() shouldn't take argument 
        multiedges=False
    else:
        multiedges=True
        
    if P.get_type()=='graph': # undirected
        if multiedges:
            create_using=networkx.MultiGraph()
        else:
            create_using=networkx.Graph()
    else:
        if multiedges:
            create_using=networkx.MultiDiGraph()
        else:
            create_using=networkx.DiGraph()

    # assign defaults        
    N=networkx.empty_graph(0,create_using)
    N.name=P.get_name()
    node_attr={}

    # add nodes, attributes to N.node_attr
    for p in P.get_node_list():
        n=p.get_name()
        if n.startswith('"'):
            n=n[1:-1]
        if n in ('node','graph','edge'):
            continue
        N.add_node(n)
        node_attr[n]=p.get_attributes()

    # add edges
    for e in P.get_edge_list():
        u=e.get_source()
        v=e.get_destination()
        attr=e.get_attributes()
        if edge_attr:
            N.add_edge(u,v,attr)
        else:
            N.add_edge(u,v,float(attr.get('weight',1)))

    # add default attributes for graph, nodes, edges
    # hang them on N.graph_attr
    N.graph_attr={}
    N.graph_attr['graph']=P.get_attributes()
    # get atributes not working for these?
    # get_node_defaults()
    if 'node' in P.obj_dict['nodes']:
        N.graph_attr['node']=P.obj_dict['nodes']['node'][0]['attributes']
    # get_edge_defaults()
    if 'edge' in P.obj_dict['nodes']:
        N.graph_attr['edge']=P.obj_dict['nodes']['edge'][0]['attributes']
    N.node_attr=node_attr

    return N        

def to_pydot(N, graph_attr=None, node_attr=None, strict=True):
    """Return a pydot graph from a NetworkX graph N.

    Parameters
    ----------
    N : NetworkX graph
      A graph created with NetworkX
      
    graph_attr: dictionary,optional 
       Dictionary with default attributes for graph, nodes, and edges
       keyed by 'graph', 'node', and 'edge' to attribute dictionaries.
       Example: graph_attr['graph']={'pack':'true','epsilon':0.01}

    node_attr: dictionary, optional
       Dictionary keyed by node to node attribute dictionary.

    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> P=nx.to_pydot(K5)

    Notes
    -----
    If N has an dict N.graph_attr an attempt will be made first
    to copy properties attached to the graph
    and then updated with the calling arguments if any.

    """
    if hasattr(N,'graph_attr'):
        graph_attributes=N.graph_attr
    else:
        graph_attributes={}
    if graph_attr is not None:
        graph_attributes.update(graph_attr)

    # set Graphviz graph type
    if N.directed:
        graph_type='digraph'
    else:
        graph_type='graph'
    strict=N.number_of_selfloops()==0 and not N.multigraph 

    try:
        node_a=N.node_attr
    except:
        node_a={}
    if node_attr is not None:        
        node_a.update(node_attr)

    P = pydot.Dot(graph_type=graph_type,strict=strict)

    for n in N.nodes_iter():
        if n in node_a:
            attr=node_a[n]
        else:
            attr={}
        p=pydot.Node(str(n),**attr)
        P.add_node(p)

    for u,v,d in N.edges_iter(data=True):
        if N.multigraph==True:
            dlist=N[u][v]
        else:
            dlist=[N[u][v]]
        for d in dlist:
            if hasattr(d,"__iter__"):
                attr=d
            else:
                attr={'weight':str(d)}
            edge=pydot.Edge(str(u),str(v),**attr)
            P.add_edge(edge)

    try:
        P.obj_dict['attributes'].update(graph_attributes['graph'])
    except:
        pass
    try:
        P.obj_dict['nodes']['node'][0]['attributes'].update(graph_attributes['node'])
    except:
        pass
    try:
        P.obj_dict['nodes']['edge'][0]['attributes'].update(graph_attributes['edge'])
    except:
        pass

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
    from networkx.drawing.nx_pydot import pydot_from_networkx
    try:
        import pydot
    except:
        print "Import Error: not able to import pydot."
        raise
    P=to_pydot(G)
    if root is not None :
        P.set("root",str(root))

    D=P.create_dot(prog=prog)

    if D=="":  # no data returned
        print "Graphviz layout with %s failed"%(prog)
        print
        print "To debug what happened try:"
        print "P=pydot_from_networkx(G)"
        print "P.write_dot(\"file.dot\")"
        print "And then run %s on file.dot"%(prog)
        return

    Q=pydot.graph_from_dot_data(D)

    node_pos={}
    for n in G.nodes():
        node=Q.get_node(str(n))
        pos=node.get_pos()[1:-1] # strip leading and trailing double quotes
        if pos != None:
            xx,yy=pos.split(",")
            node_pos[n]=(float(xx),float(yy))
    return node_pos

