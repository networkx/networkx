"""
Draw networks with matplotlib/pylab.

References:
 - matplotlib:     http://matplotlib.sourceforge.net/

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-06-15 11:29:39 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1035 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import NX
import math
import sys
from string import split
try:
    from matplotlib.axes import Subplot
    import matplotlib.cbook as cb
    from matplotlib.colors import colorConverter, normalize, Colormap
    import matplotlib.cm as cm
    from matplotlib.collections import PatchCollection,\
                                       RegularPolyCollection,\
                                       LineCollection
    from matplotlib.numerix import sin, cos, pi, asarray, sqrt, arctan2
    from matplotlib.numerix import arange as narange
    from matplotlib.pylab import gca, gci, hold, text, \
             draw_if_interactive, show, savefig,\
             figure, clf, ion, ioff
    # matplotlib.pylab draw conflicts with draw in this module
    from matplotlib.pylab import draw as redraw
except ImportError:
#    print "Import Error: not able to import matplotlib."
    raise

def draw_circular(G, **kwargs):
    """Draw NX graph in circular layout"""
    from NX.drawing.layout import circular_layout
    draw_nx(G,circular_layout(G),**kwargs)
    
def draw_random(G, **kwargs):
    """Draw NX graph with random layout."""
    from NX.drawing.layout import random_layout
    draw_nx(G,random_layout(G),**kwargs)

def draw_spectral(G, **kwargs):
    """Draw NX graph with spectral layout."""
    from NX.drawing.layout import spectral_layout
    draw_nx(G,spectral_layout(G),**kwargs)

def draw_spring(G, **kwargs):
    """Draw NX graph with spring layout"""
    from NX.drawing.layout import spring_layout
    draw_nx(G,spring_layout(G),**kwargs)

    
def draw_shell(G, **kwargs):
    """Draw NX graph with shell layout"""
    from NX.drawing.layout import shell_layout
    nlist = kwargs.get('nlist', None)
    if nlist != None:        
        del(kwargs['nlist'])
    draw_nx(G,shell_layout(G,nlist=nlist),**kwargs)

def drawg(G, **kwargs):
    """Draw NX graph using spring layout"""
    draw_spring(G,**kwargs)

def draw(G, **kwargs):
    """Draw NX graph using spring layout.
    NB:
    pylab.draw() has been renamed to pylab.redraw()
    so use redraw() from pylab interface.
    """
    draw_spring(G,**kwargs)


def draw_nx(G, node_pos, **kwargs):
    """ Draw NX graph with nodes at node_pos.
    See layout.py for functions that compute node positions.

    node_pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.

    Use kwarg of node_color with a dictionary keyed by vertex with a 
    floating point number as a value.

    Use kwarg of node_size with a dictionary keyed by vertex with a 
    floating point number as a value.

    """
    # set node positions
    np={}
    for n in G.nodes():
        try:
            np[n]=node_pos[n]
        except KeyError:
            raise NX.NetworkXError, "node %s doesn't have position"%n

    # set edge positions
    edge_pos=[]
    for e in G.edges_iter():
        # The edge e can be a 2-tuple (Graph) or a 3-tuple (Xgraph)
        u=e[0]
        v=e[1]
        if v in node_pos and u in node_pos:
            edge_pos.append((tuple(node_pos[u]),tuple(node_pos[v])))
    digraph=G.is_directed()
    ax=gca()
 # allow callers to override the hold state by passing hold=True|False
    b = gca().ishold()
    h = kwargs.get('hold', None)
    if h is not None:
        hold(h)
    try:
        ret =  mpl_network(ax, np, edge_pos, digraph=digraph, **kwargs)
        draw_if_interactive()
    except:
        hold(b)
        raise
    hold(b)
    return ret


def draw_nxpydot(G,**kwds):
    """Draw NX graph using pydot and graphviz layout.

    >>> G=barbell_graph(5,10)
    >>> d=G.degree(with_labels=True)
    >>> draw_nxpydot(G)
    >>> draw_nxpydot(G,node_color=d,cmap=cm.pink)
    >>> draw_nxpydot(G,prog='neato')
    
    Can use prog= "neato", "dot", "circo", "twopi", or "fdp"

    """
    from NX.drawing.nx_pydot import pydot_from_NX
    try:
        from pydot import graph_from_dot_data
    except:
        print "Import Error: not able to import pydot."
        raise
    prog = kwds.get('prog', "neato")
    P=pydot_from_NX(G)
    D=P.create_dot(prog=prog)
    if D=="":  # no data returned
        print "Graphviz layout with %s failed"%(prog)
        print
        print "To debug what happened try:"
        print "P=pydot_from_NX(G)"
        print "P.write_dot(\"file.dot\")"
        print "And then run %s on file.dot"%(prog)
        return

    Q=graph_from_dot_data(D)

    if kwds.has_key('prog'):
        del(kwds['prog'])
    draw_pydot(Q,**kwds)


def draw_nxpydot_nolabels(G,**kwargs):
    """Draw NX graph without labels in textbook style.

    node_color is black, unless specified in kwargs
    (with node_color= a dictionary that maps each key=node to  a 
    floating point number.)
    e.g.
    >>> G=star_graph(10)
    >>> d=G.degree(with_labels=True)
    >>> draw_nxpydot_nolabels(G)
    >>> draw_nxpydot_nolabels(G,node_color=d,cmap=cm.pink)
    >>> draw_nxpydot_nolabels(G,prog='neato')

    Can use prog= "neato", "dot", "circo", "twopi", or "fdp"
    
    """
    ncolor= kwargs.get('node_color', None)
    if ncolor is None:
        draw_nxpydot(G,node_size=50,node_labels=False,node_color='k',
                     **kwargs)
    else:
        draw_nxpydot(G,node_size=50,node_labels=False,**kwargs)
    return


def draw_pydot(P, **kwargs):
    """Draw pydot graph P with matplotlib.
    The pydot graph must have position information in graphviz dot format.
    """
    # create from pydot
    notnode={"graph":1,"node":1,"edge":1}        
    node_pos={}
    for node in P.get_node_list():
        if node.name in notnode:
            continue
        if node.pos != None:
            xx,yy=split(node.pos,",")
            node_pos[node.name]=(float(xx),float(yy))
    edge_pos=[]
    for edge in P.get_edge_list():
        edge_pos.append((node_pos[edge.src],node_pos[edge.dst]))
    if P.graph_type=='digraph':
        digraph=True
    else:
        digraph=False
    ax=gca()
    # test and convert color dict to be keyed by string, nasty hack 4sure
    c=kwargs.get("node_color")
    if cb.iterable(c) and not cb.is_string_like(c):
        test=c.keys().pop()
        if not cb.is_string_like(test):
            node_color_new={}
            for node in c:
                node_color_new[str(node)]=c[node]
            kwargs["node_color"]=node_color_new

 # allow callers to override the hold state by passing hold=True|False
    b = gca().ishold()
    h = kwargs.get('hold', None)
    if h is not None:
        hold(h)
    try:
        ret =  mpl_network(ax, node_pos, edge_pos, digraph=digraph, **kwargs)
        draw_if_interactive()
    except:
        hold(b)
        raise
    hold(b)
    return ret

def draw_pydot_subgraph(ax,P,**kwds):
    """
    Draw a pydot network P that has nested subgraphs.
    """
    draw_pydot(P,**kwds)
    subgraphs=P.get_subgraph_list()
    while subgraphs:
        S=subgraphs.pop()
        draw_pydot(S,**kwds)
        

def mpl_network(ax, node_pos, edge_pos,\
                node_size=300, node_color ='r', node_marker = 'o', \
                node_labels = True,\
                fonts = {}, \
                edge_color ='k', edge_width = 1.0,\
                cmap = None, norm = None, vmin = None, vmax = None,\
                alpha=1.0, digraph=False):

    """
    Draw network with matplotlib using node positions=node_pos
    and edge positions=edge_pos. 

    Steals heavily from matplotlib.axes.scatter.

    """
    if not ax._hold: ax.cla()

    syms =  { # a dict from symbol to (numsides, angle)           
        's' : (4, math.pi/4.0),  # square
        'o' : (20, 0),           # circle
        '^' : (3,0),             # triangle up
        '>' : (3,math.pi/2.0),   # triangle right
        'v' : (3,math.pi),       # triangle down
        '<' : (3,3*math.pi/2.0), # triangle left
        'd' : (4,0),             # diamond
        'p' : (5,0),             # pentagram
        'h' : (6,0),             # hexagon
        '8' : (8,0),             # octogon
        }

    # same marker for all nodes
    if not syms.has_key(node_marker):
        raise NX.NetworkXError('Unknown node marker symbol')
    numsides, rotation = syms[node_marker]

    if not cb.iterable(node_size):
        scales = (node_size,)
    else:
        scales=[]
        npk=node_pos.keys()
        npk.sort()
        for n in npk:
            if node_size.has_key(n):
                scales.append(node_size[n])
            else:
                scales.append(300)

    # no nodes!        
    if len(node_pos)<1:
        return

    if not cb.is_string_like(node_color) \
           and cb.iterable(node_color) \
           and len(node_color)==len(node_pos):
        node_colors = None
        node_color_floats=[]
        npk=node_pos.keys()
        npk.sort()
        for n in npk:
            if node_color.has_key(n):
                node_color_floats.append(float(node_color[n]))
            else:
                node_color_floats.append(0.0)
        node_color_floats=asarray(node_color_floats)                
    else:
        node_colors = ( colorConverter.to_rgba(node_color, alpha), )

        
    npk=node_pos.keys()
    npk.sort()
    npos=[tuple(node_pos[v]) for v in npk],
    node_collection = RegularPolyCollection(
        ax.figure.dpi,
        numsides, rotation, scales,
        facecolors = node_colors,
        offsets = npos[0],
        transOffset = ax.transData,             
        )

    node_collection.set_alpha(alpha)

    if node_colors is None:
        if norm is not None: assert(isinstance(norm, normalize))
        if cmap is not None: assert(isinstance(cmap, Colormap))        
        
        node_collection.set_array(node_color_floats)
        node_collection.set_cmap(cmap)
        node_collection.set_norm(norm)            

        if norm is None:
            node_collection.set_clim(vmin, vmax)

    node_collection.set_zorder(2)            

    if not cb.iterable(edge_width):
        lw = (edge_width,)
    else:
        lw = edge_width

    # edge colors specified with floats won't work here
    # since LineCollection doesn't use ScalarMappable.
    # You can use an array of RGBA or text labels
    if not cb.is_string_like(edge_color) \
           and cb.iterable(edge_color) \
           and len(edge_color)==len(edge_pos):
        edge_colors = None
    else:
        edge_colors = ( colorConverter.to_rgba(edge_color, alpha), )

    edge_collection = LineCollection(edge_pos,
                                colors       = edge_colors,
                                linewidths   = lw,
                                antialiaseds = (1,),
                                transOffset = ax.transData,             
                                )


    if edge_colors is None:
        if norm is not None: assert(isinstance(norm, normalize))
        if cmap is not None: assert(isinstance(cmap, Colormap))        

        #edge_collection.set_array(edge_color)
        #edge_collection.set_cmap(cmap)
        #edge_collection.set_norm(norm)            

        #if norm is None:
            #edge_collection.set_clim(vmin, vmax)

    edge_collection.set_zorder(1)            

    if digraph:
        # a directed graph hack
        # draw thick line segments at head end of edge
        # waiting for someone else to implement arrows that will work 
        arrow_colors = ( colorConverter.to_rgba('k', alpha), )
        a_pos=[]
        p=0.25 # make head segment 25 percent of edge length
        for src,dst in edge_pos:
            x1,y1=src
            x2,y2=dst
            d=sqrt((x2-x1)**2+(y2-y1)**2)
            if d==0:
                continue
            if x2==x1:
                xa=x2
                ya=(y2-y1)*(1-p)+y1
            if y2==y1:
                ya=y2
                xa=(x2-x1)*(1-p)+x1
            else:
                theta=math.acos((x2-x1)/d)
                xa=math.cos(theta)*d*(1-p)+x1
                theta=math.asin((y2-y1)/d)
                ya=math.sin(theta)*d*(1-p)+y1
                
            a_pos.append(((xa,ya),(x2,y2)))
        arrow_collection = LineCollection(a_pos,
                                colors       = arrow_colors,
                                linewidths   = (4,),
                                antialiaseds = (1,),
                                transOffset = ax.transData,             
                                )
        arrow_collection.set_zorder(1)            
        ax.add_collection(arrow_collection)

    # ignore any dot file bounding box and set limits
    x=[xx for xx,yy in node_pos.values()]
    y=[yy for xx,yy in node_pos.values()]
    minx = min(x)
    maxx = max(x)
    miny = min(y)
    maxy = max(y)
    w = maxx-minx
    h = maxy-miny
    # the pad is a little hack to deal with the fact that we don't
    # want to transform all the symbols whose scales are in points
    # to data coords to get the exact bounding box for efficiency
    # reasons.  It can be done right if this is deemed important
    padx, pady = 0.05*w, 0.05*h
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady) 
    ax.update_datalim(corners)
    ax.autoscale_view()

    # turn of axes ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])

    # add edges and nodes
    ax.add_collection(edge_collection)
    ax.add_collection(node_collection)

    if node_labels:
        # add text in a very pylaby way
        for n in node_pos:
            (x,y)=node_pos[n]
            text(x, y, str(n), fonts, 
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform = ax.transData,
                 )



    return node_collection


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/nx_pylab.txt',package='NX')
    return suite

if __name__ == "__main__":
    import sys
    import unittest

    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
