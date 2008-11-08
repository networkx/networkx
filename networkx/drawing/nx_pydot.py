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


def from_pydot(P):
    """Return a NetworkX Graph or DiGraph from a pydot graph.

    The Graph X will have a dictionary X.graph_attr containing
    the default graphviz attributes for graphs, nodes and edges.

    Default node attributes will be in the dictionary X.node_attr
    which is keyed by node.

    Edge attributes will be returned as edge data in the graph X.

    Examples
    ---------

    >>> G=nx.complete_graph(5)
    >>> P=nx.to_pydot(G)
    >>> X=nx.from_pydot(P)

    If you want a Graph with no attributes attached use

    >>> G=nx.Graph(X)

    Similarly to make a DiGraph without attributes

    >>> D=nx.DiGraph(X)

    """
    import networkx

    if P.get_strict(None): # pydot bug: get_strict() shouldn't take argument 
        multiedges=False
        selfloops=False
    else:
        multiedges=True
        selfloops=True
        
    if P.get_type()=='graph': # undirected
        if P.get_strict(None):
            create_using=networkx.Graph()
        else:
            create_using=networkx.MultiGraph()
    else:
        if P.get_strict(None):
            create_using=networkx.DiGraph()
        else:
            create_using=networkx.MultiDiGraph()

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
        source=e.get_source()
        dest=e.get_destination()
        if hasattr(N,'allow_multiedges')==True: # XGraph or XDiGraph
            N.add_edge(source,dest,e.get_attributes())
        else: # Graph
            N.add_edge(source,dest)

    # add default attributes for graph, nodes, and edges       
    # hang them on N.graph_attr
    if hasattr(N,'allow_multiedges')==True: # XGraph
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

def to_pydot(N, graph_attr=None, node_attr=None, edge_attr=None,
              strict=True):
    """Return a pydot graph from a NetworkX graph N.

    If N is a Graph or DiGraph, graphviz attributes can
    be supplied through the keyword arguments

    graph_attr:  dictionary with default attributes for graph, nodes, and edges
                 keyed by 'graph', 'node', and 'edge' to attribute dictionaries

    node_attr: dictionary keyed by node to node attribute dictionary

    edge_attr: dictionary keyed by edge tuple to edge attribute dictionary

    If N is an XGraph or XDiGraph an attempt will be made first
    to copy properties attached to the graph (see from_pydot)
    and then updated with the calling arguments, if any.

    """
    if hasattr(N,'graph_attr'):
        graph_attributes=N.graph_attr
    else:
        graph_attributes={}
    if graph_attr is not None:
        graph_attributes.update(graph_attr)

    if N.directed:
        graph_type='digraph'
    else:
        graph_type='graph'
    if hasattr(N,'allow_multiedges'):
        if N.multiedges:
            strict=False
    if hasattr(N,'allow_selfloops'):
        if N.selfloops:
            strict=False

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

    for e in N.edges_iter():
        if len(e)==2:
            (u,v)=e
            edge=pydot.Edge(str(u),str(v))
            P.add_edge(edge)
        if len(e)==3:
            (u,v,x)=e
            try:
                N.allow_multiedges()==True
                dlist=N.get_edge(u,v)
            except:
                dlist=[N.get_edge(u,v)]
            for d in dlist:
                if hasattr(d,"__iter__"):
                    attr=d
                else:
                    attr={'label':d}
                try:
                    attr.update(edge_attr[(u,v)])                    
                except:
                    pass
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
	"""Creates a pydot graph from an networkx graph N"""
        from warnings import warn
        warn('pydot_from_networkx is replaced by to_pydot', DeprecationWarning)
        return to_pydot(N)

def networkx_from_pydot(D, create_using=None):
	"""Creates an networkx graph from an pydot graph D"""
        from warnings import warn
        warn('networkx_from_pydot is replaced by from_pydot', 
             DeprecationWarning)
        return from_pydot(D)

def graphviz_layout(G,prog='neato',root=None, **kwds):
    """Create layout using pydot and graphviz.
    Returns a dictionary of positions keyed by node.

    >>> G=nx.complete_graph(4)
    >>> pos=nx.graphviz_layout(G)
    >>> pos=nx.graphviz_layout(G,prog='dot')

    This is a wrapper for pydot_layout.

    """
    return pydot_layout(G=G,prog=prog,root=root,**kwds)


def pydot_layout(G,prog='neato',root=None, **kwds):
    """
    Create layout using pydot and graphviz.
    Returns a dictionary of positions keyed by node.

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

