"""
**********
Matplotlib
**********

Draw networks with matplotlib (pylab).

See Also
--------
matplotlib:     http://matplotlib.sourceforge.net/
pygraphviz:     http://networkx.lanl.gov/pygraphviz/

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['draw',
           'draw_networkx',
           'draw_networkx_nodes',
           'draw_networkx_edges',
           'draw_networkx_labels',
           'draw_networkx_edge_labels',
           'draw_circular',
           'draw_random',
           'draw_spectral',
           'draw_spring',
           'draw_shell',
           'draw_graphviz']


import networkx
from networkx.drawing.layout import shell_layout,\
    circular_layout,spectral_layout,spring_layout,random_layout

def draw(G, pos=None, ax=None, hold=None, **kwds):
    """Draw the graph G with matplotlib (pylab).

    This is a pylab friendly function that will use the
    current pylab figure axes (e.g. subplot).

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    Usage:

    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G))

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
      - `edge_cmap`: colormap for edge intensities (default=None) 
      - `edge_vmin,edge_vmax`: min and max for colormap edge scaling (default=None)
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
    >>> import networkx as nx
    >>> G=nx.dodecahedral_graph()

    and then use

    >>> nx.draw(G)  # networkx draw()

    and
    >>> P.draw()    # pylab draw()

    """
    try:
        import matplotlib.pylab as pylab
    except ImportError:
        raise ImportError, "Matplotlib required for draw()"
    except RuntimeError:
        pass # unable to open display

    if pos is None:
        pos=networkx.drawing.spring_layout(G) # default to spring layout

    cf=pylab.gcf()
    cf.set_facecolor('w')
    if ax is None:
        if cf._axstack() is None:
            ax=cf.add_axes((0,0,1,1))
        else:
            ax=cf.gca()

 # allow callers to override the hold state by passing hold=True|False
    b = pylab.ishold()
    h = kwds.pop('hold', None)
    if h is not None:
        pylab.hold(h)
    try:
        draw_networkx(G,pos,ax=ax,**kwds)
        ax.set_axis_off()
        pylab.draw_if_interactive()
    except:
        pylab.hold(b)
        raise
    pylab.hold(b)
    return


def draw_networkx(G, pos, with_labels=True, **kwds):
    """Draw the graph G with given node positions pos

    Usage:

    >>> G=nx.dodecahedral_graph()
    >>> pos=nx.spring_layout(G)
    >>> nx.draw_networkx(G,pos)

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
    try:
        import matplotlib.pylab as pylab
    except ImportError:
        raise ImportError, "Matplotlib required for draw()"
    except RuntimeError:
        pass # unable to open display

    node_collection=draw_networkx_nodes(G, pos, **kwds)
    edge_collection=draw_networkx_edges(G, pos, **kwds) 
    if with_labels:
        draw_networkx_labels(G, pos, **kwds)
    pylab.draw_if_interactive()

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
                        linewidths=None,
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
    try:
        import matplotlib.pylab as pylab
        import numpy
    except ImportError:
        raise ImportError, "Matplotlib required for draw()"
    except RuntimeError:
        pass # unable to open display

    if ax is None:
        ax=pylab.gca()

    if nodelist is None:
        nodelist=G.nodes()

    if not nodelist or len(nodelist)==0:  # empty nodelist, no drawing
        return None 

    try:
        xy=numpy.asarray([pos[v] for v in nodelist])
    except KeyError,e:
        raise networkx.NetworkXError('Node %s has no position.'%e)
    except ValueError:
        raise networkx.NetworkXError('Bad value in node positions.')


    node_collection=ax.scatter(xy[:,0], xy[:,1],
                               s=node_size,
                               c=node_color,
                               marker=node_shape,
                               cmap=cmap, 
                               vmin=vmin,
                               vmax=vmax,
                               alpha=alpha,
                               linewidths=linewidths)
                               
    pylab.axes(ax)
    pylab.sci(node_collection)
    node_collection.set_zorder(2)            
    return node_collection


def draw_networkx_edges(G, pos,
                        edgelist=None,
                        width=1.0,
                        edge_color='k',
                        style='solid',
                        alpha=None,
                        edge_cmap=None,
                        edge_vmin=None,
                        edge_vmax=None, 
                        ax=None,
                        arrows=True,
                        **kwds):
    """Draw the edges of the graph G

    This draws only the edges of the graph G.

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    edgelist is an optional list of the edges in G to be drawn.
    If provided, only the edges in edgelist will be drawn. 

    edgecolor can be a list of matplotlib color letters such as 'k' or
    'b' that lists the color of each edge; the list must be ordered in
    the same way as the edge list. Alternatively, this list can contain
    numbers and those number are mapped to a color scale using the color
    map edge_cmap.  Finally, it can also be a list of (r,g,b) or (r,g,b,a)
    tuples, in which case these will be used directly to color the edges.  If
    the latter mode is used, you should not provide a value for alpha, as it
    would be applied globally to all lines.
    
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.

    See draw_networkx for the list of other optional parameters.

    """
    try:
        import matplotlib
        import matplotlib.pylab as pylab
        import matplotlib.cbook as cb
        from matplotlib.colors import colorConverter,Colormap
        from matplotlib.collections import LineCollection
        import numpy
    except ImportError:
        raise ImportError, "Matplotlib required for draw()"
    except RuntimeError:
        pass # unable to open display

    if ax is None:
        ax=pylab.gca()

    if edgelist is None:
        edgelist=G.edges()

    if not edgelist or len(edgelist)==0: # no edges!
        return None

    # set edge positions
    edge_pos=numpy.asarray([(pos[e[0]],pos[e[1]]) for e in edgelist])
    
    if not cb.iterable(width):
        lw = (width,)
    else:
        lw = width

    if not cb.is_string_like(edge_color) \
           and cb.iterable(edge_color) \
           and len(edge_color)==len(edge_pos):
        if numpy.alltrue([cb.is_string_like(c) 
                         for c in edge_color]):
            # (should check ALL elements)
            # list of color letters such as ['k','r','k',...]
            edge_colors = tuple([colorConverter.to_rgba(c,alpha) 
                                 for c in edge_color])
        elif numpy.alltrue([not cb.is_string_like(c) 
                           for c in edge_color]):
            # If color specs are given as (rgb) or (rgba) tuples, we're OK
            if numpy.alltrue([cb.iterable(c) and len(c) in (3,4)
                             for c in edge_color]):
                edge_colors = tuple(edge_color)
            else:
                # numbers (which are going to be mapped with a colormap)
                edge_colors = None
        else:
            raise ValueError('edge_color must consist of either color names or numbers')
    else:
        if cb.is_string_like(edge_color) or len(edge_color)==1:
            edge_colors = ( colorConverter.to_rgba(edge_color, alpha), )
        else:
            raise ValueError('edge_color must be a single color or list of exactly m colors where m is the number or edges')

    edge_collection = LineCollection(edge_pos,
                                     colors       = edge_colors,
                                     linewidths   = lw,
                                     antialiaseds = (1,),
                                     linestyle    = style,     
                                     transOffset = ax.transData,             
                                     )


    edge_collection.set_zorder(1) # edges go behind nodes            
    ax.add_collection(edge_collection)

    # Note: there was a bug in mpl regarding the handling of alpha values for
    # each line in a LineCollection.  It was fixed in matplotlib in r7184 and
    # r7189 (June 6 2009).  We should then not set the alpha value globally,
    # since the user can instead provide per-edge alphas now.  Only set it
    # globally if provided as a scalar.
    if cb.is_numlike(alpha):
        edge_collection.set_alpha(alpha)

    # need 0.87.7 or greater for edge colormaps
    mpl_version=matplotlib.__version__
    if mpl_version.endswith('.svn'):
        mpl_version=matplotlib.__version__[0:-4]
    elif mpl_version.endswith('svn'):
        mpl_version=matplotlib.__version__[0:-3]
    elif mpl_version.endswith('pre'):
        mpl_version=matplotlib.__version__[0:-3]
    if map(int,mpl_version.split('.'))>=[0,87,7]:
        if edge_colors is None:
            if edge_cmap is not None: assert(isinstance(edge_cmap, Colormap))
            edge_collection.set_array(numpy.asarray(edge_color))
            edge_collection.set_cmap(edge_cmap)
            if edge_vmin is not None or edge_vmax is not None:
                edge_collection.set_clim(edge_vmin, edge_vmax)
            else:
                edge_collection.autoscale()
            pylab.axes(ax)
            pylab.sci(edge_collection)

#    else:
#        sys.stderr.write(\
#            """matplotlib version >= 0.87.7 required for colormapped edges.
#        (version %s detected)."""%matplotlib.__version__)
#        raise UserWarning(\
#            """matplotlib version >= 0.87.7 required for colormapped edges.
#        (version %s detected)."""%matplotlib.__version__)

    arrow_collection=None

    if G.is_directed() and arrows:

        # a directed graph hack
        # draw thick line segments at head end of edge
        # waiting for someone else to implement arrows that will work 
        arrow_colors = edge_colors
        a_pos=[]
        p=1.0-0.25 # make head segment 25 percent of edge length
        for src,dst in edge_pos:
            x1,y1=src
            x2,y2=dst
            dx=x2-x1 # x offset
            dy=y2-y1 # y offset
            d=numpy.sqrt(float(dx**2+dy**2)) # length of edge
            if d==0: # source and target at same position
                continue
            if dx==0: # vertical edge
                xa=x2
                ya=dy*p+y1
            if dy==0: # horizontal edge
                ya=y2
                xa=dx*p+x1
            else:
                theta=numpy.arctan2(dy,dx)
                xa=p*d*numpy.cos(theta)+x1
                ya=p*d*numpy.sin(theta)+y1
                
            a_pos.append(((xa,ya),(x2,y2)))

        arrow_collection = LineCollection(a_pos,
                                colors       = arrow_colors,
                                linewidths   = [4*ww for ww in lw],
                                antialiaseds = (1,),
                                transOffset = ax.transData,             
                                )
        
        arrow_collection.set_zorder(1) # edges go behind nodes            
        ax.add_collection(arrow_collection)


    # update view        
    minx = numpy.amin(numpy.ravel(edge_pos[:,:,0]))
    maxx = numpy.amax(numpy.ravel(edge_pos[:,:,0]))
    miny = numpy.amin(numpy.ravel(edge_pos[:,:,1]))
    maxy = numpy.amax(numpy.ravel(edge_pos[:,:,1]))

    w = maxx-minx
    h = maxy-miny
    padx, pady = 0.05*w, 0.05*h
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
    ax.update_datalim( corners)
    ax.autoscale_view()

#    if arrow_collection:

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
    
    See draw_networkx for the list of other optional parameters.

    """
    try:
        import matplotlib.pylab as pylab
        import matplotlib.cbook as cb
    except ImportError:
        raise ImportError, "Matplotlib required for draw()"
    except RuntimeError:
        pass # unable to open display

    if ax is None:
        ax=pylab.gca()

    if labels is None:
        labels=dict(zip(G.nodes(),G.nodes()))

    text_items={}  # there is no text collection so we'll fake one        
    for (n,label) in labels.items():
        (x,y)=pos[n]
        if not cb.is_string_like(label):
            label=str(label) # this will cause "1" and 1 to be labeled the same
        t=ax.text(x, y,
                  label,
                  size=font_size,
                  color=font_color,
                  family=font_family,
                  weight=font_weight,
                  horizontalalignment='center',
                  verticalalignment='center',
                  transform = ax.transData,
                  )
        text_items[n]=t

    return text_items

def draw_networkx_edge_labels(G, pos,
                              edge_labels=None,
                              font_size=10,
                              font_color='k',
                              font_family='sans-serif',
                              font_weight='normal',
                              alpha=1.0,
                              bbox=None,
                              ax=None,
                              **kwds):
    """Draw edge labels.

    pos is a dictionary keyed by vertex with a two-tuple
    of x-y positions as the value.
    See networkx.layout for functions that compute node positions.

    labels is an optional dictionary keyed by edge tuple with labels
    as the values.  If provided only labels for the keys in the dictionary
    are drawn.  If not provided the edge data is used as a label.
   
    See draw_networkx for the list of other optional parameters.

    """
    try:
        import matplotlib.pylab as pylab
        import matplotlib.cbook as cb
        import numpy
    except ImportError:
        raise ImportError, "Matplotlib required for draw()"
    except RuntimeError:
        pass # unable to open display

    if ax is None:
        ax=pylab.gca()
    if edge_labels is None:
        labels=dict(zip(G.edges(),[d for u,v,d in G.edges(data=True)]))
    else:
        labels = edge_labels
    text_items={} 
    for ((n1,n2),label) in labels.items():
        (x1,y1)=pos[n1]
        (x2,y2)=pos[n2]
        (x,y) = ((x1+x2)/2, (y1+y2)/2)
        angle=numpy.arctan2(y2-y1,x2-x1)/(2.0*numpy.pi)*360 # degrees
        # make label orientation "right-side-up"
        if angle > 90: 
            angle-=180
        if angle < - 90: 
            angle+=180
        # transform data coordinate angle to screen coordinate angle
        xy=numpy.array((x,y))
        trans_angle=ax.transData.transform_angles(numpy.array((angle,)),
                                                  xy.reshape((1,2)))[0]
        # use default box of white with white border
        if bbox is None:
            bbox = dict(boxstyle='round',
                        ec=(1.0, 1.0, 1.0),
                        fc=(1.0, 1.0, 1.0),
                        )
        if not cb.is_string_like(label):
            label=str(label) # this will cause "1" and 1 to be labeled the same
        t=ax.text(x, y,
                  label,
                  size=font_size,
                  color=font_color,
                  family=font_family,
                  weight=font_weight,
                  horizontalalignment='center',
                  verticalalignment='center',
                  rotation=trans_angle,
                  transform = ax.transData,
                  bbox = bbox,
                  zorder = 1,
                  )
        text_items[(n1,n2)]=t

    return text_items



def draw_circular(G, **kwargs):
    """Draw the graph G with a circular layout"""
    draw(G,circular_layout(G),**kwargs)
    
def draw_random(G, **kwargs):
    """Draw the graph G with a random layout."""
    draw(G,random_layout(G),**kwargs)

def draw_spectral(G, **kwargs):
    """Draw the graph G with a spectral layout."""
    draw(G,spectral_layout(G),**kwargs)

def draw_spring(G, **kwargs):
    """Draw the graph G with a spring layout"""
    draw(G,spring_layout(G),**kwargs)

def draw_shell(G, **kwargs):
    """Draw networkx graph with shell layout"""
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
