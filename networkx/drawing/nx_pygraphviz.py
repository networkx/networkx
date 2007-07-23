"""
Import and export networkx networks to dot format using pygraphviz.

Provides:

 - write_dot()
 - read_dot()
 - graphviz_layout()
 - pygraphviz_layout()

 - to_pygraphviz()
 - from_pygraphviz()
 
 - xgraph_to_pygraphviz()
 - xgraph_from_pygraphviz()

and the graph layout methods:

 - graphviz_layout()
 - pygraphviz_layout()
 
Does not currently handle graphviz subgraphs.

Either this module or nx_pydot can be used to interface with graphviz.  

References:
 - pygraphviz    : http://networkx.lanl.gov/pygraphviz/
 - Graphviz:	   http://www.research.att.com/sw/tools/graphviz/
 - DOT Language:   http://www.research.att.com/~erg/graphviz/info/lang.html

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-06-15 08:55:33 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1034 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import os
import sys
from networkx.utils import is_string_like,_get_fh
try:
    import pygraphviz
except ImportError:
    raise


def write_dot(G,path):
    """Write NetworkX graph G to Graphviz dot format on path.

    Path can be a string or a file handle.
    """
    A=to_pygraphviz(G)
    fh=_get_fh(path,mode='w')
    A.write(fh)
    return

def read_dot(path):
    """Return a NetworkX Graph from a dot file on path.

    Path can be a string or a file handle.
    """
    fh=_get_fh(path,mode='r')
    A=pygraphviz.Agraph()
    A.read(fh)
    return from_pygraphviz(A)

def to_pygraphviz(N,
                  graph_attr=None,
                  node_attr=None,
                  edge_attr=None):
    """Creates a pygraphviz graph from an networkx graph N.

    This simplest use creates a pygraphviz graph with no attributes,
    just the nodes and edges. Attributes can be added by modifying
    the resulting pygraphviz graph.
 
    Optional arguments graph_attr, node_attr, edge_attr are used
    to specify Graphviz graph properties to applied during the conversion.
    http://www.graphviz.org/doc/info/attrs.html

    The graph_attr, node_attr, and edge_attr  arguments can be either
    a dictionary or function as follows:

    graph_attr:
        dictionary with keys as attribute names and values as attribute values
        or
        function that returns a dictionary of attribute names and values
        The function takes one argument - the graph name::

          def graph_attr(G):
              a={'color':'red','label'='my graph'}
              return a
        
    node_attr:
        dictionary keyed by node name that has as a value a dictionary
        of attribute names and values.
        or
        function that returns a dictionary of attribute names and values
        The function takes two arguments - the graph name and node name::

          def node_attr(G,n):
              a={'color':'red','shape'='diamond'}
              return a

    edge_attr:
        dictionary keyed by edge tuple (u,v) that has as a value a dictionary
        of attribute names and values.
        or
        function that returns a dictionary of attribute names and values
        The function takes two arguments - the graph name and edge tuple e::

          def edge_attr(G,e):
              a={'color':'red','shape'='diamond'}
              return a

    """

    if N.is_directed():
        A = pygraphviz.Agraph(name=N.name,
                              type=pygraphviz.graphviz.cvar.Agdirected)
        digraph=True
    else:
        A = pygraphviz.Agraph(name=N.name,
                              type=pygraphviz.graphviz.cvar.Agundirected)
        digraph=False

    # handle attributes, user dictionary or function
    if hasattr(graph_attr,"__getitem__"):   # if we are a dict
        get_graph_attr=graph_attr.copy   # call dict copy 
    else:
        get_graph_attr=graph_attr  # call user function

    # nodes            
    if hasattr(node_attr,"__getitem__"):   # if we are a dict
        get_node_attr=node_attr.__getitem__   # call as a function
    else:
        get_node_attr=node_attr  # call user function

    # edges
    if hasattr(edge_attr,"__getitem__"):   
        def get_edge_attr(e):
            return edge_attr[e]
    else: #    elif hasattr(edge_attr,"__call__"): 
        def get_edge_attr(e):
            return edge_attr(N,e)

    # graph attributes
    try:
        attr=get_graph_attr()
        A.set_attr(attr)
    except:
        pass

    # loop over nodes
    for n in N.nodes_iter():
        node=A.add_node(str(n))
        try:
            attr=get_node_attr(n)
            A.set_node_attr(node,attr)
        except:
            pass


    # loop over edges
    for e in N.edges_iter():
        name=None
        if len(e)==2:
            (u,v)=e
        elif len(e)==3:  # XGraph or XDigraph
            (u,v,x)=e
            if x is not None: 
                if is_string_like(x): # use data as edge name
                    name=x
        edge=A.add_edge(str(u),str(v),name)
        try:
            attr=get_edge_attr(e)
            A.set_edge_attr((u,v),attr)
        except:
            pass
        if not digraph:                    
            try:
                if len(e)==2:
                    er=(v,u)
                else:
                    er=(v,u,x)
                attr=get_edge_attr(er)
                A.set_edge_attr((v,u),attr)
            except:
                pass
    return A

def from_pygraphviz(A,
                    create_using=None,
                    graph_attr=None,
                    node_attr=None,
                    edge_attr=None):
    """Creates an networkx graph from an pygraphviz graph A.

    This simplest use creates a netwrkx graph and ignores graphviz
    attributes.
 
    Optional arguments graph_attr, node_attr, edge_attr are used
    to get graph properties.
    http://www.graphviz.org/doc/info/attrs.html

    The graph_attr, node_attr, and edge_attr  arguments can be either
    a dictionary or function as follows:

    graph_attr:
        empty dictionary will be filled with keys as attribute names and
        values as attribute values
        or
        A function that takes two arguments -
        the NetworkX graph and attributes::

          def graph_attr(G,a):
              print a # just print attributes
              return
        
    node_attr:
        empty dictionary will be filled with keys as nodes with
        value set to a dictionary of attribute names and values.
        or
        A function that takes three arguments - the graph name, node name
        and attributes::

          def node_attr(G,n,a):
              print n,a # print node and attributes
              return a

    edge_attr:
        empty dictionary will be filled with keys as  edge tuples (u,v)
        with a value set to a dictionary of attribute names and values.
        or
        A function that takes three arguments - the graph name, edge tuple,
        and attributes::

          def edge_attr(G,n,e):
              print e,a # print node and attributes
              return a


    create_using is an optional networkx graph type.
    The default is to use a Graph or DiGraph depending on the
    type of the pygraphviz graph A

    """
    import networkx

    # set graph type or user defined
    if create_using is None:
        if A.is_undirected():
            create_using=networkx.Graph()
        else:
            create_using=networkx.DiGraph()

    N=networkx.empty_graph(0,create_using)
    N.name=str(A)

    # handle graph attributes,
    if hasattr(graph_attr,"__setitem__"):   # if we are a dict
        add_graph=graph_attr.update   # call update as a function
        # user function                
    elif hasattr(graph_attr,"__call__"): 
        def add_graph(a):
            return graph_attr(N,a)
    else:
        def add_graph(a):
            return

    # add node function with optional attributes
    if hasattr(node_attr,"__setitem__"):  
        # update user dictionary 
        def add_node(n,a):
            N.add_node(n)
            node_attr[n]=a
            return
    elif hasattr(node_attr,"__call__"): 
        # call user function
        def add_node(n,a):
            node_attr(N,n,a)
            return 
    else:
        # just add node
        def add_node(n,a):
            N.add_node(n)
            return
                

    # add edge function with optional attributes
    if hasattr(edge_attr,"__setitem__"):   
        # update user dictionary
        def add_edge(e,a):
            N.add_edge(e[0],e[1])
            edge_attr[e]=a
            return
    elif hasattr(edge_attr,"__call__"): 
        # call user function
        def add_edge(e,a):
            return edge_attr(N,e,a)
    else:
        # just add edge
        def add_edge(e,a):
            N.add_edge(e[0],e[1])

    # graph                
    add_graph(dict(A.get_all_attr()))
    # loop through nodes            
    for node in A.nodes():
        name=pygraphviz.graphviz.agnameof(node.anode)
        add_node(name,A.get_all_attr(node=node))
    # loop through edges
    edges_seen = {}
    for edge in A.edges():
        if edge in edges_seen: continue
        source=pygraphviz.graphviz.agnameof(edge.source().anode)
        target=pygraphviz.graphviz.agnameof(edge.target().anode)
        edges_seen[edge]=1
        add_edge((source,target),A.get_all_attr(edge=(source,target)))
    return N

networkx_from_pygraphviz=from_pygraphviz
pygraphviz_from_networkx=to_pygraphviz

def xgraph_from_pygraphviz(A):
    """Convert from a pygraphviz graph to a NetworkX XGraph.
    
    A NetworkX XGraph XG is returned with

    XG.attr - a dictionary set to the graphviz graph attributes
    XG.nattr - a dictionary keyed by node with graphviz graph attributes

    and the edge data set to a dictionary of graphviz edge attributes.
    """
    graph_attr={}
    node_attr={}
    def set_edge_attr(N,e,attr):
        N.add_edge(e[0],e[1],attr)
        return 
    XG=XGraph(multiedges=True,selfloops=True)
    G=from_pygraphviz(A,
                      graph_attr=graph_attr,
                      node_attr=node_attr,
                      edge_attr=set_edge_attr,
                      create_using=G)

    G.attr=graph_attr
    G.nattr=node_attr
    return G

def to_pygraphviz_from_xgraph(G):
    """Convert from a NetworkX XGraph with attributes to a pygraphviz graph.
    See from_pygraphviz_to_xgraph for the special XGraph format.
    """
    def get_edge_attr(N,e):
        return e[2]
    A=to_pygraphviz(G,
                    graph_attr=G.attr,
                    node_attr=G.nattr,
                    edge_attr=get_edge_attr)

    return A


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
    import tempfile
    try:
        import pygraphviz
    except:
        print "Import Error: not able to import pygraphviz."
        raise

    if root is not None :
        args+=" -Groot=%s"%str(root)

    gprogs=dict.fromkeys(['neato','dot','twopi','circo','fdp','circa'],True)
    try:
        gprogs[prog]==True
    except:
        raise "program %s not from graphviz"%prog 
    
    try: # user must pick one of the graphviz programs...
        runprog = _which(prog)
    except:
        raise "program %s not found in path"%prog 

    tmp_fd, tmp_name = tempfile.mkstemp()
    write_dot(G, tmp_name)
    os.close(tmp_fd)
    cmd=' '.join([runprog,args,"-Tdot",tmp_name])
    stdin,stdout,stderr=os.popen3(cmd, 'b')
    try:
        A=pygraphviz.Agraph()
        A.read(stdout)
        stdin.close(); stdout.close(); stderr.close()
    except:
        print "Graphviz layout with %s failed"%(prog)
        print "the file %s might have useful information"%tmp_name
        print stderr.read()
        stdin.close(); stdout.close(); stderr.close()
        return

    os.unlink(tmp_name)
    node_pos={}
    for n in G.nodes():
        node=A.get_node(str(n))
        try:
            xx,yy=node.get_attr("pos").split(',')
            node_pos[n]=(float(xx),float(yy))
        except:
            print "no position for node",n
            node_pos[n]=(0.0,0.0)
    return node_pos

def _which(name):
    """searches for executable in path """
    import os
    import glob
    paths = os.environ["PATH"]
    for path in paths.split(os.pathsep):
        match=glob.glob(os.path.join(path, name))
        if match:
            return match[0]
    raise "no prog %s in path"%name        

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/drawing/nx_pygraphviz.txt',package='networkx')
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
    
