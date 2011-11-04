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
#    Copyright (C) 2004-2010 by 
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


import networkx as nx
from networkx.drawing.layout import shell_layout,\
    circular_layout,spectral_layout,spring_layout,random_layout

def draw(G, pos=None, ax=None, hold=None, **kwds):
    """Draw the graph G with Matplotlib (pylab).

    Draw the graph as a simple representation with no node
    labels or edge labels and using the full Matplotlib figure area
    and no axis labels by default.  See draw_networkx() for more
    full-featured drawing that allows title, axis labels etc.
    
    Parameters
    ----------
    G : graph
       A networkx graph 

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.
       
    ax : Matplotlib Axes object, optional
       Draw the graph in specified Matplotlib axes.  

    hold : bool, optional
       Set the Matplotlib hold state.  If True subsequent draw
       commands will be added to the current axes.

    **kwds : optional keywords
       See networkx.draw_networkx() for a description of optional keywords.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G)) # use spring layout

    See Also
    --------
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()

    Notes
    -----
    This function has the same name as pylab.draw and pyplot.draw
    so beware when using

    >>> from networkx import *

    since you might overwrite the pylab.draw function.

    Good alternatives are:

    With pylab:

    >>> import pylab as P # 
    >>> import networkx as nx
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)  # networkx draw()
    >>> P.draw()    # pylab draw()
    
    With pyplot

    >>> import matplotlib.pyplot as plt
    >>> import networkx as nx
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)  # networkx draw()
    >>> plt.draw()  # pyplot draw()

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html


    """
    try:
        import matplotlib.pylab as pylab
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

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
        draw_networkx(G,pos=pos,ax=ax,**kwds)
        ax.set_axis_off()
        pylab.draw_if_interactive()
    except:
        pylab.hold(b)
        raise
    pylab.hold(b)
    return


def draw_networkx(G, pos=None, with_labels=True, **kwds):
    """Draw the graph G using Matplotlib.

    Draw the graph with Matplotlib with options for node positions,
    labeling, titles, and many other drawing features.
    See draw() for simple drawing without labels or axes.
    
    Parameters
    ----------
    G : graph
       A networkx graph 

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.
       
    with_labels :  bool, optional (default=True)
       Set to True to draw labels on the nodes.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.  

    nodelist : list, optional (default G.nodes())
       Draw only specified nodes 

    edgelist : list, optional (default=G.edges())
       Draw only specified edges

    node_size : scalar or array, optional (default=300)
       Size of nodes.  If an array is specified it must be the
       same length as nodelist. 

    node_color : color string, or array of floats, (default='r')
       Node color. Can be a single color format string,
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string, optional (default='o')
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8'.

    alpha : float, optional (default=1.0)
       The node transparency

    cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of nodes

    vmin,vmax : float, optional (default=None)
       Minimum and maximum for node colormap scaling

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)

    width : float, optional (default=1.0)
       Line width of edges

    edge_color : color string, or array of floats (default='r')
       Edge color. Can be a single color format string,
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    edge_ cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of edges

    edge_vmin,edge_vmax : floats, optional (default=None)
       Minimum and maximum for edge colormap scaling

    style : string, optional (deafult='solid')
       Edge line style (solid|dashed|dotted,dashdot)

    labels : dictionary, optional (deafult=None)
       Node labels in a dictionary keyed by node of text labels

    font_size : int, optional (default=12)
       Font size for text labels

    font_color : string, optional (default='k' black)
       Font color string 

    font_weight : string, optional (default='normal')
       Font weight 

    font_family : string, optional (default='sans-serif')
       Font family 

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G)) # use spring layout

    >>> import pylab
    >>> limits=pylab.axis('off') # turn of axis 

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html

    See Also
    --------
    draw()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()

    """
    try:
        import matplotlib.pylab as pylab
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if pos is None:
        pos=nx.drawing.spring_layout(G) # default to spring layout

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
    """Draw the nodes of the graph G.

    This draws only the nodes of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph 

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.
       
    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.  

    nodelist : list, optional
       Draw only specified nodes (default G.nodes())

    node_size : scalar or array
       Size of nodes (default=300).  If an array is specified it must be the
       same length as nodelist. 

    node_color : color string, or array of floats
       Node color. Can be a single color format string (default='r'),
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8' (default='o').

    alpha : float
       The node transparency (default=1.0) 

    cmap : Matplotlib colormap
       Colormap for mapping intensities of nodes (default=None)

    vmin,vmax : floats
       Minimum and maximum for node colormap scaling (default=None)

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nodes=nx.draw_networkx_nodes(G,pos=nx.spring_layout(G)) 

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()



    """
    try:
        import matplotlib.pylab as pylab
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise


    if ax is None:
        ax=pylab.gca()

    if nodelist is None:
        nodelist=G.nodes()

    if not nodelist or len(nodelist)==0:  # empty nodelist, no drawing
        return None 

    try:
        xy=numpy.asarray([pos[v] for v in nodelist])
    except KeyError as e:
        raise nx.NetworkXError('Node %s has no position.'%e)
    except ValueError:
        raise nx.NetworkXError('Bad value in node positions.')



    node_collection=ax.scatter(xy[:,0], xy[:,1],
                               s=node_size,
                               c=node_color,
                               marker=node_shape,
                               cmap=cmap, 
                               vmin=vmin,
                               vmax=vmax,
                               alpha=alpha,
                               linewidths=linewidths)
                               
#    pylab.axes(ax)
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
    """Draw the edges of the graph G.

    This draws only the edges of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph 

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.
       
    edgelist : collection of edge tuples
       Draw only specified edges(default=G.edges())

    width : float
       Line width of edges (default =1.0)

    edge_color : color string, or array of floats
       Edge color. Can be a single color format string (default='r'),
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    style : string
       Edge line style (default='solid') (solid|dashed|dotted,dashdot)

    alpha : float
       The edge transparency (default=1.0) 

    edge_ cmap : Matplotlib colormap
       Colormap for mapping intensities of edges (default=None)

    edge_vmin,edge_vmax : floats
       Minimum and maximum for edge colormap scaling (default=None)

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.  

    arrows : bool, optional (default=True) 
       For directed graphs, if True draw arrowheads.

    Notes
    -----
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.
    Yes, it is ugly but drawing proper arrows with Matplotlib this
    way is tricky.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edges=nx.draw_networkx_edges(G,pos=nx.spring_layout(G)) 

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_labels()
    draw_networkx_edge_labels()

    """
    try:
        import matplotlib
        import matplotlib.pylab as pylab
        import matplotlib.cbook as cb
        from matplotlib.colors import colorConverter,Colormap
        from matplotlib.collections import LineCollection
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

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

    if edge_colors is None:
        if edge_cmap is not None: 
            assert(isinstance(edge_cmap, Colormap))
        edge_collection.set_array(numpy.asarray(edge_color))
        edge_collection.set_cmap(edge_cmap)
        if edge_vmin is not None or edge_vmax is not None:
            edge_collection.set_clim(edge_vmin, edge_vmax)
        else:
            edge_collection.autoscale()
        pylab.sci(edge_collection)

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
    """Draw node labels on the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph 

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.
       
    font_size : int
       Font size for text labels (default=12)

    font_color : string
       Font color string (default='k' black)

    font_family : string
       Font family (default='sans-serif')

    font_weight : string
       Font weight (default='normal')

    alpha : float
       The text transparency (default=1.0) 

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.  


    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> labels=nx.draw_networkx_labels(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html


    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pylab as pylab
        import matplotlib.cbook as cb
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax=pylab.gca()

    if labels is None:
        labels=dict( (n,n) for n in G.nodes())

    # set optional alignment
    horizontalalignment=kwds.get('horizontalalignment','center')
    verticalalignment=kwds.get('verticalalignment','center')

    text_items={}  # there is no text collection so we'll fake one        
    for n, label in labels.items():
        (x,y)=pos[n]
        if not cb.is_string_like(label):
            label=str(label) # this will cause "1" and 1 to be labeled the same
        t=ax.text(x, y,
                  label,
                  size=font_size,
                  color=font_color,
                  family=font_family,
                  weight=font_weight,
                  horizontalalignment=horizontalalignment,
                  verticalalignment=verticalalignment,
                  transform = ax.transData,
                  clip_on=True,
                  )
        text_items[n]=t

    return text_items

def draw_networkx_edge_labels(G, pos,
                              edge_labels=None,
                              label_pos=0.5,
                              font_size=10,
                              font_color='k',
                              font_family='sans-serif',
                              font_weight='normal',
                              alpha=1.0,
                              bbox=None,
                              ax=None,
                              rotate=True,
                              **kwds):
    """Draw edge labels.

    Parameters
    ----------
    G : graph
       A networkx graph 

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.
       
    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.  

    alpha : float
       The text transparency (default=1.0) 

    edge_labels : dictionary
       Edge labels in a dictionary keyed by edge two-tuple of text
       labels (default=None). Only labels for the keys in the dictionary
       are drawn. 

    label_pos : float
       Position of edge label along edge (0=head, 0.5=center, 1=tail)

    font_size : int
       Font size for text labels (default=12)

    font_color : string
       Font color string (default='k' black)

    font_weight : string
       Font weight (default='normal')

    font_family : string
       Font family (default='sans-serif')

    bbox : Matplotlib bbox
       Specify text box shape and colors.

    clip_on : bool
       Turn on clipping at axis boundaries (default=True)

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edge_labels=nx.draw_networkx_edge_labels(G,pos=nx.spring_layout(G)) 

    Also see the NetworkX drawing examples at
    http://networkx.lanl.gov/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()

    """
    try:
        import matplotlib.pylab as pylab
        import matplotlib.cbook as cb
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax=pylab.gca()
    if edge_labels is None:
        labels=dict( ((u,v), d) for u,v,d in G.edges(data=True) )
    else:
        labels = edge_labels
    text_items={} 
    for (n1,n2), label in labels.items():
        (x1,y1)=pos[n1]
        (x2,y2)=pos[n2]
        (x,y) = (x1 * label_pos + x2 * (1.0 - label_pos), 
                 y1 * label_pos + y2 * (1.0 - label_pos)) 

        if rotate: 
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
        else:
            trans_angle=0.0
        # use default box of white with white border
        if bbox is None:
            bbox = dict(boxstyle='round',
                        ec=(1.0, 1.0, 1.0),
                        fc=(1.0, 1.0, 1.0),
                        )
        if not cb.is_string_like(label):
            label=str(label) # this will cause "1" and 1 to be labeled the same

        # set optional alignment
        horizontalalignment=kwds.get('horizontalalignment','center')
        verticalalignment=kwds.get('verticalalignment','center')

        t=ax.text(x, y,
                  label,
                  size=font_size,
                  color=font_color,
                  family=font_family,
                  weight=font_weight,
                  horizontalalignment=horizontalalignment,
                  verticalalignment=verticalalignment,
                  rotation=trans_angle,
                  transform = ax.transData,
                  bbox = bbox,
                  zorder = 1,
                  clip_on=True,
                  )
        text_items[(n1,n2)]=t

    return text_items



def draw_circular(G, **kwargs):
    """Draw the graph G with a circular layout."""
    draw(G,circular_layout(G),**kwargs)
    
def draw_random(G, **kwargs):
    """Draw the graph G with a random layout."""
    draw(G,random_layout(G),**kwargs)

def draw_spectral(G, **kwargs):
    """Draw the graph G with a spectral layout."""
    draw(G,spectral_layout(G),**kwargs)

def draw_spring(G, **kwargs):
    """Draw the graph G with a spring layout."""
    draw(G,spring_layout(G),**kwargs)

def draw_shell(G, **kwargs):
    """Draw networkx graph with shell layout."""
    nlist = kwargs.get('nlist', None)
    if nlist != None:        
        del(kwargs['nlist'])
    draw(G,shell_layout(G,nlist=nlist),**kwargs)

def draw_graphviz(G, prog="neato", **kwargs):
    """Draw networkx graph with graphviz layout."""
    pos=nx.drawing.graphviz_layout(G,prog)
    draw(G,pos,**kwargs)

def draw_nx(G,pos,**kwds):
    """For backward compatibility; use draw or draw_networkx."""
    draw(G,pos,**kwds)

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import matplotlib as mpl
        mpl.use('PS',warn=False)
        import pylab
    except:
        raise SkipTest("matplotlib not available")
