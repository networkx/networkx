"""
Draw networks with matplotlib (pylab).

References:
 - matplotlib:     http://matplotlib.sourceforge.net/
 - pygraphviz:     http://networkx.lanl.gov/pygraphviz/

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

import networkx

try:
    import matplotlib.cbook as cb
    from matplotlib.colors import colorConverter
    from matplotlib.collections import LineCollection
    from matplotlib.numerix import sin, cos, pi, sqrt, \
         arctan2, arccos, arcsin
    from matplotlib.numerix.mlab import amin, amax
    from matplotlib.pylab import gca, hold, draw_if_interactive 
except ImportError:
    raise  "Import Error: not able to import matplotlib."

def draw(G, pos=None, with_labels=True, **kwds):
    """Draw the graph G with matplotlib (pylab).

    This is a pylab friendly function that will use the
    current pylab figure axes (e.g. subplot).

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    Usage:

    >>> draw(G)

    >>> pos=graphviz_layout(G)
    >>> draw(G,pos)

    >>> draw(G,pos=spring_layout(G))

    Also see doc/examples/draw_*

    :Parameters:

      - `nodelist`: list of nodes to be drawn (default=G.nodes())
      - `edgelist`: list of edges to be drawn (default=G.edges())
      - `node_size`: scalar or array of the same length as nodelist (default=300)
      - `node_color`: single color string or numeric/numarray array of floats (default='r')
      - `node_shape`: node shape (default='o'), or 'so^>v<dph8' see pylab.scatter
      - `alpha`: transparency (default=1.0) 
      - `cmap`: colormap for mapping intensities (default=None)
      - `vmin,vmax`: min and max for colormap scaling (default=None)
      - `width`: line width of edges (default =1.0)
      - `edge_color`: scalar or array (default='k')
      - `style`: edge linestyle (default='solid') (solid|dashed|dotted,dashdot)
      - `labels`: dictionary keyed by node of text labels (default=None)
      - `font_size`: size for text labels (default=12)
      - `font_color`: (default='k')
      - `font_weight`: (default='normal')
      - `font_family`: (default='sans-serif')
      - `ax`: matplotlib axes instance

    for more see pylab.scatter

    NB: this has the same name as pylab.draw so beware when using

    >>> from networkx import *

    since you will overwrite the pylab.draw function.

    A good alternative is to use

    >>> import pylab as P
    >>> import networkx as NX

    and then use

    >>> NX.draw(G)  # networkx draw()
    and
    >>> P.draw()    # pylab draw()

    """
    if pos is None:
        pos=networkx.drawing.spring_layout(G) # default to spring layout

    ax=gca()
    # allow callers to override the hold state by passing hold=True|False
    b = ax.ishold()
    h = kwds.get('hold', None)
    if h is not None:
        hold(h)
    try:
        draw_networkx(G, pos, ax=ax, with_labels=with_labels, **kwds)
        draw_if_interactive()
        # turn of axes ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])

    except:
        hold(b)
        raise
    hold(b)

def draw_networkx(G, pos, with_labels=True, ax=None, **kwds):
    """Draw the graph G with given node positions pos

    Usage:

    >>> import pylab as P
    >>> ax=P.subplot(111)
    >>> pos=spring_layout(G)
    >>> draw_networkx(G,pos,ax=ax)

    This is same as 'draw' but the node positions *must* be
    specified in the variable pos.
    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    An optional matplotlib axis can be provided through the
    optional keyword ax.

    with_labels contols text labeling of the nodes

    Also see:

    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    """
    if ax is None:
        ax=gca()
    node_collection=draw_networkx_nodes(G, pos, ax=ax, **kwds)
    edge_collection=draw_networkx_edges(G, pos, ax=ax, **kwds) 
    if with_labels:
        draw_networkx_labels(G, pos, ax=ax, **kwds)
    draw_if_interactive()

def draw_networkx_nodes(G, pos,
                        nodelist=None,
                        node_size=300,
                        node_color='r',
                        node_shape='o',
                        alpha=1.0,
                        cmap=None,
                        vmin=None,
                        vmax=None, 
                        ax=None,
                        **kwds):
    """Draw nodes of graph G

    This draws only the nodes of the graph G.

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    nodelist is an optional list of nodes in G to be drawn.
    If provided only the nodes in nodelist will be drawn.
    
    see draw_networkx for the list of other optional parameters.
    """
    if ax is None:
        ax=gca()

    if nodelist is None:
        nodelist=G.nodes()

    x=[pos[v][0] for v in nodelist]
    y=[pos[v][1] for v in nodelist]

    node_collection=ax.scatter(x, y,
                               s=node_size,
                               c=node_color,
                               marker=node_shape,
                               cmap=cmap, 
                               vmin=vmin,
                               vmax=vmax,
                               alpha=alpha)
                               
    node_collection.set_zorder(2)            
    return node_collection


def draw_networkx_edges(G, pos,
                        edgelist=None,
                        width=1.0,
                        edge_color='k',
                        style='solid',
                        alpha=1.0,
                        ax=None,
                        **kwds):
    """Draw the edges of the graph G

    This draws only the edges of the graph G.

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    edgelist is an optional list of the edges in G to be drawn.
    If provided only the edges in edgelist will be drawn. 
    
    see draw_networkx for the list of other optional parameters.
    """
    if ax is None:
        ax=gca()

    if edgelist is None:
        edgelist=G.edges()

    # set edge positions
    head=[]
    tail=[]
    for e in edgelist:
        # edge e can be a 2-tuple (Graph) or a 3-tuple (Xgraph)
        u=e[0]
        v=e[1]
        head.append(pos[u])
        tail.append(pos[v])
    edge_pos=zip(head,tail)

    if not cb.iterable(width):
        lw = (width,)
    else:
        lw = width

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
                                linestyle    = style,     
                                transOffset = ax.transData,             
                                )
    arrow_collection=None

    if G.is_directed():

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
                theta=arccos((x2-x1)/d)
                xa=cos(theta)*d*(1-p)+x1
                theta=arcsin((y2-y1)/d)
                ya=sin(theta)*d*(1-p)+y1
                
            a_pos.append(((xa,ya),(x2,y2)))

        arrow_collection = LineCollection(a_pos,
                                colors       = arrow_colors,
                                linewidths   = (4,),
                                antialiaseds = (1,),
                                transOffset = ax.transData,             
                                )
        
    # update view        
    xx= [x for (x,y) in head+tail]        
    yy= [y for (x,y) in head+tail]        
    minx = amin(xx)
    maxx = amax(xx)
    miny = amin(yy)
    maxy = amax(yy)
    w = maxx-minx
    h = maxy-miny
    padx, pady = 0.05*w, 0.05*h
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
    ax.update_datalim( corners)
    ax.autoscale_view()

    edge_collection.set_zorder(1) # edges go behind nodes            
    ax.add_collection(edge_collection)
    if arrow_collection:
        arrow_collection.set_zorder(1) # edges go behind nodes            
        ax.add_collection(arrow_collection)


    return edge_collection


def draw_networkx_labels(G, pos,
                         labels=None,
                         font_size=12,
                         font_color='k',
                         font_family='sans-serif',
                         font_weight='normal',
                         alpha=1.0,
                         ax=None,
                         **kwds):
    """Draw node labels on the graph G

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    labels is an optional dictionary keyed by vertex with node labels
    as the values.  If provided only labels for the keys in the dictionary
    are drawn.
    
    see draw_networkx for the list of other optional parameters.
    """
    if ax is None:
        ax=gca()

    if labels is None:
        labels=dict(zip(G.nodes(),G.nodes()))

    for n in labels:
        (x,y)=pos[n]
        ax.text(x, y,
                str(labels[n]),
                size=font_size,
                color=font_color,
                family=font_family,
                weight=font_weight,
                horizontalalignment='center',
                verticalalignment='center',
                transform = ax.transData,
                )


def draw_circular(G, **kwargs):
    """Draw the graph G with a circular layout"""
    from networkx.drawing.layout import circular_layout
    draw(G,circular_layout(G),**kwargs)
    
def draw_random(G, **kwargs):
    """Draw the graph G with a random layout."""
    from networkx.drawing.layout import random_layout
    draw(G,random_layout(G),**kwargs)

def draw_spectral(G, **kwargs):
    """Draw the graph G with a spectral layout."""
    from networkx.drawing.layout import spectral_layout
    draw(G,spectral_layout(G),**kwargs)

def draw_spring(G, **kwargs):
    """Draw the graph G with a spring layout"""
    from networkx.drawing.layout import spring_layout
    draw(G,spring_layout(G),**kwargs)

def draw_shell(G, **kwargs):
    """Draw networkx graph with shell layout"""
    from networkx.drawing.layout import shell_layout
    nlist = kwargs.get('nlist', None)
    if nlist != None:        
        del(kwargs['nlist'])
    draw(G,shell_layout(G,nlist=nlist),**kwargs)

def draw_graphviz(G, prog="neato", **kwargs):
    """Draw networkx graph with graphviz layout"""
    pos=networkx.drawing.graphviz_layout(G,prog)
    draw(G,pos,**kwargs)

def draw_nx(G,pos,**kwds):
    """For backward compatibility; use draw or draw_networkx"""
    draw(G,pos,**kwds)



def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/drawing/nx_pylab.txt',\
                                 package='networkx')
    return suite

if __name__ == "__main__":
    import os
    import sys
    import unittest

    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required (%d.%d detected)." \
              %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
