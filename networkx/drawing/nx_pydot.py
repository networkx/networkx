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

import os
import sys
import tempfile
import time

from networkx.utils import (
    open_file, get_fobj, make_str, default_opener
)
import networkx as nx

__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__all__ = ['write_dot', 'read_dot', 'graphviz_layout', 'pydot_layout',
           'to_pydot', 'from_pydot', 'draw_pydot']

DEFAULT_SHOW = True

@open_file(1, mode='w')
def write_dot(G, path):
    """Write NetworkX graph G to Graphviz dot format on path.

    Path can be a string or a file handle.
    """
    P=to_pydot(G)
    path.write(P.to_string())
    return

@open_file(0, mode='r')
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
    import pydot
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

def filter_attrs(attrs, attr_type):
    """
    Helper function to keep only pydot supported attributes.

    All unsupported attributes are filtered out.

    Parameters
    ----------
    attrs : dict
        A dictionary of attributes.
    attr_type : str
        The type of attributes. Must be 'edge', 'graph', or 'node'.

    Returns
    -------
    d : dict
        The filtered attributes.

    """
    import pydot

    if attr_type == 'edge':
        accepted = pydot.EDGE_ATTRIBUTES
    elif attr_type == 'graph':
        accepted = pydot.GRAPH_ATTRIBUTES
    elif attr_type == 'node':
        accepted = pydot.NODE_ATTRIBUTES
    else:
        raise Exception("Invalid attr_type.")

    d = dict( [(k,v) for (k,v) in attrs.iteritems() if k in accepted] )
    return d

def to_pydot(G, raise_exceptions=True):
    """Return a pydot graph from a NetworkX graph G.

    All node names are converted to strings.  However, no preprocessing is
    performed on the edge/graph/node attribute values since some attributes
    need to be strings while other need to be floats. If pydot does not handle
    needed conversions, then your graph should be modified beforehand.

    Generally, the rule is:  If the attribute is a supported Graphviz
    attribute, then it will be added to the Pydot graph (and thus, assumed to
    be in the proper format for Graphviz).

    Parameters
    ----------
    G : NetworkX graph
        A graph created with NetworkX.
    raise_exceptions : bool
        If `True`, raise any exceptions.  Otherwise, the exception is ignored
        and the procedure continues.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> G.add_edge(2, 10, color='red')
    >>> P = nx.to_pydot(G)

    """
    import pydot

    # Set Graphviz graph type.
    if G.is_directed():
        graph_type = 'digraph'
    else:
        graph_type = 'graph'
    strict = G.number_of_selfloops() == 0 and not G.is_multigraph()

    # Create the Pydot graph.
    name = G.graph.get('name')
    graph_defaults = filter_attrs(G.graph, 'graph')
    if name is None:
        P = pydot.Dot(graph_type=graph_type, strict=strict, **graph_defaults)
    else:
        P = pydot.Dot(name, graph_type=graph_type, strict=strict,
                      **graph_defaults)

    # Set default node attributes, if possible.
    node_defaults = filter_attrs(G.graph.get('node', {}), 'node')
    if node_defaults:
        try:
            P.set_node_defaults(**node_defaults)
        except:
            if raise_exceptions:
                raise

    # Set default edge attributes, if possible.
    edge_defaults = filter_attrs(G.graph.get('edge', {}), 'edge')
    if edge_defaults:
        # This adds a node called "edge" to the graph.
        try:
            P.set_edge_defaults(**edge_defaults)
        except:
            if raise_exceptions:
                raise

    # Add the nodes.
    for n,nodedata in G.nodes_iter(data=True):
        attrs = filter_attrs(nodedata, 'node')
        node = pydot.Node(make_str(n), **attrs)
        P.add_node(node)

    # Add the edges.
    if G.is_multigraph():
        for u,v,key,edgedata in G.edges_iter(data=True,keys=True):
            attrs = filter_attrs(edgedata, 'edge')
            uu, vv, kk = make_str(u), make_str(v), make_str(key)
            edge = pydot.Edge(uu, vv, key=kk, **attrs)
            P.add_edge(edge)
    else:
        for u,v,edgedata in G.edges_iter(data=True):
            attrs = filter_attrs(edgedata, 'edge')
            uu, vv = make_str(u), make_str(v)
            edge = pydot.Edge(uu, vv, **attrs)
            P.add_edge(edge)

    return P

def graphviz_layout(G, prog='neato', root=None, **kwds):
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


def pydot_layout(G, prog='neato', root=None, **kwds):
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


def safer_pydot_write(self, path, prog=None, format='raw'):
    """
    pydot.Dot.write() is not safe to use with temporary files since it
    requires a string be passed in for the filename.  We provide a modified
    version here.

    This was needed in Pydot 1.0.28.

    """
    if prog is None:
        prog = self.prog

    fobj, close = get_fobj(path, 'w+b')
    try:
        if format == 'raw':
            data = self.to_string()
            if isinstance(data, basestring):
                if not isinstance(data, unicode):
                    try:
                        data = unicode(data, 'utf-8')
                    except:
                        pass

            try:
                data = data.encode('utf-8')
            except:
                pass
            fobj.write(data)
        else:
            fobj.write(self.create(prog, format))
    finally:
        if close:
            fobj.close()

    return True


def draw_pydot(G, filename=None, format=None, prefix=None, suffix=None,
                  layout='dot', args=None, show=None):
    """Draws the graph G using pydot and graphviz.

    Parameters
    ----------
    G : graph
        A NetworkX graph object (e.g., Graph, DiGraph).

    filename : str, None, file object
        The name of the file to save the image to.  If None, save to a
        temporary file with the name:
             nx_PREFIX_RANDOMSTRING_SUFFIX.ext.
        File formats are inferred from the extension of the filename, when
        provided.  If the `format` parameter is not `None`, it overwrites any
        inferred value for the extension.

    format : str
        An output format. Note that not all may be available on every system
        depending on how Graphviz was built. If no filename is provided and
        no format is specified, then a 'png' image is created. Other values
        for `format` are:

            'canon', 'cmap', 'cmapx', 'cmapx_np', 'dia', 'dot',
            'fig', 'gd', 'gd2', 'gif', 'hpgl', 'imap', 'imap_np',
            'ismap', 'jpe', 'jpeg', 'jpg', 'mif', 'mp', 'pcl', 'pdf',
            'pic', 'plain', 'plain-ext', 'png', 'ps', 'ps2', 'svg',
            'svgz', 'vml', 'vmlz', 'vrml', 'vtx', 'wbmp', 'xdot', 'xlib'

    prefix : str | None
        If `filename` is None, we save to a temporary file.  The value of
        `prefix` will appear after 'nx_' but before random string
        and file extension. If None, then the graph name will be used.

    suffix : str | None
        If `filename` is None, we save to a temporary file.  The value of
        `suffix` will appear at after the prefix and random string but before
        the file extension. If None, then no suffix is used.

    layout : str
        The graphviz layout program.  Pydot is responsible for locating the
        binary. Common values for the layout program are:
            'neato','dot','twopi','circo','fdp','nop', 'wc','acyclic','gvpr',
            'gvcolor','ccomps','sccmap','tred'

    args : list
        Additional arguments to pass to the Graphviz layout program.
        This should be a list of strings.  For example, ['-s10', '-maxiter=10'].

    show : bool
        If `True`, then the image is displayed using the default viewer
        after drawing it. If show equals 'ipynb', then the image is displayed
        inline for an IPython notebook.  If `None`, then the value of the
        global variable DEFAULT_SHOW is used.  By default, it is set to `True`.

    """
    # Determine the output format
    if format is None:
        # grab extension from filename
        if filename is None:
            # default to png
            ext = 'png'
        else:
            ext = os.path.splitext(filename)[-1].lower()[1:]
    else:
        ext = format

    # Determine the "path" to be passed to pydot.Dot.write()
    if filename is None:
        if prefix is None:
            prefix = G.graph.get("name", '')

        if prefix:
            fn_prefix = "nx_{0}_".format(prefix)
        else:
            fn_prefix = "nx_"

        if suffix:
            fn_suffix = '_{0}.{1}'.format(suffix, ext)
        else:
            fn_suffix = '.{0}'.format(ext)

        fobj = tempfile.NamedTemporaryFile(prefix=fn_prefix,
                                           suffix=fn_suffix,
                                           delete=False)
        fname = fobj.name
        close = True
    else:
        fobj, close = get_fobj(filename, 'w+b')
        fname = fobj.name

    # Include additional command line arguments to the layout program.
    if args is None:
        args = []
        prog = layout
    else:
        args = list(args)
        prog = [layout] + args

    # Draw the image.
    G2 = to_pydot(G)
    safer_pydot_write(G2, fobj, prog=prog, format=ext)
    if close:
        fobj.close()

    if show is None:
        # Configurable global default behavior
        # Eventually, place in some rcParams.
        #    nx.rcParams['pydot.show'] = True
        #    nx.rcParams['pydot.show'] = 'ipynb'
        show = DEFAULT_SHOW

    if show:
        if show == 'ipynb':
            from IPython.core.display import Image
            return Image(filename=fname, embed=True)
        else:
            default_opener(fname)
            if sys.platform == 'linux2':
                # necessary when opening many images in a row
                time.sleep(.5)

    return fname

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import pydot
    except:
        raise SkipTest("pydot not available")
