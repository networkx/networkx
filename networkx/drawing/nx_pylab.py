#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Author: Aric Hagberg (hagberg@lanl.gov)
"""
**********
Matplotlib
**********

Draw networks with matplotlib.

See Also
--------

matplotlib:     http://matplotlib.org/

pygraphviz:     http://pygraphviz.github.io/

"""

import networkx as nx
from networkx.drawing.layout import shell_layout,\
    circular_layout,spectral_layout,spring_layout,random_layout

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
           'draw_shell']

def draw(G, pos=None, ax=None, hold=None, **kwds):
    """Draw the graph G with Matplotlib.

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

    kwds : optional keywords
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

    With pyplot use

    >>> import matplotlib.pyplot as plt
    >>> import networkx as nx
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)  # networkx draw()
    >>> plt.draw()  # pyplot draw()

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html
    """
    try:
        import matplotlib.pyplot as plt
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        cf = plt.gcf()
    else:
        cf = ax.get_figure()
    cf.set_facecolor('w')
    if ax is None:
        if cf._axstack() is None:
            ax = cf.add_axes((0, 0, 1, 1))
        else:
            ax = cf.gca()

    ax.set_aspect('equal')

    if 'with_labels' not in kwds:
        kwds['with_labels'] = 'labels' in kwds
    b = plt.ishold()
    # allow callers to override the hold state by passing hold=True|False
    h = kwds.pop('hold', None)
    if h is not None:
        plt.hold(h)
    try:
        draw_networkx(G, pos=pos, ax=ax, **kwds)
        ax.set_axis_off()
        plt.draw_if_interactive()
    except:
        plt.hold(b)
        raise
    plt.hold(b)

def draw_networkx(G, pos=None, arrows=True, with_labels=True, **kwds):
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

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.

    with_labels :  bool, optional (default=True)
       Set to True to draw labels on the nodes.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    nodelist : list, optional (default G.nodes())
       Draw only specified nodes

    edgelist : list, optional (default=G.edges())
       Draw only specified edges

    node_size : scalar or array, optional (default=3)
       Size of nodes.  If an array is specified it must be the
       same length as nodelist.

    node_color : color string, or array of floats, (default='w')
       Node color. Can be a single color format string,
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string, optional (default='o')
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8'.

    alpha : float, optional (default=1.0)
       The node and edge transparency

    cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of nodes

    vmin,vmax : float, optional (default=None)
       Minimum and maximum for node colormap scaling

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default=0.5)

    width : float, optional (default=1.0)
       Line width of edges

    edge_color : color string, or array of floats (default='k')
       Edge color. Can be a single color format string,
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    edge_cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of edges

    edge_vmin,edge_vmax : floats, optional (default=None)
       Minimum and maximum for edge colormap scaling

    labels : dictionary, optional (default=None)
       Node labels in a dictionary keyed by node of text labels

    font_size : int, optional (default=12)
       Font size for text labels

    font_color : string, optional (default='k' black)
       Font color string

    font_weight : string, optional (default='normal')
       Font weight

    font_family : string, optional (default='sans-serif')
       Font family

    label : string, optional
        Label for graph legend

    Notes
    -----
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.
    Yes, it is ugly but drawing proper arrows with Matplotlib this
    way is tricky.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G)) # use spring layout

    >>> import matplotlib.pyplot as plt
    >>> limits=plt.axis('off') # turn of axis

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if pos is None:
        pos = nx.drawing.spring_layout(G)  # default to spring layout

    node_collection = draw_networkx_nodes(G, pos, **kwds)
    edge_collection = draw_networkx_edges(G, pos, arrows=arrows, **kwds)
    if with_labels:
        draw_networkx_labels(G, pos, **kwds)
    plt.draw_if_interactive()

def draw_networkx_nodes(G, pos,
                        nodelist=None,
                        node_size=3.,
                        node_color='w',
                        node_edge_color='k',
                        node_shape='o',
                        alpha=1.0,
                        cmap=None,
                        vmin=None,
                        vmax=None,
                        ax=None,
                        linewidth=0.5,
                        label=None,
                        **kwds):
    """Draw the nodes of the graph G.

    This draws only the nodes of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    nodelist : list, optional
       Draw only specified nodes (default G.nodes())

    node_size : scalar or array
       Size (radius) of nodes (default=3.0).
       If an array is specified it must be the same length as nodelist.

    node_color : color string, or array of floats
       Node color. Can be a single color format string (default='w'),
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.

    node_edge_color : color string, or array of floats
       Node color. Can be a single color format string (default='k'),
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.

    node_shape : string
       The shape of the node. Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8' (default='o').

    alpha : float
       The node transparency (default=1.0)

    cmap : Matplotlib colormap
       Colormap for mapping intensities of nodes (default=None)

    vmin, vmax : floats
       Minimum and maximum for node colormap scaling (default=None)

    linewidth : [scalar | sequence]
       Line width of symbol border (default=0.5)

    label : [None| string] (TODO: currently ignored)
       Label for legend

    Returns
    -------
        list of (node edge artist, node artist) tuples,
        where both artists are instances of matplotlib.patches

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nodes=nx.draw_networkx_nodes(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    import collections
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if nodelist is None:
        nodelist = list(G)

    if not nodelist or len(nodelist) == 0:  # empty nodelist, no drawing
        return None

    try:
        positions = numpy.asarray([pos[v] for v in nodelist])
    except KeyError as e:
        raise nx.NetworkXError('Node %s has no position.'%e)
    except ValueError:
        raise nx.NetworkXError('Bad value in node positions.')

    node_color = _handle_colors(node_color, alpha, nodelist, cmap, vmin, vmax)
    node_edge_color = _handle_colors(node_edge_color, alpha, nodelist, cmap, vmin, vmax)

    if isinstance(node_size, (int, float)):
        node_size = node_size * numpy.ones((G.number_of_nodes()), dtype=numpy.float)
    if isinstance(linewidth, (int, float)):
        linewidth = linewidth * numpy.ones((G.number_of_nodes()), dtype=numpy.float)

    # rescale
    node_size *= 1e-2
    linewidth *= 1e-2

    # circles made with plt.scatter / networkx.draw_nodes scale with axis dimensions
    # which in practice makes it hard to have one consistent layout
    # -> use patches.Circle instead which creates circles that are in data coordinates
    artists = []
    for ii, node_id in enumerate(nodelist):
        # simulate node edge by drawing a slightly larger circle;
        # I wish there was a better way to do this,
        # but this seems to be the only way to guarantee constant proportions,
        # as linewidth argument in matplotlib.patches will not be proportional
        # to radius as it is in axis coordinates
        node_edge_artist = _get_node_artist(shape=node_shape,
                                            position=positions[ii],
                                            size=node_size[ii],
                                            facecolor=node_edge_color[ii],
                                            zorder=2)
        ax.add_artist(node_edge_artist)

        # draw node
        node_artist = _get_node_artist(shape=node_shape,
                                       position=positions[ii],
                                       size=node_size[ii] -linewidth[ii],
                                       facecolor=node_color[ii],
                                       zorder=3)
        ax.add_artist(node_artist)
        artists.append((node_artist, node_edge_artist))

    # pad x and y limits as patches are not registered properly
    # when matplotlib sets axis limits automatically
    maxs = numpy.max(node_size)
    maxx = numpy.amax(positions[:,0])
    minx = numpy.amin(positions[:,0])
    maxy = numpy.amax(positions[:,1])
    miny = numpy.amin(positions[:,1])

    w = maxx-minx
    h = maxy-miny
    padx, pady = 0.05*w + maxs, 0.05*h + maxs
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
    ax.update_datalim(corners)
    ax.autoscale_view()

    return artists


def _get_node_artist(shape, position, size, facecolor, zorder=2):
    import numpy
    import matplotlib
    if shape == 'o': # circle
        artist = matplotlib.patches.Circle(xy=position,
                                           radius=size,
                                           facecolor=facecolor,
                                           linewidth=0.,
                                           zorder=zorder)
    elif shape == '^': # triangle up
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=3,
                                                   facecolor=facecolor,
                                                   orientation=0,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == '<': # triangle left
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=3,
                                                   facecolor=facecolor,
                                                   orientation=numpy.pi*0.5,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == 'v': # triangle down
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=3,
                                                   facecolor=facecolor,
                                                   orientation=numpy.pi,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == '>': # triangle right
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=3,
                                                   facecolor=facecolor,
                                                   orientation=numpy.pi*1.5,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == 's': # square
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=4,
                                                   facecolor=facecolor,
                                                   orientation=numpy.pi*0.25,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == 'd': # diamond
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=4,
                                                   facecolor=facecolor,
                                                   orientation=numpy.pi*0.5,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == 'p': # pentagon
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=5,
                                                   facecolor=facecolor,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == 'h': # hexagon
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=6,
                                                   facecolor=facecolor,
                                                   linewidth=0.,
                                                   zorder=zorder)
    elif shape == 8: # octagon
        artist = matplotlib.patches.RegularPolygon(xy=position,
                                                   radius=size,
                                                   numVertices=8,
                                                   facecolor=facecolor,
                                                   linewidth=0.,
                                                   zorder=zorder)
    else:
        raise ValueError("Node shape one of: ''so^>v<dph8'. Current shape:{}".format(shape))

    return artist


def draw_networkx_edges(G, pos,
                        edgelist=None,
                        width=1.,
                        edge_color='k',
                        alpha=1.,
                        edge_cmap=None,
                        edge_vmin=None,
                        edge_vmax=None,
                        ax=None,
                        arrows=True,
                        label=None,
                        node_size=0.,
                        **kwds):
    """Draw the edges of the graph G.

    This draws only the edges of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    edgelist : collection of edge tuples
       Draw only specified edges(default=G.edges())

    width : float, or array of floats
       Line width of edges (default=1.0)

    edge_color : color string, or array of floats
       Edge color. Can be a single color format string (default='r'),
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    alpha : float
       The edge transparency (default=1.0)

    edge_cmap : Matplotlib colormap
       Colormap for mapping intensities of edges (default=None)

    edge_vmin, edge_vmax : floats
       Minimum and maximum for edge colormap scaling (default=None)

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.

    label : [None| string]
       Label for legend

    node_size: float, or array of floats (default=0.0)
       'Size' of nodes (radius/greatest distance of node edge to node centre);
       used to offset arrow heads such that they are not occluded.
       If draw_networkx_nodes() is called independently, node_size should be set
       to the same value (draw_networkx_nodes() default=3.0).

    Returns
    -------
        list of matplotlib.patches.FancyArrow artists

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edges=nx.draw_networkx_edges(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

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
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
        from matplotlib.colors import colorConverter, Colormap
        from matplotlib.collections import LineCollection
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if edgelist is None:
        edgelist = list(G.edges())

    if not edgelist or len(edgelist) == 0:  # no edges!
        return None

    if isinstance(node_size, (int, float)):
        node_size = node_size * numpy.ones((G.number_of_nodes()))
    if isinstance(width, (int, float)):
        width = width * numpy.ones((len(edgelist)))

    # rescale -- all sizes are in axes coordinate units and hence small
    node_size *= 1e-2
    width *= 1e-2

    # convert node size to dictionary -> zero-indexing of nodes not guaranteed
    nodelist = list(G)
    node_size = dict([(node_id, node_size[ii]) for ii, node_id in enumerate(nodelist)])

    edge_color = _handle_colors(edge_color,
                               alpha,
                               edgelist,
                               cmap=edge_cmap,
                               vmin=edge_vmin,
                               vmax=edge_vmax)

    # construct a more useful edge list
    total_edges = len(edgelist)
    edges = numpy.zeros((total_edges, 9))
    for ii, (source, target) in enumerate(edgelist):
        x1, y1 = pos[source]
        x2, y2 = pos[target]
        dx = x2-x1
        dy = y2-y1
        w = width[ii]
        edges[ii] = source, target, x1, y1, x2, y2, dx, dy, w

    artists = []
    for ii, (edge, color) in enumerate(zip(edges, edge_color)):
        source, target, x1, y1, x2, y2, dx, dy, w = edge
        bidirectional = (target, source) in edgelist

        if arrows and bidirectional:
            # shift edge to the right (looking along the arrow)
            x1, y1, x2, y2 = _shift_edge(x1, y1, x2, y2, delta=0.5*w)
            # plot half arrow
            patch = _arrow(ax,
                           x1, y1, dx, dy,
                           offset=node_size[target],
                           facecolor=color,
                           width=w,
                           head_length=2*w,
                           head_width=3*w,
                           length_includes_head=True,
                           zorder=1,
                           # edgecolor='none',
                           linewidth=0.1,
                           shape='right',
                           )

        elif arrows and not bidirectional:
            # don't shift edge, plot full arrow
            patch = _arrow(ax,
                           x1, y1, dx, dy,
                           offset=node_size[target],
                           facecolor=color,
                           width=w,
                           head_length=2*w,
                           head_width=3*w,
                           length_includes_head=True,
                           # edgecolor='none',
                           linewidth=0.1,
                           zorder=1,
                           shape='full',
                           )

        else: # i.e. undirected
            patch = _line(ax,
                          x1, y1, dx, dy,
                          facecolor=color,
                          width=w,
                          head_length=1e-10, # 0 throws error
                          head_width=1e-10, # 0 throws error
                          length_includes_head=False,
                          # edgecolor='none',
                          linewidth=0.1,
                          zorder=1,
                          shape='full',
                          )

        artists.append(patch)
        ax.add_artist(patch)

    # update view
    unique_nodes = numpy.unique(numpy.array(edgelist))
    positions = numpy.array([pos[ii] for ii in unique_nodes])
    maxx = numpy.amax(positions[:,0])
    minx = numpy.amin(positions[:,0])
    maxy = numpy.amax(positions[:,1])
    miny = numpy.amin(positions[:,1])

    w = maxx-minx
    h = maxy-miny
    padx, pady = 0.05*w, 0.05*h
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
    ax.update_datalim(corners)
    ax.autoscale_view()

    return artists

def _shift_edge(x1, y1, x2, y2, delta):
    import numpy
    # get orthogonal unit vector
    v = numpy.r_[x2-x1, y2-y1] # original
    v = numpy.r_[-v[1], v[0]] # orthogonal
    v = v / numpy.linalg.norm(v) # unit

    dx, dy = delta * v
    return x1+dx, y1+dy, x2+dx, y2+dy

def _arrow(ax, x1, y1, dx, dy, offset, **kwargs):
    import numpy
    # offset to prevent occlusion of head from nodes
    r = numpy.sqrt(dx**2 + dy**2)
    dx *= (r-offset)/r
    dy *= (r-offset)/r

    return _line(ax, x1, y1, dx, dy, **kwargs)

def _line(ax, x1, y1, dx, dy, **kwargs):
    import matplotlib
    # use FancyArrow instead of e.g. LineCollection to ensure consistent scaling across elements;
    return matplotlib.patches.FancyArrow(x1, y1, dx, dy, **kwargs)

def draw_networkx_labels(G, pos,
                         labels=None,
                         font_size=12,
                         font_color='k',
                         font_family='sans-serif',
                         font_weight='normal',
                         alpha=1.0,
                         bbox=None,
                         ax=None,
                         **kwds):
    """Draw node labels on the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    labels : dictionary, optional (default=None)
       Node labels in a dictionary keyed by node of text labels

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

    Returns
    -------
    dict
        `dict` of labels keyed on the nodes

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> labels=nx.draw_networkx_labels(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html


    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if labels is None:
        labels = dict((n, n) for n in G.nodes())

    # set optional alignment
    horizontalalignment = kwds.get('horizontalalignment', 'center')
    verticalalignment = kwds.get('verticalalignment', 'center')

    text_items = {}  # there is no text collection so we'll fake one
    for n, label in labels.items():
        (x, y) = pos[n]
        if not cb.is_string_like(label):
            label = str(label)  # this will cause "1" and 1 to be labeled the same
        t = ax.text(x, y,
                  label,
                  size=font_size,
                  color=font_color,
                  family=font_family,
                  weight=font_weight,
                  horizontalalignment=horizontalalignment,
                  verticalalignment=verticalalignment,
                  transform=ax.transData,
                  bbox=bbox,
                  clip_on=True,
                  )
        text_items[n] = t

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

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

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

    Returns
    -------
    dict
        `dict` of labels keyed on the edges

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edge_labels=nx.draw_networkx_edge_labels(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()
    if edge_labels is None:
        labels = dict(((u, v), d) for u, v, d in G.edges(data=True))
    else:
        labels = edge_labels
    text_items = {}
    for (n1, n2), label in labels.items():
        (x1, y1) = pos[n1]
        (x2, y2) = pos[n2]
        (x, y) = (x1 * label_pos + x2 * (1.0 - label_pos),
                  y1 * label_pos + y2 * (1.0 - label_pos))

        if rotate:
            angle = numpy.arctan2(y2-y1, x2-x1)/(2.0*numpy.pi)*360  # degrees
            # make label orientation "right-side-up"
            if angle > 90:
                angle -= 180
            if angle < - 90:
                angle += 180
            # transform data coordinate angle to screen coordinate angle
            xy = numpy.array((x, y))
            trans_angle = ax.transData.transform_angles(numpy.array((angle,)),
                                                        xy.reshape((1, 2)))[0]
        else:
            trans_angle = 0.0
        # use default box of white with white border
        if bbox is None:
            bbox = dict(boxstyle='round',
                        ec=(1.0, 1.0, 1.0),
                        fc=(1.0, 1.0, 1.0),
                        )
        if not cb.is_string_like(label):
            label = str(label)  # this will cause "1" and 1 to be labeled the same

        # set optional alignment
        horizontalalignment = kwds.get('horizontalalignment', 'center')
        verticalalignment = kwds.get('verticalalignment', 'center')

        t = ax.text(x, y,
                    label,
                    size=font_size,
                    color=font_color,
                    family=font_family,
                    weight=font_weight,
                    horizontalalignment=horizontalalignment,
                    verticalalignment=verticalalignment,
                    rotation=trans_angle,
                    transform=ax.transData,
                    bbox=bbox,
                    zorder=1,
                    clip_on=True,
                    )
        text_items[(n1, n2)] = t

    return text_items


def draw_circular(G, **kwargs):
    """Draw the graph G with a circular layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, circular_layout(G), **kwargs)


def draw_random(G, **kwargs):
    """Draw the graph G with a random layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, random_layout(G), **kwargs)


def draw_spectral(G, **kwargs):
    """Draw the graph G with a spectral layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, spectral_layout(G), **kwargs)


def draw_spring(G, **kwargs):
    """Draw the graph G with a spring layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, spring_layout(G), **kwargs)


def draw_shell(G, **kwargs):
    """Draw networkx graph with shell layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    nlist = kwargs.get('nlist', None)
    if nlist is not None:
        del(kwargs['nlist'])
    draw(G, shell_layout(G, nlist=nlist), **kwargs)

def draw_nx(G, pos, **kwds):
    """For backward compatibility; use draw or draw_networkx."""
    draw(G, pos, **kwds)

def _handle_colors(colors, alpha, elem_list, cmap=None, vmin=None, vmax=None):
    import numpy
    rgba_colors = apply_alpha(colors, alpha, elem_list,
                              cmap, vmin, vmax)
    if len(rgba_colors) == 1:
        rgba_colors = numpy.repeat(rgba_colors, len(elem_list), axis=0)
    return rgba_colors

# TODO: fix naming of function -- this function does a hell of a lot more than the name suggests
def apply_alpha(colors, alpha, elem_list, cmap=None, vmin=None, vmax=None):
    """
    Apply an alpha (or list of alphas) to the colors provided.
    If colors are specified as strings, this function converts them to RGBA arrays.

    Parameters
    ----------

    color : color string, or array of floats
       Color of element. Can be a single color format string (default='r'),
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    alpha : float or array of floats
       Alpha values for elements. This can be a single alpha value, in
       which case it will be applied to all the elements of color. Otherwise,
       if it is an array, the elements of alpha will be applied to the colors
       in order (cycling through alpha multiple times if necessary).

    elem_list : array of networkx objects
       The list of elements which are being colored. These could be nodes, edges
       or labels.

    cmap : matplotlib colormap
       Color map for use if colors is a list of floats corresponding to points on
       a color mapping.

    vmin, vmax : float
       Minimum and maximum values for normalizing colors if a color mapping is used.

    Returns
    -------

    rgba_colors : numpy ndarray
        Array containing RGBA format values for each of the node colours.

    """

    import numbers
    import itertools
    import numpy

    try:
        from matplotlib.colors import colorConverter
        import matplotlib.cm as cm
    except ImportError:
        raise ImportError("Matplotlib required for draw()")

    # If we have been provided with a list of numbers as long as elem_list, apply the color mapping.
    if len(colors) == len(elem_list) and isinstance(colors[0], numbers.Number):
        mapper = cm.ScalarMappable(cmap=cmap)
        mapper.set_clim(vmin, vmax)
        rgba_colors = mapper.to_rgba(colors)
    # Otherwise, convert colors to matplotlib's RGB using the colorConverter object.
    # These are converted to numpy ndarrays to be consistent with the to_rgba method of ScalarMappable.
    else:
        try:
            rgba_colors = numpy.array([colorConverter.to_rgba(colors)])
        except ValueError:
            rgba_colors = numpy.array([colorConverter.to_rgba(color) for color in colors])
    # Set the final column of the rgba_colors to have the relevant alpha values.
    try:
        # If alpha is longer than the number of colors, resize to the number of elements.
        # Also, if rgba_colors.size (the number of elements of rgba_colors) is the same as the number of
        # elements, resize the array, to avoid it being interpreted as a colormap by scatter()
        if len(alpha) > len(rgba_colors) or rgba_colors.size == len(elem_list):
            rgba_colors.resize((len(elem_list), 4))
            rgba_colors[1:, 0] = rgba_colors[0, 0]
            rgba_colors[1:, 1] = rgba_colors[0, 1]
            rgba_colors[1:, 2] = rgba_colors[0, 2]
        rgba_colors[:,  3] = list(itertools.islice(itertools.cycle(alpha), len(rgba_colors)))
    except TypeError:
        rgba_colors[:, -1] = alpha

    return rgba_colors

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import matplotlib as mpl
        mpl.use('PS', warn=False)
        import matplotlib.pyplot as plt
    except:
        raise SkipTest("matplotlib not available")
