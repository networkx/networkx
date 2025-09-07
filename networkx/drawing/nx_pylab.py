"""
**********
Matplotlib
**********

Draw networks with matplotlib.

Examples
--------
>>> G = nx.complete_graph(5)
>>> nx.draw(G)

See Also
--------
 - :doc:`matplotlib <matplotlib:index>`
 - :func:`matplotlib.pyplot.scatter`
 - :obj:`matplotlib.patches.FancyArrowPatch`
"""

import math
from numbers import Number

import networkx as nx

__all__ = [
    "display",
    "apply_matplotlib_colors",
    "draw",
    "draw_networkx",
    "draw_networkx_nodes",
    "draw_networkx_edges",
    "draw_networkx_labels",
    "draw_networkx_edge_labels",
    "draw_bipartite",
    "draw_circular",
    "draw_kamada_kawai",
    "draw_random",
    "draw_spectral",
    "draw_spring",
    "draw_planar",
    "draw_shell",
    "draw_forceatlas2",
]


def apply_matplotlib_colors(
    G, src_attr, dest_attr, map, vmin=None, vmax=None, nodes=True
):
    """
    Apply colors from a matplotlib colormap to a graph.

    Reads values from the `src_attr` and use a matplotlib colormap
    to produce a color. Write the color to `dest_attr`.

    Parameters
    ----------
    G : nx.Graph
        The graph to read and compute colors for.

    src_attr : str or other attribute name
        The name of the attribute to read from the graph.

    dest_attr : str or other attribute name or None
        The name of the attribute to write to on the graph.
        If None, return color map as a dict from node name to color.

    map : matplotlib.colormap
        The matplotlib colormap to use.

    vmin : float, default None
        The minimum value for scaling the colormap. If `None`, find the
        minimum value of `src_attr`.

    vmax : float, default None
        The maximum value for scaling the colormap. If `None`, find the
        maximum value of `src_attr`.

    nodes : bool, default True
        Whether the attribute names are edge attributes or node attributes.
    """
    import matplotlib as mpl

    if nodes:
        type_iter = G.nodes()
    elif G.is_multigraph():
        type_iter = G.edges(keys=True)
    else:
        type_iter = G.edges()

    if vmin is None or vmax is None:
        vals = [type_iter[a][src_attr] for a in type_iter]
        if vmin is None:
            vmin = min(vals)
        if vmax is None:
            vmax = max(vals)

    mapper = mpl.cm.ScalarMappable(cmap=map)
    mapper.set_clim(vmin, vmax)

    def do_map(x):
        # Cast numpy scalars to float
        return tuple(float(x) for x in mapper.to_rgba(x))

    if nodes:
        c_map = {n: do_map(G.nodes[n][src_attr]) for n in G.nodes()}
        if dest_attr is not None:
            nx.set_node_attributes(G, c_map, dest_attr)
        else:
            return c_map
    else:
        c_map = {e: do_map(G.edges[e][src_attr]) for e in type_iter}
        if dest_attr is not None:
            nx.set_edge_attributes(G, c_map, dest_attr)
        else:
            return c_map


class CurvedArrowTextBase:
    def __init__(
        self,
        arrow,
        *args,
        label_pos=0.5,
        labels_horizontal=False,
        ax=None,
        **kwargs,
    ):
        # Bind to FancyArrowPatch
        self.arrow = arrow
        # how far along the text should be on the curve,
        # 0 is at start, 1 is at end etc.
        self.label_pos = label_pos
        self.labels_horizontal = labels_horizontal
        if ax is None:
            ax = plt.gca()
        self.ax = ax
        self.x, self.y, self.angle = self._update_text_pos_angle(arrow)

        # Create text object
        super().__init__(self.x, self.y, *args, rotation=self.angle, **kwargs)
        # Bind to axis
        self.ax.add_artist(self)

    def _get_arrow_path_disp(self, arrow):
        """
        This is part of FancyArrowPatch._get_path_in_displaycoord
        It omits the second part of the method where path is converted
            to polygon based on width
        The transform is taken from ax, not the object, as the object
            has not been added yet, and doesn't have transform
        """
        dpi_cor = arrow._dpi_cor
        trans_data = self.ax.transData
        if arrow._posA_posB is None:
            raise ValueError(
                "Can only draw labels for fancy arrows with "
                "posA and posB inputs, not custom path"
            )
        posA = arrow._convert_xy_units(arrow._posA_posB[0])
        posB = arrow._convert_xy_units(arrow._posA_posB[1])
        (posA, posB) = trans_data.transform((posA, posB))
        _path = arrow.get_connectionstyle()(
            posA,
            posB,
            patchA=arrow.patchA,
            patchB=arrow.patchB,
            shrinkA=arrow.shrinkA * dpi_cor,
            shrinkB=arrow.shrinkB * dpi_cor,
        )
        # Return is in display coordinates
        return _path

    def _update_text_pos_angle(self, arrow):
        # Fractional label position
        # Text position at a proportion t along the line in display coords
        # default is 0.5 so text appears at the halfway point
        import matplotlib as mpl
        import numpy as np

        t = self.label_pos
        tt = 1 - t
        path_disp = self._get_arrow_path_disp(arrow)
        conn = arrow.get_connectionstyle()
        # 1. Calculate x and y
        points = path_disp.vertices
        if is_curve := isinstance(
            conn,
            mpl.patches.ConnectionStyle.Angle3 | mpl.patches.ConnectionStyle.Arc3,
        ):
            # Arc3 or Angle3 type Connection Styles - Bezier curve
            (x1, y1), (cx, cy), (x2, y2) = points
            x = tt**2 * x1 + 2 * t * tt * cx + t**2 * x2
            y = tt**2 * y1 + 2 * t * tt * cy + t**2 * y2
        else:
            if not isinstance(
                conn,
                mpl.patches.ConnectionStyle.Angle
                | mpl.patches.ConnectionStyle.Arc
                | mpl.patches.ConnectionStyle.Bar,
            ):
                msg = f"invalid connection style: {type(conn)}"
                raise TypeError(msg)
            # A. Collect lines
            codes = path_disp.codes
            lines = [
                points[i - 1 : i + 1]
                for i in range(1, len(points))
                if codes[i] == mpl.path.Path.LINETO
            ]
            # B. If more than one line, find the right one and position in it
            if (nlines := len(lines)) != 1:
                dists = [math.dist(*line) for line in lines]
                dist_tot = sum(dists)
                cdist = 0
                last_cut = 0
                i_last = nlines - 1
                for i, dist in enumerate(dists):
                    cdist += dist
                    cut = cdist / dist_tot
                    if i == i_last or t < cut:
                        t = (t - last_cut) / (dist / dist_tot)
                        tt = 1 - t
                        lines = [lines[i]]
                        break
                    last_cut = cut
            [[(cx1, cy1), (cx2, cy2)]] = lines
            x = cx1 * tt + cx2 * t
            y = cy1 * tt + cy2 * t

        # 2. Calculate Angle
        if self.labels_horizontal:
            # Horizontal text labels
            angle = 0
        else:
            # Labels parallel to curve
            if is_curve:
                change_x = 2 * tt * (cx - x1) + 2 * t * (x2 - cx)
                change_y = 2 * tt * (cy - y1) + 2 * t * (y2 - cy)
            else:
                change_x = (cx2 - cx1) / 2
                change_y = (cy2 - cy1) / 2
            angle = np.arctan2(change_y, change_x) / (2 * np.pi) * 360
            # Text is "right way up"
            if angle > 90:
                angle -= 180
            elif angle < -90:
                angle += 180
        (x, y) = self.ax.transData.inverted().transform((x, y))
        return x, y, angle

    def draw(self, renderer):
        # recalculate the text position and angle
        self.x, self.y, self.angle = self._update_text_pos_angle(self.arrow)
        self.set_position((self.x, self.y))
        self.set_rotation(self.angle)
        # redraw text
        super().draw(renderer)


def display(
    G,
    canvas=None,
    **kwargs,
):
    """Draw the graph G.

    Draw the graph as a collection of nodes connected by edges.
    The exact details of what the graph looks like are controlled by the below
    attributes. All nodes and nodes at the end of visible edges must have a
    position set, but nearly all other node and edge attributes are options and
    nodes or edges missing the attribute will use the default listed below. A more
    complete description of each parameter is given below this summary.

    .. list-table:: Default Visualization Attributes
        :widths: 25 25 50
        :header-rows: 1

        * - Parameter
          - Default Attribute
          - Default Value
        * - node_pos
          - `"pos"`
          - If there is not position, a layout will be calculated with `nx.spring_layout`.
        * - node_visible
          - `"visible"`
          - True
        * - node_color
          - `"color"`
          - #1f78b4
        * - node_size
          - `"size"`
          - 300
        * - node_label
          - `"label"`
          - Dict describing the node label. Defaults create a black text with
            the node name as the label. The dict respects these keys and defaults:

            * size : 12
            * color : black
            * family : sans serif
            * weight : normal
            * alpha : 1.0
            * h_align : center
            * v_align : center
            * bbox : Dict describing a `matplotlib.patches.FancyBboxPatch`.
              Default is None.

        * - node_shape
          - `"shape"`
          - "o"
        * - node_alpha
          - `"alpha"`
          - 1.0
        * - node_border_width
          - `"border_width"`
          - 1.0
        * - node_border_color
          - `"border_color"`
          - Matching node_color
        * - edge_visible
          - `"visible"`
          - True
        * - edge_width
          - `"width"`
          - 1.0
        * - edge_color
          - `"color"`
          - Black (#000000)
        * - edge_label
          - `"label"`
          - Dict describing the edge label. Defaults create black text with a
            white bounding box. The dictionary respects these keys and defaults:

            * size : 12
            * color : black
            * family : sans serif
            * weight : normal
            * alpha : 1.0
            * bbox : Dict describing a `matplotlib.patches.FancyBboxPatch`.
              Default {"boxstyle": "round", "ec": (1.0, 1.0, 1.0), "fc": (1.0, 1.0, 1.0)}
            * h_align : "center"
            * v_align : "center"
            * pos : 0.5
            * rotate : True

        * - edge_style
          - `"style"`
          - "-"
        * - edge_alpha
          - `"alpha"`
          - 1.0
        * - edge_arrowstyle
          - `"arrowstyle"`
          - ``"-|>"`` if `G` is directed else ``"-"``
        * - edge_arrowsize
          - `"arrowsize"`
          - 10 if `G` is directed else 0
        * - edge_curvature
          - `"curvature"`
          - arc3
        * - edge_source_margin
          - `"source_margin"`
          - 0
        * - edge_target_margin
          - `"target_margin"`
          - 0

    Parameters
    ----------
    G : graph
        A networkx graph

    canvas : Matplotlib Axes object, optional
        Draw the graph in specified Matplotlib axes

    node_pos : string or function or dict, default "pos"
        A string naming the node attribute storing the position of nodes as a tuple.
        Or a function to be called with input `G` which returns the layout as a dict keyed
        by node to position tuple like the NetworkX layout functions. Or a dict keyed from
        node to position tuple.
        If no nodes in the graph has the attribute, a spring layout is calculated.

    node_visible : string or bool or dict, default visible
        A string naming the node attribute which stores if a node should be drawn.
        If `True`, all nodes will be visible while if `False` no nodes will be visible.
        If incomplete, nodes missing this attribute will be shown by default.
        If a dict, keys should be nodes and the values a boolean.

    node_color : string or dict, default "color"
        A string naming the node attribute which stores the color of each node or
        a dict from nodes to the color, which can be a hexadecimal string, rgb or
        rbga tuple.
        Visible nodes without this attribute will use '#1f78b4' as a default.

    node_size : string or number or dict, default "size"
        A string naming the node attribute which stores the size of each node or
        dict from nodes to sizes.
        Visible nodes without this attribute will use a default size of 300.

    node_label : string or bool or dict, default "label"
        A string naming the node attribute which stores the label of each node.
        The attribute value can be a string, False (no label for that node),
        True (the node is the label) or a dict keyed by node to the label.

        If a dict is specified, these keys are read to further control the label:

        * label : The text of the label; default: name of the node
        * size : Font size of the label; default: 12
        * color : Font color of the label; default: black
        * family : Font family of the label; default: "sans-serif"
        * weight : Font weight of the label; default: "normal"
        * alpha : Alpha value of the label; default: 1.0
        * h_align : The horizontal alignment of the label.
            one of "left", "center", "right"; default: "center"
        * v_align : The vertical alignment of the label.
            one of "top", "center", "bottom"; default: "center"
        * bbox : A dict of parameters for `matplotlib.patches.FancyBboxPatch`.

        Visible nodes without this attribute will be treated as if the value was True.

    node_shape : string or dict, default "shape"
        A string naming the node attribute which stores the label of each node or a dict
        from node to a matplotlib shape.
        The values of this attribute are expected to be one of the matplotlib shapes,
        one of 'so^>v<dph8'. Visible nodes without this attribute will use 'o'.

    node_alpha : string or dict, default "alpha"
        A string naming the node attribute which stores the alpha of each node or a
        dict from node to alpha value.
        The values of this attribute are expected to be floats between 0.0 and 1.0.
        Visible nodes without this attribute will be treated as if the value was 1.0.

    node_border_width : string or dict, default "border_width"
        A string naming the node attribute storing the width of the border of the node
        or a dict from node name to numeric width values.
        The values of this attribute are expected to be numeric. Visible nodes without
        this attribute will use the assumed default of 1.0.

    node_border_color : string or dict, default "border_color"
        A string naming the node attribute which storing the color of the border of the node,
        or a dict from node name to a color.
        Visible nodes missing this attribute will use the final node_color value.

    edge_visible : string or bool or dict, default "visible"
        A string nameing the edge attribute which stores if an edge should be drawn,
        or a dict from node name to a boolean.
        If `True`, all edges will be drawn while if `False` no edges will be visible.
        If incomplete, edges missing this attribute will be shown by default. Values
        of this attribute are expected to be booleans.

    edge_width : string or int or dict, default "width"
        A string nameing the edge attribute which stores the width of each edge, or
        a dict from node name to a numeric width.
        Visible edges without this attribute will use a default width of 1.0.

    edge_color : string or color or dict, default "color"
        A string nameing the edge attribute which stores of color of each edge, or
        dict from node name to a color.
        Visible edges without this attribute will be drawn black. Each color can be
        a string or rgb (or rgba) tuple of floats from 0.0 to 1.0.

    edge_label : string or bool or None, default "label"
        A string naming the edge attribute which stores the label of each edge.
        The values of this attribute can be a string, number or False or None. In
        the latter two cases, no edge label is displayed.

        If a dict is specified, these keys are read to further control the label:

        * label : The text of the label, or the name of an edge attribute holding the label.
        * size : Font size of the label; default: 12
        * color : Font color of the label; default: black
        * family : Font family of the label; default: "sans-serif"
        * weight : Font weight of the label; default: "normal"
        * alpha : Alpha value of the label; default: 1.0
        * h_align : The horizontal alignment of the label.
            one of "left", "center", "right"; default: "center"
        * v_align : The vertical alignment of the label.
            one of "top", "center", "bottom"; default: "center"
        * bbox : A dict of parameters for `matplotlib.patches.FancyBboxPatch`.
        * rotate : Whether to rotate labels to lie parallel to the edge, default: True.
        * pos : A float showing how far along the edge to put the label; default: 0.5.

    edge_style : string or dict, default "style"
        A string naming the edge attribute which stores the style of each edge or
        a dict from node name to a matplotlib edge style.
        Visible edges without this attribute will be drawn solid. Values of this
        attribute can be line styles, e.g. '-', '--', '-.' or ':' or words like 'solid'
        or 'dashed'. If no edge in the graph has this attribute and it is a non-default
        value, assume that it describes the edge style for all edges in the graph.

    edge_alpha : string or float or dict, default "alpha"
        A string naming the edge attribute which stores the alpha value of each edge,
        or dict from node name to alpha values.
        Visible edges without this attribute will use an alpha value of 1.0.

    edge_arrowstyle : string or dict, default "arrowstyle"
        A string naming the edge attribute which stores the type of arrowhead to use for
        each edge, or a dict from node name to arrow style.
        Visible edges without this attribute use ``"-"`` for undirected graphs and ``"-|>"``
        for directed graphs.

        See `matplotlib.patches.ArrowStyle` for more options

    edge_arrowsize : string or int or dict, default "arrowsize"
        A string naming the edge attribute which stores the size of the arrowhead for each
        edge, or a dict from node name to arrow sizes. Visible edges without this attribute
        will use a default value of 10.

    edge_curvature : string or dict, default "curvature"
       A string naming the edge attribute storing the curvature and connection style
       of each edge, or dict from node name to curvature value. Visible edges without this
       attribute will use "arc3" as a default value, resulting an a straight line between
       the two nodes. Curvature can be given as 'arc3,rad=0.2' to specify both the style and
       radius of curvature.

       Please see `matplotlib.patches.ConnectionStyle` and
       `matplotlib.patches.FancyArrowPatch` for more information.

    edge_source_margin : string or int or dict, default "source_margin"
        A string naming the edge attribute which stores the minimum margin (gap) between
        the source node and the start of the edge, or a dict from node name to source margin.
        Visible edges without this attribute will use a default value of 0.

    edge_target_margin : string or int or dict, default "target_margin"
        A string naming the edge attribute which stores the minimumm margin (gap) between
        the target node and the end of the edge, or an int for all nodes, or a dict from
        node name to target margin. Visible edges without this attribute will use a default
        value of 0.

    hide_ticks : bool, default True
        Weather to remove the ticks from the axes of the matplotlib object.

    Raises
    ------
    NetworkXError
        If a node or edge is missing a required parameter such as `pos` or
        if `display` receives an argument not listed above.

    ValueError
        If a node or edge has an invalid color format, i.e. not a color string,
        rgb tuple or rgba tuple.

    Returns
    -------
    The input graph. This is potentially useful for dispatching visualization
    functions.
    """
    from collections import Counter

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    defaults = {
        "node_pos": None,
        "node_visible": True,
        "node_color": "#1f78b4",
        "node_size": 300,
        "node_label": {
            "size": 12,
            "color": "#000000",
            "family": "sans-serif",
            "weight": "normal",
            "alpha": 1.0,
            "h_align": "center",
            "v_align": "center",
            "bbox": None,
        },
        "node_shape": "o",
        "node_alpha": 1.0,
        "node_border_width": 1.0,
        "node_border_color": "face",
        "edge_visible": True,
        "edge_width": 1.0,
        "edge_color": "#000000",
        "edge_label": {
            "size": 12,
            "color": "#000000",
            "family": "sans-serif",
            "weight": "normal",
            "alpha": 1.0,
            "bbox": {"boxstyle": "round", "ec": (1.0, 1.0, 1.0), "fc": (1.0, 1.0, 1.0)},
            "h_align": "center",
            "v_align": "center",
            "pos": 0.5,
            "rotate": True,
        },
        "edge_style": "-",
        "edge_alpha": 1.0,
        "edge_arrowstyle": "-|>" if G.is_directed() else "-",
        "edge_arrowsize": 10 if G.is_directed() else 0,
        "edge_curvature": "arc3",
        "edge_source_margin": 0,
        "edge_target_margin": 0,
        "hide_ticks": True,
    }

    # Allow some undocumented kwargs to allow the old draw API to wrap display
    compat_kwargs = [
        "compat_force_fancy_arrows",
        "compat_return_edge_viz_obj",
        "compat_return_node_label_obj",
        "compat_return_edge_label_obj",
        "compat_edge_label_anyways",
    ]

    # Check arguments
    for kwarg in kwargs:
        if kwarg not in defaults and kwarg not in compat_kwargs:
            raise nx.NetworkXError(
                f"Unrecognized visualization keyword argument: {kwarg}"
            )

    if canvas is None:
        canvas = plt.gca()

    if kwargs.get("hide_ticks", defaults["hide_ticks"]):
        canvas.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )

    ### Helper methods and classes

    def node_property_sequence(seq, attr_name):
        """Return a list of attribute values for `seq`, using a default if needed"""

        # All node attribute parameters start with "node_"
        param_name = f"node_{attr_name}"
        default = defaults[param_name]
        attr = kwargs.get(param_name, attr_name)

        def get_attr(n):
            if isinstance(attr, dict):
                return attr.get(n, default)
            else:
                return node_subgraph.nodes[n].get(attr, default)

        def check_attr(n):
            if isinstance(attr, dict):
                return n in attr
            else:
                return attr in node_subgraph.nodes[n]

        if default is None:
            # raise instead of using non-existant default value
            for n in seq:
                if not check_attr(n):
                    raise nx.NetworkXError(
                        f"Attribute '{attr_name}' missing for node {n}"
                    )

        # If `attr` is not a graph attr and was explicitly passed as an argument
        # it must be a user-default value. Allow attr=None to tell draw to skip
        # attributes which are on the graph
        if (
            attr is not None
            and not isinstance(attr, dict)
            and nx.get_node_attributes(node_subgraph, attr) == {}
            and any(attr == v for k, v in kwargs.items() if "node" in k)
        ):
            return [attr for _ in seq]

        return [get_attr(n) for n in seq]

    def compute_colors(color, alpha):
        if isinstance(color, str):
            rgba = mpl.colors.colorConverter.to_rgba(color)
            # Using a non-default alpha value overrides any alpha value in the color
            if alpha != defaults["node_alpha"]:
                return (rgba[0], rgba[1], rgba[2], alpha)
            return rgba

        if isinstance(color, tuple | np.ndarray) and len(color) == 3:
            return (color[0], color[1], color[2], alpha)

        if isinstance(color, tuple | np.ndarray) and len(color) == 4:
            return color

        raise ValueError(f"Invalid format for color: {color}")

    # Find which edges can be plotted as a line collection
    #
    # Non-default values for these attributes require fancy arrow patches:
    # - any arrow style (including the default -|> for directed graphs)
    # - arrow size (by extension of style)
    # - connection style
    # - min_source_margin
    # - min_target_margin

    def collection_compatible(e):
        if "compat_force_fancy_arrows" in kwargs:
            return e[0] != e[1] and not kwargs["compat_force_fancy_arrows"]
        else:
            return (
                # Edge can be plotted with LineCollection since it has compatible characteristics
                get_edge_attr(e, "arrowstyle") == "-"
                and get_edge_attr(e, "curvature") == "arc3"
                and get_edge_attr(e, "source_margin") == 0
                and get_edge_attr(e, "target_margin") == 0
                # self-loops ALWAYS get a fancy arrow
                and e[0] != e[1]
            )

    def edge_property_sequence(seq, attr_name):
        """Return a list of attribute values for `seq`, using a default if needed"""

        param_name = f"edge_{attr_name}"
        default = defaults[param_name]
        attr = kwargs.get(param_name, attr_name)

        def get_attr(e):
            if isinstance(attr, dict):
                return attr.get(e, default)
            else:
                return edge_subgraph.edges[e].get(attr, default)

        def check_attr(e):
            if isinstance(attr, dict):
                return e in attr
            else:
                return attr in edge_subgraph.edges[n]

        if default is None:
            # raise instead of using non-existant default value
            for e in seq:
                if not check_attr(e):
                    raise nx.NetworkXError(
                        f"Attribute '{attr_name}' missing for edge {e}"
                    )

        if (
            attr is not None
            and not isinstance(attr, dict)
            and nx.get_edge_attributes(edge_subgraph, attr) == {}
            and any(attr == v for k, v in kwargs.items() if "edge" in k)
        ):
            return [attr for _ in seq]

        return [get_attr(e) for e in seq]

    def get_edge_attr(e, attr_name):
        """Return the final edge attribute value, using default if not None"""

        param_name = f"edge_{attr_name}"
        default = defaults[param_name]
        attr = kwargs.get(param_name, attr_name)

        def get_attr(e):
            if isinstance(attr, dict):
                return attr.get(e, default)
            else:
                return edge_subgraph.edges[e].get(attr, default)

        def check_attr(e):
            if isinstance(attr, dict):
                return e in attr
            else:
                return attr in edge_subgraph.edges[e]

        if default is None and not check_attr(e):
            raise nx.NetworkXError(f"Attribute '{attr_name}' missing from edge {e}")

        if (
            attr is not None
            and not isinstance(attr, dict)
            and nx.get_edge_attributes(edge_subgraph, attr) == {}
            and attr in kwargs.values()
        ):
            return attr

        return get_attr(e)

    def get_node_attr(n, attr_name, use_edge_subgraph=True):
        """Return the final node attribute value, using default if not None"""
        subgraph = edge_subgraph if use_edge_subgraph else node_subgraph

        param_name = f"node_{attr_name}"
        default = defaults[param_name]
        attr = kwargs.get(param_name, attr_name)

        def get_attr(n):
            if isinstance(attr, dict):
                return attr.get(n, default)
            else:
                return subgraph.nodes[n].get(attr, default)

        def check_attr(n):
            if isinstance(attr, dict):
                return n in attr
            else:
                return attr in subgraph.nodes[n]

        if default is None and not check_attr(n):
            raise nx.NetworkXError(f"Attribute '{attr_name}' missing from node {n}")

        if (
            attr is not None
            and not isinstance(attr, dict)
            and nx.get_node_attributes(subgraph, attr) == {}
            and attr in kwargs.values()
        ):
            return attr

        return get_attr(n)

    # Taken from ConnectionStyleFactory
    def self_loop(edge_index, node_size):
        def self_loop_connection(posA, posB, *args, **kwargs):
            if not np.all(posA == posB):
                raise nx.NetworkXError(
                    "`self_loop` connection style method"
                    "is only to be used for self-loops"
                )
            # this is called with _screen space_ values
            # so convert back to data space
            data_loc = canvas.transData.inverted().transform(posA)
            # Scale self loop based on the size of the base node
            # Size of nodes are given in points ** 2 and each point is 1/72 of an inch
            v_shift = np.sqrt(node_size) / 72
            h_shift = v_shift * 0.5
            # put the top of the loop first so arrow is not hidden by node
            path = np.asarray(
                [
                    # 1
                    [0, v_shift],
                    # 4 4 4
                    [h_shift, v_shift],
                    [h_shift, 0],
                    [0, 0],
                    # 4 4 4
                    [-h_shift, 0],
                    [-h_shift, v_shift],
                    [0, v_shift],
                ]
            )
            # Rotate self loop 90 deg. if more than 1
            # This will allow for maximum of 4 visible self loops
            if edge_index % 4:
                x, y = path.T
                for _ in range(edge_index % 4):
                    x, y = y, -x
                path = np.array([x, y]).T
            return mpl.path.Path(
                canvas.transData.transform(data_loc + path), [1, 4, 4, 4, 4, 4, 4]
            )

        return self_loop_connection

    def to_marker_edge(size, marker):
        if marker in "s^>v<d":
            return np.sqrt(2 * size) / 2
        else:
            return np.sqrt(size) / 2

    def build_fancy_arrow(e):
        source_margin = to_marker_edge(
            get_node_attr(e[0], "size"),
            get_node_attr(e[0], "shape"),
        )
        source_margin = max(
            source_margin,
            get_edge_attr(e, "source_margin"),
        )

        target_margin = to_marker_edge(
            get_node_attr(e[1], "size"),
            get_node_attr(e[1], "shape"),
        )
        target_margin = max(
            target_margin,
            get_edge_attr(e, "target_margin"),
        )
        return mpl.patches.FancyArrowPatch(
            pos[e[0]],
            pos[e[1]],
            arrowstyle=get_edge_attr(e, "arrowstyle"),
            connectionstyle=(
                get_edge_attr(e, "curvature")
                if e[0] != e[1]
                else self_loop(
                    0 if len(e) == 2 else e[2] % 4,
                    get_node_attr(e[0], "size"),
                )
            ),
            color=get_edge_attr(e, "color"),
            alpha=get_edge_attr(e, "alpha"),
            linestyle=get_edge_attr(e, "style"),
            linewidth=get_edge_attr(e, "width"),
            mutation_scale=get_edge_attr(e, "arrowsize"),
            shrinkA=source_margin,
            shrinkB=target_margin,
            zorder=1,
        )

    def build_ghost_fancy_arrow(e):
        node_size = kwargs.get("node_size", defaults["node_size"])
        src_size = node_size[e[0]] if isinstance(node_size, dict) else node_size
        tar_size = node_size[e[1]] if isinstance(node_size, dict) else node_size
        source_margin = to_marker_edge(src_size, "o")
        target_margin = to_marker_edge(tar_size, "o")
        curvature = kwargs.get("edge_curvature", defaults["edge_curvature"])
        curvature = curvature[e] if isinstance(curvature, dict) else curvature
        return mpl.patches.FancyArrowPatch(
            pos[e[0]],
            pos[e[1]],
            connectionstyle=(
                curvature
                if e[0] != e[1]
                else self_loop(
                    0 if len(e) == 2 else e[2] % 4,
                    src_size,
                )
            ),
            shrinkA=source_margin,
            shrinkB=target_margin,
            zorder=1,
        )

    class CurvedArrowText(CurvedArrowTextBase, mpl.text.Text):
        pass

    ### Draw the nodes first
    node_visible = kwargs.get("node_visible", "visible")
    if isinstance(node_visible, bool):
        if node_visible:
            visible_nodes = G.nodes()
        else:
            visible_nodes = []
    elif isinstance(node_visible, dict):
        visible_nodes = [n for n, v in node_visible.items() if v]
    else:
        visible_nodes = [
            n for n, v in nx.get_node_attributes(G, node_visible, True).items() if v
        ]

    node_subgraph = G.subgraph(visible_nodes)

    # Ignore the default dict value since that's for default values to use, not
    # default attribute name
    pos = kwargs.get("node_pos", "pos")

    if callable(pos):
        pos_map = pos(node_subgraph)
        pos = pos_map
        kwargs["node_pos"] = pos_map
    elif not isinstance(pos, dict) and nx.get_node_attributes(G, pos) == {}:
        pos_map = nx.spring_layout(node_subgraph)
        pos = pos_map
        kwargs["node_pos"] = pos_map
    elif not isinstance(pos, dict):
        pos = nx.get_node_attributes(G, pos)

    # Each shape requires a new scatter object since they can't have different
    # shapes.
    if len(visible_nodes) > 0:
        node_shape = kwargs.get("node_shape", "shape")
        node_shape_dict = (
            nx.get_node_attributes(node_subgraph, node_shape, defaults["node_shape"])
            if not isinstance(node_shape, dict)
            else node_shape
        )
        for shape in Counter(node_shape_dict.values()):
            # Filter position just on this shape.
            nodes_with_shape = [
                n
                for n, s in node_shape_dict.items()
                if s == shape or (s is None and shape == defaults["node_shape"])
            ]
            # There are two property sequences to create before hand.
            # 1. position, since it is used for x and y parameters to scatter
            # 2. edgecolor, since the spaeical 'face' parameter value can only be
            #    be passed in as the sole string, not part of a list of strings.
            position = np.asarray(node_property_sequence(nodes_with_shape, "pos"))
            color = np.asarray(
                [
                    compute_colors(c, a)
                    for c, a in zip(
                        node_property_sequence(nodes_with_shape, "color"),
                        node_property_sequence(nodes_with_shape, "alpha"),
                    )
                ]
            )
            border_color = np.asarray(
                [
                    (
                        c
                        if (
                            c := get_node_attr(
                                n,
                                "border_color",
                                False,
                            )
                        )
                        != "face"
                        else color[i]
                    )
                    for i, n in enumerate(nodes_with_shape)
                ]
            )
            canvas.scatter(
                position[:, 0],
                position[:, 1],
                s=node_property_sequence(nodes_with_shape, "size"),
                c=color,
                marker=shape,
                linewidths=node_property_sequence(nodes_with_shape, "border_width"),
                edgecolors=border_color,
                zorder=2,
            )

    ### Draw node labels
    node_label = kwargs.get("node_label", "label")
    # Plot labels if node_label is not None and not False
    node_label_objs = {}
    if node_label is not None and node_label is not False:
        default_dict = {}
        if isinstance(node_label, dict):
            default_dict = node_label
            node_label = None

        for n, lbl in node_subgraph.nodes(data=node_label):
            if lbl is False:
                continue

            # We work with label dicts down here...
            if not isinstance(lbl, dict):
                lbl = {"label": lbl if lbl is not None else n}

            lbl_text = lbl.get("label", n)
            if not isinstance(lbl_text, str):
                lbl_text = str(lbl_text)

            lbl.update(default_dict)
            x, y = pos[n]
            t = canvas.text(
                x,
                y,
                lbl_text,
                size=lbl.get("size", defaults["node_label"]["size"]),
                color=lbl.get("color", defaults["node_label"]["color"]),
                family=lbl.get("family", defaults["node_label"]["family"]),
                weight=lbl.get("weight", defaults["node_label"]["weight"]),
                horizontalalignment=lbl.get(
                    "h_align", defaults["node_label"]["h_align"]
                ),
                verticalalignment=lbl.get("v_align", defaults["node_label"]["v_align"]),
                transform=canvas.transData,
                bbox=lbl.get("bbox", defaults["node_label"]["bbox"]),
            )
            if kwargs.get("compat_return_node_label_obj", False):
                node_label_objs[n] = t

    ### Draw edges

    edge_visible = kwargs.get("edge_visible", "visible")
    if isinstance(edge_visible, bool):
        if edge_visible:
            visible_edges = G.edges()
        else:
            visible_edges = []
    elif isinstance(edge_visible, dict):
        visible_edges = [n for n, v in edge_visible.items() if v]
    else:
        visible_edges = [
            e for e, v in nx.get_edge_attributes(G, edge_visible, True).items() if v
        ]

    edge_subgraph = G.edge_subgraph(visible_edges)

    collection_edges = (
        [e for e in edge_subgraph.edges(keys=True) if collection_compatible(e)]
        if edge_subgraph.is_multigraph()
        else [e for e in edge_subgraph.edges() if collection_compatible(e)]
    )
    non_collection_edges = (
        [e for e in edge_subgraph.edges(keys=True) if not collection_compatible(e)]
        if edge_subgraph.is_multigraph()
        else [e for e in edge_subgraph.edges() if not collection_compatible(e)]
    )
    edge_position = np.asarray(
        [
            (
                get_node_attr(u, "pos", use_edge_subgraph=True),
                get_node_attr(v, "pos", use_edge_subgraph=True),
            )
            for u, v, *_ in collection_edges
        ]
    )

    # Only plot a line collection if needed
    edge_collection = None
    if len(collection_edges) > 0:
        edge_collection = mpl.collections.LineCollection(
            edge_position,
            colors=edge_property_sequence(collection_edges, "color"),
            linewidths=edge_property_sequence(collection_edges, "width"),
            linestyle=edge_property_sequence(collection_edges, "style"),
            alpha=edge_property_sequence(collection_edges, "alpha"),
            antialiaseds=(1,),
            zorder=1,
        )
        canvas.add_collection(edge_collection)

    fancy_arrows = {}
    if len(non_collection_edges) > 0:
        for e in non_collection_edges:
            # Cache results for use in edge labels
            fancy_arrows[e] = build_fancy_arrow(e)
            canvas.add_patch(fancy_arrows[e])

    ### Draw edge labels
    edge_label = kwargs.get("edge_label", "label")
    default_dict = {}
    if isinstance(edge_label, dict) and not all(e in G.edges for e in edge_label):
        default_dict = edge_label
        # Restore the default label attribute key of 'label'
        edge_label = "label"

    if kwargs.get("compat_edge_label_anyways", False):
        edge_label_data = [(e, lbl["label"]) for e, lbl in edge_label.items()]
    else:
        edge_label_data = (
            edge_subgraph.edges(data=edge_label, keys=True)
            if edge_subgraph.is_multigraph()
            else edge_subgraph.edges(data=edge_label)
        )
    edge_label_objs = {}
    if edge_label is not None and edge_label is not False:
        for *e, lbl in edge_label_data:
            if kwargs.get("compat_edge_label_anyways", False):
                e = e[0]
            else:
                e = tuple(e)
            # I'm not sure how I want to handle None here... For now it means no label
            if lbl is False or lbl is None:
                continue

            if not isinstance(lbl, dict):
                lbl = {"label": lbl}

            lbl.update(default_dict)
            lbl_text = lbl.get("label")
            if not isinstance(lbl_text, str):
                lbl_text = str(lbl_text)

            # In the old code, every non-self-loop is placed via a fancy arrow patch
            # Only compute a new fancy arrow if needed by caching the results from
            # edge placement.
            try:
                arrow = fancy_arrows[e]
            except KeyError:
                if kwargs.get("compat_edge_label_anyways", False):
                    # We likely have an empty node / edge subgraph
                    arrow = build_ghost_fancy_arrow(e)
                else:
                    arrow = build_fancy_arrow(e)

            if e[0] == e[1]:
                # Taken directly from draw_networkx_edge_labels
                connectionstyle_obj = arrow.get_connectionstyle()
                posA = canvas.transData.transform(pos[e[0]])
                path_disp = connectionstyle_obj(posA, posA)
                path_data = canvas.transData.inverted().transform_path(path_disp)
                x, y = path_data.vertices[0]
                t = canvas.text(
                    x,
                    y,
                    lbl_text,
                    size=lbl.get("size", defaults["edge_label"]["size"]),
                    color=lbl.get("color", defaults["edge_label"]["color"]),
                    family=lbl.get("family", defaults["edge_label"]["family"]),
                    weight=lbl.get("weight", defaults["edge_label"]["weight"]),
                    alpha=lbl.get("alpha", defaults["edge_label"]["alpha"]),
                    horizontalalignment=lbl.get(
                        "h_align", defaults["edge_label"]["h_align"]
                    ),
                    verticalalignment=lbl.get(
                        "v_align", defaults["edge_label"]["v_align"]
                    ),
                    rotation=0,
                    transform=canvas.transData,
                    bbox=lbl.get("bbox", defaults["edge_label"]["bbox"]),
                    zorder=1,
                )
                if kwargs.get("compat_return_edge_label_obj", False):
                    edge_label_objs[e] = t
                continue

            t = CurvedArrowText(
                arrow,
                lbl_text,
                size=lbl.get("size", defaults["edge_label"]["size"]),
                color=lbl.get("color", defaults["edge_label"]["color"]),
                family=lbl.get("family", defaults["edge_label"]["family"]),
                weight=lbl.get("weight", defaults["edge_label"]["weight"]),
                alpha=lbl.get("alpha", defaults["edge_label"]["alpha"]),
                bbox=lbl.get("bbox", defaults["edge_label"]["bbox"]),
                horizontalalignment=lbl.get(
                    "h_align", defaults["edge_label"]["h_align"]
                ),
                verticalalignment=lbl.get("v_align", defaults["edge_label"]["v_align"]),
                label_pos=lbl.get("pos", defaults["edge_label"]["pos"]),
                labels_horizontal=lbl.get("rotate", defaults["edge_label"]["rotate"]),
                transform=canvas.transData,
                zorder=1,
                ax=canvas,
            )
            if kwargs.get("compat_return_edge_label_obj", False):
                edge_label_objs[e] = t

    if kwargs.get("compat_return_edge_viz_obj", False):
        return (
            edge_collection
            if edge_collection is not None
            else list(fancy_arrows.values())
        )
    if kwargs.get("compat_return_node_label_obj", False):
        return node_label_objs
    if kwargs.get("compat_return_edge_label_obj", False):
        return edge_label_objs
    return G


def draw(G, pos=None, ax=None, **kwds):
    """Draw the graph G with Matplotlib.

    Draw the graph as a simple representation with no node
    labels or edge labels and using the full Matplotlib figure area
    and no axis labels by default.  See draw_networkx() for more
    full-featured drawing that allows title, axis labels etc.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary, optional
        A dictionary with nodes as keys and positions as values.
        If not specified a spring layout positioning will be computed.
        See :py:mod:`networkx.drawing.layout` for functions that
        compute node positions.

    ax : Matplotlib Axes object, optional
        Draw the graph in specified Matplotlib axes.

    kwds : optional keywords
        See networkx.draw_networkx() for a description of optional keywords.

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G, pos=nx.spring_layout(G))  # use spring layout

    See Also
    --------
    display
    draw_networkx
    draw_networkx_nodes
    draw_networkx_edges
    draw_networkx_labels
    draw_networkx_edge_labels

    Notes
    -----
    This function has the same name as pylab.draw and pyplot.draw
    so beware when using `from networkx import *`

    since you might overwrite the pylab.draw function.

    With pyplot use

    >>> import matplotlib.pyplot as plt
    >>> G = nx.dodecahedral_graph()
    >>> nx.draw(G)  # networkx draw()
    >>> plt.draw()  # pyplot draw()

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html
    """

    import matplotlib.pyplot as plt

    if ax is None:
        cf = plt.gcf()
    else:
        cf = ax.get_figure()
    cf.set_facecolor("w")
    if ax is None:
        if cf.axes:
            ax = cf.gca()
        else:
            ax = cf.add_axes((0, 0, 1, 1))

    if "with_labels" not in kwds:
        kwds["with_labels"] = "labels" in kwds

    draw_networkx(G, pos=pos, ax=ax, **kwds)
    ax.set_axis_off()
    plt.draw_if_interactive()
    return


def draw_networkx(G, pos=None, arrows=None, with_labels=True, **kwds):
    r"""Draw the graph G using Matplotlib.

    Draw the graph with Matplotlib with options for node positions,
    labeling, titles, and many other drawing features.
    See draw() for simple drawing without labels or axes.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary, optional
        A dictionary with nodes as keys and positions as values.
        If not specified a spring layout positioning will be computed.
        See :py:mod:`networkx.drawing.layout` for functions that
        compute node positions.

    arrows : bool or None, optional (default=None)
        If `None`, directed graphs draw arrowheads with
        `~matplotlib.patches.FancyArrowPatch`, while undirected graphs draw edges
        via `~matplotlib.collections.LineCollection` for speed.
        If `True`, draw arrowheads with FancyArrowPatches (bendable and stylish).
        If `False`, draw edges using LineCollection (linear and fast).
        For directed graphs, if True draw arrowheads.
        Note: Arrows will be the same color as edges.

    arrowstyle : str (default='-\|>' for directed graphs)
        For directed graphs, choose the style of the arrowsheads.
        For undirected graphs default to '-'

        See `matplotlib.patches.ArrowStyle` for more options.

    arrowsize : int or list (default=10)
        For directed graphs, choose the size of the arrow head's length and
        width. A list of values can be passed in to assign a different size for arrow head's length and width.
        See `matplotlib.patches.FancyArrowPatch` for attribute `mutation_scale`
        for more info.

    with_labels :  bool (default=True)
        Set to True to draw labels on the nodes.

    ax : Matplotlib Axes object, optional
        Draw the graph in the specified Matplotlib axes.

    nodelist : list (default=list(G))
        Draw only specified nodes

    edgelist : list (default=list(G.edges()))
        Draw only specified edges

    node_size : scalar or array (default=300)
        Size of nodes.  If an array is specified it must be the
        same length as nodelist.

    node_color : color or array of colors (default='#1f78b4')
        Node color. Can be a single color or a sequence of colors with the same
        length as nodelist. Color can be string or rgb (or rgba) tuple of
        floats from 0-1. If numeric values are specified they will be
        mapped to colors using the cmap and vmin,vmax parameters. See
        matplotlib.scatter for more details.

    node_shape :  string (default='o')
        The shape of the node.  Specification is as matplotlib.scatter
        marker, one of 'so^>v<dph8'.

    alpha : float or None (default=None)
        The node and edge transparency

    cmap : Matplotlib colormap, optional
        Colormap for mapping intensities of nodes

    vmin,vmax : float, optional
        Minimum and maximum for node colormap scaling

    linewidths : scalar or sequence (default=1.0)
        Line width of symbol border

    width : float or array of floats (default=1.0)
        Line width of edges

    edge_color : color or array of colors (default='k')
        Edge color. Can be a single color or a sequence of colors with the same
        length as edgelist. Color can be string or rgb (or rgba) tuple of
        floats from 0-1. If numeric values are specified they will be
        mapped to colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    edge_cmap : Matplotlib colormap, optional
        Colormap for mapping intensities of edges

    edge_vmin,edge_vmax : floats, optional
        Minimum and maximum for edge colormap scaling

    style : string (default=solid line)
        Edge line style e.g.: '-', '--', '-.', ':'
        or words like 'solid' or 'dashed'.
        (See `matplotlib.patches.FancyArrowPatch`: `linestyle`)

    labels : dictionary (default=None)
        Node labels in a dictionary of text labels keyed by node

    font_size : int (default=12 for nodes, 10 for edges)
        Font size for text labels

    font_color : color (default='k' black)
        Font color string. Color can be string or rgb (or rgba) tuple of
        floats from 0-1.

    font_weight : string (default='normal')
        Font weight

    font_family : string (default='sans-serif')
        Font family

    label : string, optional
        Label for graph legend

    hide_ticks : bool, optional
        Hide ticks of axes. When `True` (the default), ticks and ticklabels
        are removed from the axes. To set ticks and tick labels to the pyplot default,
        use ``hide_ticks=False``.

    kwds : optional keywords
        See networkx.draw_networkx_nodes(), networkx.draw_networkx_edges(), and
        networkx.draw_networkx_labels() for a description of optional keywords.

    Notes
    -----
    For directed graphs, arrows  are drawn at the head end.  Arrows can be
    turned off with keyword arrows=False.

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G, pos=nx.spring_layout(G))  # use spring layout

    >>> import matplotlib.pyplot as plt
    >>> limits = plt.axis("off")  # turn off axis

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html

    See Also
    --------
    display
    draw
    draw_networkx_nodes
    draw_networkx_edges
    draw_networkx_labels
    draw_networkx_edge_labels
    """
    from inspect import signature

    import matplotlib.pyplot as plt

    # Get all valid keywords by inspecting the signatures of draw_networkx_nodes,
    # draw_networkx_edges, draw_networkx_labels

    valid_node_kwds = signature(draw_networkx_nodes).parameters.keys()
    valid_edge_kwds = signature(draw_networkx_edges).parameters.keys()
    valid_label_kwds = signature(draw_networkx_labels).parameters.keys()

    # Create a set with all valid keywords across the three functions and
    # remove the arguments of this function (draw_networkx)
    valid_kwds = (valid_node_kwds | valid_edge_kwds | valid_label_kwds) - {
        "G",
        "pos",
        "arrows",
        "with_labels",
    }

    if any(k not in valid_kwds for k in kwds):
        invalid_args = ", ".join([k for k in kwds if k not in valid_kwds])
        raise ValueError(f"Received invalid argument(s): {invalid_args}")

    node_kwds = {k: v for k, v in kwds.items() if k in valid_node_kwds}
    edge_kwds = {k: v for k, v in kwds.items() if k in valid_edge_kwds}
    label_kwds = {k: v for k, v in kwds.items() if k in valid_label_kwds}

    if pos is None:
        pos = nx.drawing.spring_layout(G)  # default to spring layout

    draw_networkx_nodes(G, pos, **node_kwds)
    draw_networkx_edges(G, pos, arrows=arrows, **edge_kwds)
    if with_labels:
        draw_networkx_labels(G, pos, **label_kwds)
    plt.draw_if_interactive()


def draw_networkx_nodes(
    G,
    pos,
    nodelist=None,
    node_size=300,
    node_color="#1f78b4",
    node_shape="o",
    alpha=None,
    cmap=None,
    vmin=None,
    vmax=None,
    ax=None,
    linewidths=None,
    edgecolors=None,
    label=None,
    margins=None,
    hide_ticks=True,
):
    """Draw the nodes of the graph G.

    This draws only the nodes of the graph G.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary
        A dictionary with nodes as keys and positions as values.
        Positions should be sequences of length 2.

    ax : Matplotlib Axes object, optional
        Draw the graph in the specified Matplotlib axes.

    nodelist : list (default list(G))
        Draw only specified nodes

    node_size : scalar or array (default=300)
        Size of nodes.  If an array it must be the same length as nodelist.

    node_color : color or array of colors (default='#1f78b4')
        Node color. Can be a single color or a sequence of colors with the same
        length as nodelist. Color can be string or rgb (or rgba) tuple of
        floats from 0-1. If numeric values are specified they will be
        mapped to colors using the cmap and vmin,vmax parameters. See
        matplotlib.scatter for more details.

    node_shape :  string (default='o')
        The shape of the node.  Specification is as matplotlib.scatter
        marker, one of 'so^>v<dph8'.

    alpha : float or array of floats (default=None)
        The node transparency.  This can be a single alpha value,
        in which case it will be applied to all the nodes of color. Otherwise,
        if it is an array, the elements of alpha will be applied to the colors
        in order (cycling through alpha multiple times if necessary).

    cmap : Matplotlib colormap (default=None)
        Colormap for mapping intensities of nodes

    vmin,vmax : floats or None (default=None)
        Minimum and maximum for node colormap scaling

    linewidths : [None | scalar | sequence] (default=1.0)
        Line width of symbol border

    edgecolors : [None | scalar | sequence] (default = node_color)
        Colors of node borders. Can be a single color or a sequence of colors with the
        same length as nodelist. Color can be string or rgb (or rgba) tuple of floats
        from 0-1. If numeric values are specified they will be mapped to colors
        using the cmap and vmin,vmax parameters. See `~matplotlib.pyplot.scatter` for more details.

    label : [None | string]
        Label for legend

    margins : float or 2-tuple, optional
        Sets the padding for axis autoscaling. Increase margin to prevent
        clipping for nodes that are near the edges of an image. Values should
        be in the range ``[0, 1]``. See :meth:`matplotlib.axes.Axes.margins`
        for details. The default is `None`, which uses the Matplotlib default.

    hide_ticks : bool, optional
        Hide ticks of axes. When `True` (the default), ticks and ticklabels
        are removed from the axes. To set ticks and tick labels to the pyplot default,
        use ``hide_ticks=False``.

    Returns
    -------
    matplotlib.collections.PathCollection
        `PathCollection` of the nodes.

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> nodes = nx.draw_networkx_nodes(G, pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html

    See Also
    --------
    display
    draw
    draw_networkx
    draw_networkx_edges
    draw_networkx_labels
    draw_networkx_edge_labels
    """

    from collections.abc import Iterable
    from itertools import cycle

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    if ax is None:
        ax = plt.gca()

    if nodelist is None:
        nodelist = list(G)

    if len(nodelist) == 0:  # empty nodelist, no drawing
        return mpl.collections.PathCollection(None)

    disp_node_visible = {n: n in nodelist for n in G.nodes}
    disp_node_size = (
        node_size
        if not isinstance(node_size, Iterable)
        else dict(zip(nodelist, node_size))
    )
    mapper = None
    if cmap is not None:
        mapper = mpl.cm.ScalarMappable(cmap=cmap)
    else:
        mapper = mpl.cm.ScalarMappable(cmap=plt.get_cmap())

    if vmin is None:
        if isinstance(node_color, list | np.ndarray) and all(
            isinstance(c, Number) for c in node_color
        ):
            vmin = min(node_color)
        else:
            vmin = 0.0
    if vmax is None:
        if isinstance(node_color, list | np.ndarray) and all(
            isinstance(c, Number) for c in node_color
        ):
            vmax = max(node_color)
        else:
            vmax = 1.0
    mapper.set_clim(vmin, vmax)

    def map_color(c):
        if mapper is None:
            raise nx.NetworkXError("Supplied scalar color without color map.")

        return tuple(float(x) for x in mapper.to_rgba(c))

    disp_node_color = None
    if isinstance(node_color, Number):
        disp_node_color = map_color(node_color)
    elif isinstance(node_color, str):
        disp_node_color = node_color
    elif isinstance(node_color, (np.ndarray | list)):
        disp_node_color = {
            n: map_color(ns) if isinstance(ns, Number) else ns
            for n, ns in zip(nodelist, node_color)
        }

    disp_node_shape = (
        node_shape if isinstance(node_shape, str) else dict(zip(nodelist, node_shape))
    )

    disp_node_alpha = (
        alpha if not isinstance(alpha, Iterable) else dict(zip(nodelist, cycle(alpha)))
    )

    disp_node_border_width = (
        linewidths
        if not isinstance(linewidths, Iterable)
        else dict(zip(nodelist, linewidths))
    )

    disp_node_border_color = (
        edgecolors
        if not isinstance(edgecolors, (np.ndarray | list))
        else {
            n: map_color(c) if isinstance(c, Number) else c
            for n, c in zip(nodelist, cycle(edgecolors))
        }
    )

    display(
        G,
        canvas=ax,
        node_pos=pos,
        node_visible=disp_node_visible,
        node_size=disp_node_size,
        node_color=disp_node_color,
        node_shape=disp_node_shape,
        node_alpha=disp_node_alpha,
        node_border_width=disp_node_border_width,
        node_border_color=disp_node_border_color,
        node_label=False,
        edge_visible=False,
        edge_label=False,
        hide_ticks=hide_ticks,
    )

    if margins is not None:
        if isinstance(margins, Iterable):
            ax.margins(*margins)
        else:
            ax.margins(margins)

    for col in ax.collections:
        if isinstance(col, mpl.collections.PathCollection):
            return col

    return None


def draw_networkx_edges(
    G,
    pos,
    edgelist=None,
    width=1.0,
    edge_color="k",
    style="solid",
    alpha=None,
    arrowstyle=None,
    arrowsize=10,
    edge_cmap=None,
    edge_vmin=None,
    edge_vmax=None,
    ax=None,
    arrows=None,
    label=None,
    node_size=300,
    nodelist=None,
    node_shape="o",
    connectionstyle="arc3",
    min_source_margin=0,
    min_target_margin=0,
    hide_ticks=True,
):
    r"""Draw the edges of the graph G.

    This draws only the edges of the graph G.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary
        A dictionary with nodes as keys and positions as values.
        Positions should be sequences of length 2.

    edgelist : collection of edge tuples (default=G.edges())
        Draw only specified edges

    width : float or array of floats (default=1.0)
        Line width of edges

    edge_color : color or array of colors (default='k')
        Edge color. Can be a single color or a sequence of colors with the same
        length as edgelist. Color can be string or rgb (or rgba) tuple of
        floats from 0-1. If numeric values are specified they will be
        mapped to colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    style : string or array of strings (default='solid')
        Edge line style e.g.: '-', '--', '-.', ':'
        or words like 'solid' or 'dashed'.
        Can be a single style or a sequence of styles with the same
        length as the edge list.
        If less styles than edges are given the styles will cycle.
        If more styles than edges are given the styles will be used sequentially
        and not be exhausted.
        Also, `(offset, onoffseq)` tuples can be used as style instead of a strings.
        (See `matplotlib.patches.FancyArrowPatch`: `linestyle`)

    alpha : float or array of floats (default=None)
        The edge transparency.  This can be a single alpha value,
        in which case it will be applied to all specified edges. Otherwise,
        if it is an array, the elements of alpha will be applied to the colors
        in order (cycling through alpha multiple times if necessary).

    edge_cmap : Matplotlib colormap, optional
        Colormap for mapping intensities of edges

    edge_vmin,edge_vmax : floats, optional
        Minimum and maximum for edge colormap scaling

    ax : Matplotlib Axes object, optional
        Draw the graph in the specified Matplotlib axes.

    arrows : bool or None, optional (default=None)
        If `None`, directed graphs draw arrowheads with
        `~matplotlib.patches.FancyArrowPatch`, while undirected graphs draw edges
        via `~matplotlib.collections.LineCollection` for speed.
        If `True`, draw arrowheads with FancyArrowPatches (bendable and stylish).
        If `False`, draw edges using LineCollection (linear and fast).

        Note: Arrowheads will be the same color as edges.

    arrowstyle : str or list of strs (default='-\|>' for directed graphs)
        For directed graphs and `arrows==True` defaults to '-\|>',
        For undirected graphs default to '-'.

        See `matplotlib.patches.ArrowStyle` for more options.

    arrowsize : int or list of ints(default=10)
        For directed graphs, choose the size of the arrow head's length and
        width. See `matplotlib.patches.FancyArrowPatch` for attribute
        `mutation_scale` for more info.

    connectionstyle : string or iterable of strings (default="arc3")
        Pass the connectionstyle parameter to create curved arc of rounding
        radius rad. For example, connectionstyle='arc3,rad=0.2'.
        See `matplotlib.patches.ConnectionStyle` and
        `matplotlib.patches.FancyArrowPatch` for more info.
        If Iterable, index indicates i'th edge key of MultiGraph

    node_size : scalar or array (default=300)
        Size of nodes. Though the nodes are not drawn with this function, the
        node size is used in determining edge positioning.

    nodelist : list, optional (default=G.nodes())
       This provides the node order for the `node_size` array (if it is an array).

    node_shape :  string (default='o')
        The marker used for nodes, used in determining edge positioning.
        Specification is as a `matplotlib.markers` marker, e.g. one of 'so^>v<dph8'.

    label : None or string
        Label for legend

    min_source_margin : int or list of ints (default=0)
        The minimum margin (gap) at the beginning of the edge at the source.

    min_target_margin : int or list of ints (default=0)
        The minimum margin (gap) at the end of the edge at the target.

    hide_ticks : bool, optional
        Hide ticks of axes. When `True` (the default), ticks and ticklabels
        are removed from the axes. To set ticks and tick labels to the pyplot default,
        use ``hide_ticks=False``.

    Returns
    -------
     matplotlib.collections.LineCollection or a list of matplotlib.patches.FancyArrowPatch
        If ``arrows=True``, a list of FancyArrowPatches is returned.
        If ``arrows=False``, a LineCollection is returned.
        If ``arrows=None`` (the default), then a LineCollection is returned if
        `G` is undirected, otherwise returns a list of FancyArrowPatches.

    Notes
    -----
    For directed graphs, arrows are drawn at the head end.  Arrows can be
    turned off with keyword arrows=False or by passing an arrowstyle without
    an arrow on the end.

    Be sure to include `node_size` as a keyword argument; arrows are
    drawn considering the size of nodes.

    Self-loops are always drawn with `~matplotlib.patches.FancyArrowPatch`
    regardless of the value of `arrows` or whether `G` is directed.
    When ``arrows=False`` or ``arrows=None`` and `G` is undirected, the
    FancyArrowPatches corresponding to the self-loops are not explicitly
    returned. They should instead be accessed via the ``Axes.patches``
    attribute (see examples).

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> edges = nx.draw_networkx_edges(G, pos=nx.spring_layout(G))

    >>> G = nx.DiGraph()
    >>> G.add_edges_from([(1, 2), (1, 3), (2, 3)])
    >>> arcs = nx.draw_networkx_edges(G, pos=nx.spring_layout(G))
    >>> alphas = [0.3, 0.4, 0.5]
    >>> for i, arc in enumerate(arcs):  # change alpha values of arcs
    ...     arc.set_alpha(alphas[i])

    The FancyArrowPatches corresponding to self-loops are not always
    returned, but can always be accessed via the ``patches`` attribute of the
    `matplotlib.Axes` object.

    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> G = nx.Graph([(0, 1), (0, 0)])  # Self-loop at node 0
    >>> edge_collection = nx.draw_networkx_edges(G, pos=nx.circular_layout(G), ax=ax)
    >>> self_loop_fap = ax.patches[0]

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html

    See Also
    --------
    display
    draw
    draw_networkx
    draw_networkx_nodes
    draw_networkx_labels
    draw_networkx_edge_labels

    """
    import warnings
    from collections.abc import Iterable
    from itertools import cycle

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np

    # The default behavior is to use LineCollection to draw edges for
    # undirected graphs (for performance reasons) and use FancyArrowPatches
    # for directed graphs.
    # The `arrows` keyword can be used to override the default behavior
    if arrows is None:
        use_linecollection = not (G.is_directed() or G.is_multigraph())
    else:
        if not isinstance(arrows, bool):
            raise TypeError("Argument `arrows` must be of type bool or None")
        use_linecollection = not arrows

    if isinstance(connectionstyle, str):
        connectionstyle = [connectionstyle]
    elif np.iterable(connectionstyle):
        connectionstyle = list(connectionstyle)
    else:
        msg = "draw_networkx_edges arg `connectionstyle` must be str or iterable"
        raise nx.NetworkXError(msg)

    if isinstance(edgelist, np.ndarray):
        edgelist = list(map(tuple, edgelist))

    # Some kwargs only apply to FancyArrowPatches. Warn users when they use
    # non-default values for these kwargs when LineCollection is being used
    # instead of silently ignoring the specified option
    if use_linecollection:
        msg = (
            "\n\nThe {0} keyword argument is not applicable when drawing edges\n"
            "with LineCollection.\n\n"
            "To make this warning go away, either specify `arrows=True` to\n"
            "force FancyArrowPatches or use the default values.\n"
            "Note that using FancyArrowPatches may be slow for large graphs.\n"
        )
        if arrowstyle is not None:
            warnings.warn(msg.format("arrowstyle"), category=UserWarning, stacklevel=2)
        if arrowsize != 10:
            warnings.warn(msg.format("arrowsize"), category=UserWarning, stacklevel=2)
        if min_source_margin != 0:
            warnings.warn(
                msg.format("min_source_margin"), category=UserWarning, stacklevel=2
            )
        if min_target_margin != 0:
            warnings.warn(
                msg.format("min_target_margin"), category=UserWarning, stacklevel=2
            )
        if any(cs != "arc3" for cs in connectionstyle):
            warnings.warn(
                msg.format("connectionstyle"), category=UserWarning, stacklevel=2
            )

    # NOTE: Arrowstyle modification must occur after the warnings section
    if arrowstyle is None:
        arrowstyle = "-|>" if G.is_directed() else "-"

    if ax is None:
        ax = plt.gca()

    if edgelist is None:
        edgelist = list(G.edges)  # (u, v, k) for multigraph (u, v) otherwise

    if len(edgelist) == 0:
        return []

    if nodelist is None:
        nodelist = list(G.nodes())

    # FancyArrowPatch handles color=None different from LineCollection
    if edge_color is None:
        edge_color = "k"

    disp_edge_visible = {e: e in edgelist for e in G.edges}
    disp_edge_width = (
        width if not isinstance(width, Iterable) else dict(zip(edgelist, cycle(width)))
    )
    disp_edge_style = (
        style if isinstance(style, (str | tuple)) else dict(zip(edgelist, cycle(style)))
    )
    disp_edge_alpha = (
        alpha if not isinstance(alpha, Iterable) else dict(zip(edgelist, cycle(alpha)))
    )

    disp_edge_arrowstyle = (
        arrowstyle
        if isinstance(arrowstyle, str)
        else dict(zip(edgelist, cycle(arrowstyle)))
    )

    if isinstance(arrowsize, Iterable):
        if len(arrowsize) != len(edgelist):
            raise ValueError("arrowsize should have the same length as edgelist")
        disp_edge_arrowsize = dict(zip(edgelist, arrowsize))
    else:
        disp_edge_arrowsize = arrowsize

    disp_node_size = (
        node_size
        if not isinstance(node_size, Iterable)
        else dict(zip(nodelist, node_size))
    )

    if edge_cmap is not None:
        mapper = mpl.cm.ScalarMappable(cmap=edge_cmap)
    else:
        mapper = mpl.cm.ScalarMappable(cmap=plt.get_cmap())

    if edge_vmin is None:
        edge_vmin = 0.0
    if edge_vmax is None:
        edge_vmax = 1.0
    mapper.set_clim(edge_vmin, edge_vmax)

    def map_color(c):
        if mapper is None:
            raise nx.NetworkXError("Supplied scalar color without color map.")

        return tuple(float(x) for x in mapper.to_rgba(c))

    disp_edge_color = None
    if isinstance(edge_color, str):
        disp_edge_color = edge_color
    elif (
        np.iterable(edge_color)
        and len(edge_color) == len(edgelist)
        and np.all([isinstance(c, Number) for c in edge_color])
    ):
        disp_edge_color = {
            n: map_color(ns) for n, ns in zip(edgelist, cycle(edge_color))
        }
    elif (
        # Tuple color... most likely
        isinstance(edge_color, tuple)
        and np.all([isinstance(c, Number) for c in edge_color])
        and (len(edge_color) == 3 or len(edge_color) == 4)
    ):
        disp_edge_color = edge_color
    elif np.iterable(edge_color):
        disp_edge_color = dict(zip(edgelist, cycle(edge_color)))
    else:
        disp_edge_color = edge_color

    disp_node_shape = (
        node_shape if isinstance(node_shape, str) else dict(zip(nodelist, node_shape))
    )

    disp_edge_curvature = (
        connectionstyle
        if not isinstance(connectionstyle, np.ndarray | list)
        else dict(zip(edgelist, cycle(connectionstyle)))
    )

    disp_edge_source_margin = (
        min_source_margin
        if not isinstance(min_source_margin, np.ndarray | list)
        else dict(zip(edgelist, cycle(min_source_margin)))
    )

    disp_edge_target_margin = (
        min_target_margin
        if not isinstance(min_target_margin, np.ndarray | list)
        else dict(zip(edgelist, cycle(min_target_margin)))
    )

    return display(
        G,
        ax,
        node_pos=pos,
        node_visible=False,
        node_label=False,
        edge_label=False,
        edge_visible=disp_edge_visible,
        edge_width=disp_edge_width,
        edge_color=disp_edge_color,
        edge_style=disp_edge_style,
        edge_alpha=disp_edge_alpha,
        edge_arrowstyle=disp_edge_arrowstyle,
        edge_arrowsize=disp_edge_arrowsize,
        edge_curvature=disp_edge_curvature,
        edge_source_margin=disp_edge_source_margin,
        edge_target_margin=disp_edge_target_margin,
        node_shape=disp_node_shape,
        node_size=disp_node_size,
        hide_ticks=hide_ticks,
        compat_force_fancy_arrows=not use_linecollection,
        compat_return_edge_viz_obj=True,
    )


def draw_networkx_labels(
    G,
    pos,
    labels=None,
    font_size=12,
    font_color="k",
    font_family="sans-serif",
    font_weight="normal",
    alpha=None,
    bbox=None,
    horizontalalignment="center",
    verticalalignment="center",
    ax=None,
    clip_on=True,
    hide_ticks=True,
):
    """Draw node labels on the graph G.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary
        A dictionary with nodes as keys and positions as values.
        Positions should be sequences of length 2.

    labels : dictionary (default={n: n for n in G})
        Node labels in a dictionary of text labels keyed by node.
        Node-keys in labels should appear as keys in `pos`.
        If needed use: `{n:lab for n,lab in labels.items() if n in pos}`

    font_size : int or dictionary of nodes to ints (default=12)
        Font size for text labels.

    font_color : color or dictionary of nodes to colors (default='k' black)
        Font color string. Color can be string or rgb (or rgba) tuple of
        floats from 0-1.

    font_weight : string or dictionary of nodes to strings (default='normal')
        Font weight.

    font_family : string or dictionary of nodes to strings (default='sans-serif')
        Font family.

    alpha : float or None or dictionary of nodes to floats (default=None)
        The text transparency.

    bbox : Matplotlib bbox, (default is Matplotlib's ax.text default)
        Specify text box properties (e.g. shape, color etc.) for node labels.

    horizontalalignment : string or array of strings (default='center')
        Horizontal alignment {'center', 'right', 'left'}. If an array is
        specified it must be the same length as `nodelist`.

    verticalalignment : string (default='center')
        Vertical alignment {'center', 'top', 'bottom', 'baseline', 'center_baseline'}.
        If an array is specified it must be the same length as `nodelist`.

    ax : Matplotlib Axes object, optional
        Draw the graph in the specified Matplotlib axes.

    clip_on : bool (default=True)
        Turn on clipping of node labels at axis boundaries

    hide_ticks : bool, optional
        Hide ticks of axes. When `True` (the default), ticks and ticklabels
        are removed from the axes. To set ticks and tick labels to the pyplot default,
        use ``hide_ticks=False``.

    Returns
    -------
    dict
        `dict` of labels keyed on the nodes

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> labels = nx.draw_networkx_labels(G, pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html

    See Also
    --------
    display
    draw
    draw_networkx
    draw_networkx_nodes
    draw_networkx_edges
    draw_networkx_edge_labels
    """
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    if labels is None:
        labels = {n: n for n in G.nodes()}

    individual_params = set()

    def check_individual_params(p_value, p_name):
        if isinstance(p_value, dict):
            if len(p_value) != len(labels):
                raise ValueError(f"{p_name} must have the same length as labels.")
            individual_params.add(p_name)

    def get_param_value(node, p_value, p_name):
        if p_name in individual_params:
            return p_value[node]
        return p_value

    check_individual_params(font_size, "font_size")
    check_individual_params(font_color, "font_color")
    check_individual_params(font_weight, "font_weight")
    check_individual_params(font_family, "font_family")
    check_individual_params(alpha, "alpha")

    text_items = {}  # there is no text collection so we'll fake one
    for n, label in labels.items():
        (x, y) = pos[n]
        if not isinstance(label, str):
            label = str(label)  # this makes "1" and 1 labeled the same
        t = ax.text(
            x,
            y,
            label,
            size=get_param_value(n, font_size, "font_size"),
            color=get_param_value(n, font_color, "font_color"),
            family=get_param_value(n, font_family, "font_family"),
            weight=get_param_value(n, font_weight, "font_weight"),
            alpha=get_param_value(n, alpha, "alpha"),
            horizontalalignment=horizontalalignment,
            verticalalignment=verticalalignment,
            transform=ax.transData,
            bbox=bbox,
            clip_on=clip_on,
        )
        text_items[n] = t

    disp_node_labels = {
        n: {
            "label": lab,
            "size": get_param_value(n, font_size, "font_size"),
            "color": get_param_value(n, font_color, "font_color"),
            "family": get_param_value(n, font_family, "font_family"),
            "weight": get_param_value(n, font_weight, "font_weight"),
            "alpha": get_param_value(n, alpha, "alpha"),
            "h_align": horizontalalignment,
            "v_align": verticalalignment,
        }
        for n, lab in labels.items()
        if n in pos
    }

    return display(
        G,
        canvas=ax,
        node_pos=pos,
        node_visible=False,
        edge_visible=False,
        edge_label=False,
        node_label=disp_node_labels,
        hide_ticks=hide_ticks,
        compat_return_node_label_obj=True,
    )


def draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=None,
    label_pos=0.5,
    font_size=10,
    font_color="k",
    font_family="sans-serif",
    font_weight="normal",
    alpha=None,
    bbox=None,
    horizontalalignment="center",
    verticalalignment="center",
    ax=None,
    rotate=True,
    clip_on=True,
    node_size=300,
    nodelist=None,
    connectionstyle="arc3",
    hide_ticks=True,
):
    """Draw edge labels.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    pos : dictionary
        A dictionary with nodes as keys and positions as values.
        Positions should be sequences of length 2.

    edge_labels : dictionary (default=None)
        Edge labels in a dictionary of labels keyed by edge two-tuple.
        Only labels for the keys in the dictionary are drawn.

    label_pos : float (default=0.5)
        Position of edge label along edge (0=head, 0.5=center, 1=tail)

    font_size : int (default=10)
        Font size for text labels

    font_color : color (default='k' black)
        Font color string. Color can be string or rgb (or rgba) tuple of
        floats from 0-1.

    font_weight : string (default='normal')
        Font weight

    font_family : string (default='sans-serif')
        Font family

    alpha : float or None (default=None)
        The text transparency

    bbox : Matplotlib bbox, optional
        Specify text box properties (e.g. shape, color etc.) for edge labels.
        Default is {boxstyle='round', ec=(1.0, 1.0, 1.0), fc=(1.0, 1.0, 1.0)}.

    horizontalalignment : string (default='center')
        Horizontal alignment {'center', 'right', 'left'}

    verticalalignment : string (default='center')
        Vertical alignment {'center', 'top', 'bottom', 'baseline', 'center_baseline'}

    ax : Matplotlib Axes object, optional
        Draw the graph in the specified Matplotlib axes.

    rotate : bool (default=True)
        Rotate edge labels to lie parallel to edges

    clip_on : bool (default=True)
        Turn on clipping of edge labels at axis boundaries

    node_size : scalar or array (default=300)
        Size of nodes.  If an array it must be the same length as nodelist.

    nodelist : list, optional (default=G.nodes())
       This provides the node order for the `node_size` array (if it is an array).

    connectionstyle : string or iterable of strings (default="arc3")
        Pass the connectionstyle parameter to create curved arc of rounding
        radius rad. For example, connectionstyle='arc3,rad=0.2'.
        See `matplotlib.patches.ConnectionStyle` and
        `matplotlib.patches.FancyArrowPatch` for more info.
        If Iterable, index indicates i'th edge key of MultiGraph

    hide_ticks : bool, optional
        Hide ticks of axes. When `True` (the default), ticks and ticklabels
        are removed from the axes. To set ticks and tick labels to the pyplot default,
        use ``hide_ticks=False``.

    Returns
    -------
    dict
        `dict` of labels keyed by edge

    Examples
    --------
    >>> G = nx.dodecahedral_graph()
    >>> edge_labels = nx.draw_networkx_edge_labels(G, pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    https://networkx.org/documentation/latest/auto_examples/index.html

    See Also
    --------
    display
    draw
    draw_networkx
    draw_networkx_nodes
    draw_networkx_edges
    draw_networkx_labels
    """
    from collections.abc import Iterable
    from itertools import cycle

    import matplotlib.pyplot as plt
    import numpy as np

    if isinstance(connectionstyle, str):
        connectionstyle = [connectionstyle]
    elif np.iterable(connectionstyle):
        connectionstyle = list(connectionstyle)
    else:
        raise nx.NetworkXError(
            "draw_networkx_edges arg `connectionstyle` must be"
            "string or iterable of strings"
        )

    if ax is None:
        ax = plt.gca()

    if edge_labels is None:
        kwds = {"keys": True} if G.is_multigraph() else {}
        edge_labels = {tuple(edge): d for *edge, d in G.edges(data=True, **kwds)}
    # NOTHING TO PLOT
    if not edge_labels:
        return {}
    edgelist, labels = zip(*edge_labels.items())

    if nodelist is None:
        nodelist = list(G.nodes())

    individual_params = {}

    def check_individual_params(p_value, p_name):
        # TODO should this be list or array (as in a numpy array)?
        if isinstance(p_value, list):
            if len(p_value) != len(edgelist):
                raise ValueError(f"{p_name} must have the same length as edgelist.")
            individual_params[p_name] = p_value.iter()

    # Don't need to pass in an edge because these are lists, not dicts
    def get_param_value(p_value, p_name):
        if p_name in individual_params:
            return next(individual_params[p_name])
        return p_value

    check_individual_params(font_size, "font_size")
    check_individual_params(font_color, "font_color")
    check_individual_params(font_weight, "font_weight")
    check_individual_params(alpha, "alpha")
    check_individual_params(horizontalalignment, "horizontalalignment")
    check_individual_params(verticalalignment, "verticalalignment")
    check_individual_params(rotate, "rotate")
    check_individual_params(label_pos, "label_pos")

    # use default box of white with white border
    if bbox is None:
        bbox = {"boxstyle": "round", "ec": (1.0, 1.0, 1.0), "fc": (1.0, 1.0, 1.0)}

    disp_edge_curvature = (
        connectionstyle
        if not isinstance(connectionstyle, Iterable)
        else dict(zip(edgelist, cycle(connectionstyle)))
    )

    disp_edge_lables = {
        e: {
            "label": lbl,
            "size": get_param_value(font_size, "font_size"),
            "color": get_param_value(font_color, "font_color"),
            "family": get_param_value(font_family, "font_family"),
            "weight": get_param_value(font_weight, "font_weight"),
            "alpha": get_param_value(alpha, "alpha"),
            "h_align": get_param_value(horizontalalignment, "horizontalalignment"),
            "v_align": get_param_value(verticalalignment, "verticalalignment"),
            "label_pos": get_param_value(label_pos, "label_pos"),
            "rotate": get_param_value(rotate, "rotate"),
            "bbox": bbox,
        }
        for e, lbl in edge_labels.items()
    }

    return display(
        G,
        canvas=ax,
        node_pos=pos,
        node_visible=False,
        node_label=False,
        edge_visible=False,
        edge_label=disp_edge_lables,
        edge_curvature=disp_edge_curvature,
        hide_ticks=hide_ticks,
        node_size=node_size,
        compat_return_edge_label_obj=True,
        compat_edge_label_anyways=True,
    )


def draw_bipartite(G, **kwargs):
    """Draw the graph `G` with a bipartite layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.bipartite_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Raises
    ------
    NetworkXError :
        If `G` is not bipartite.

    Notes
    -----
    The layout is computed each time this function is called. For
    repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.bipartite_layout` directly and reuse the result::

        >>> G = nx.complete_bipartite_graph(3, 3)
        >>> pos = nx.bipartite_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.complete_bipartite_graph(2, 5)
    >>> nx.draw_bipartite(G)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.bipartite_layout`
    """
    draw(G, pos=nx.bipartite_layout(G), **kwargs)


def draw_circular(G, **kwargs):
    """Draw the graph `G` with a circular layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.circular_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Notes
    -----
    The layout is computed each time this function is called. For
    repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.circular_layout` directly and reuse the result::

        >>> G = nx.complete_graph(5)
        >>> pos = nx.circular_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.draw_circular(G)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.circular_layout`
    """
    draw(G, pos=nx.circular_layout(G), **kwargs)


def draw_kamada_kawai(G, **kwargs):
    """Draw the graph `G` with a Kamada-Kawai force-directed layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.kamada_kawai_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Notes
    -----
    The layout is computed each time this function is called.
    For repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.kamada_kawai_layout` directly and reuse the
    result::

        >>> G = nx.complete_graph(5)
        >>> pos = nx.kamada_kawai_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.draw_kamada_kawai(G)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.kamada_kawai_layout`
    """
    draw(G, pos=nx.kamada_kawai_layout(G), **kwargs)


def draw_random(G, **kwargs):
    """Draw the graph `G` with a random layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.random_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Notes
    -----
    The layout is computed each time this function is called.
    For repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.random_layout` directly and reuse the result::

        >>> G = nx.complete_graph(5)
        >>> pos = nx.random_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.lollipop_graph(4, 3)
    >>> nx.draw_random(G)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.random_layout`
    """
    draw(G, pos=nx.random_layout(G), **kwargs)


def draw_spectral(G, **kwargs):
    """Draw the graph `G` with a spectral 2D layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.spectral_layout(G), **kwargs)

    For more information about how node positions are determined, see
    `~networkx.drawing.layout.spectral_layout`.

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Notes
    -----
    The layout is computed each time this function is called.
    For repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.spectral_layout` directly and reuse the result::

        >>> G = nx.complete_graph(5)
        >>> pos = nx.spectral_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.draw_spectral(G)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.spectral_layout`
    """
    draw(G, pos=nx.spectral_layout(G), **kwargs)


def draw_spring(G, **kwargs):
    """Draw the graph `G` with a spring layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.spring_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Notes
    -----
    `~networkx.drawing.layout.spring_layout` is also the default layout for
    `draw`, so this function is equivalent to `draw`.

    The layout is computed each time this function is called.
    For repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.spring_layout` directly and reuse the result::

        >>> G = nx.complete_graph(5)
        >>> pos = nx.spring_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.path_graph(20)
    >>> nx.draw_spring(G)

    See Also
    --------
    display
    draw
    :func:`~networkx.drawing.layout.spring_layout`
    """
    draw(G, pos=nx.spring_layout(G), **kwargs)


def draw_shell(G, nlist=None, **kwargs):
    """Draw networkx graph `G` with shell layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.shell_layout(G, nlist=nlist), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A networkx graph

    nlist : list of list of nodes, optional
        A list containing lists of nodes representing the shells.
        Default is `None`, meaning all nodes are in a single shell.
        See `~networkx.drawing.layout.shell_layout` for details.

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Notes
    -----
    The layout is computed each time this function is called.
    For repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.shell_layout` directly and reuse the result::

        >>> G = nx.complete_graph(5)
        >>> pos = nx.shell_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> shells = [[0], [1, 2, 3]]
    >>> nx.draw_shell(G, nlist=shells)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.shell_layout`
    """
    draw(G, pos=nx.shell_layout(G, nlist=nlist), **kwargs)


def draw_planar(G, **kwargs):
    """Draw a planar networkx graph `G` with planar layout.

    This is a convenience function equivalent to::

        nx.draw(G, pos=nx.planar_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
        A planar networkx graph

    kwargs : optional keywords
        See `draw_networkx` for a description of optional keywords.

    Raises
    ------
    NetworkXException
        When `G` is not planar

    Notes
    -----
    The layout is computed each time this function is called.
    For repeated drawing it is much more efficient to call
    `~networkx.drawing.layout.planar_layout` directly and reuse the result::

        >>> G = nx.path_graph(5)
        >>> pos = nx.planar_layout(G)
        >>> nx.draw(G, pos=pos)  # Draw the original graph
        >>> # Draw a subgraph, reusing the same node positions
        >>> nx.draw(G.subgraph([0, 1, 2]), pos=pos, node_color="red")

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.draw_planar(G)

    See Also
    --------
    display
    :func:`~networkx.drawing.layout.planar_layout`
    """
    draw(G, pos=nx.planar_layout(G), **kwargs)


def draw_forceatlas2(G, **kwargs):
    """Draw a networkx graph with forceatlas2 layout.

    This is a convenience function equivalent to::

       nx.draw(G, pos=nx.forceatlas2_layout(G), **kwargs)

    .. tip:: Consider using :func:`display`, the new all-in-one drawing function.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, pos=nx.forceatlas2_layout(G), **kwargs)


def apply_alpha(colors, alpha, elem_list, cmap=None, vmin=None, vmax=None):
    """Apply an alpha (or list of alphas) to the colors provided.

    Parameters
    ----------

    colors : color string or array of floats (default='r')
        Color of element. Can be a single color format string,
        or a sequence of colors with the same length as nodelist.
        If numeric values are specified they will be mapped to
        colors using the cmap and vmin,vmax parameters.  See
        matplotlib.scatter for more details.

    alpha : float or array of floats
        Alpha values for elements. This can be a single alpha value, in
        which case it will be applied to all the elements of color. Otherwise,
        if it is an array, the elements of alpha will be applied to the colors
        in order (cycling through alpha multiple times if necessary).

    elem_list : array of networkx objects
        The list of elements which are being colored. These could be nodes,
        edges or labels.

    cmap : matplotlib colormap
        Color map for use if colors is a list of floats corresponding to points
        on a color mapping.

    vmin, vmax : float
        Minimum and maximum values for normalizing colors if a colormap is used

    Returns
    -------

    rgba_colors : numpy ndarray
        Array containing RGBA format values for each of the node colours.

    """
    from itertools import cycle, islice

    import matplotlib as mpl
    import matplotlib.cm  # call as mpl.cm
    import matplotlib.colors  # call as mpl.colors
    import numpy as np

    # If we have been provided with a list of numbers as long as elem_list,
    # apply the color mapping.
    if len(colors) == len(elem_list) and isinstance(colors[0], Number):
        mapper = mpl.cm.ScalarMappable(cmap=cmap)
        mapper.set_clim(vmin, vmax)
        rgba_colors = mapper.to_rgba(colors)
    # Otherwise, convert colors to matplotlib's RGB using the colorConverter
    # object.  These are converted to numpy ndarrays to be consistent with the
    # to_rgba method of ScalarMappable.
    else:
        try:
            rgba_colors = np.array([mpl.colors.colorConverter.to_rgba(colors)])
        except ValueError:
            rgba_colors = np.array(
                [mpl.colors.colorConverter.to_rgba(color) for color in colors]
            )
    # Set the final column of the rgba_colors to have the relevant alpha values
    try:
        # If alpha is longer than the number of colors, resize to the number of
        # elements.  Also, if rgba_colors.size (the number of elements of
        # rgba_colors) is the same as the number of elements, resize the array,
        # to avoid it being interpreted as a colormap by scatter()
        if len(alpha) > len(rgba_colors) or rgba_colors.size == len(elem_list):
            rgba_colors = np.resize(rgba_colors, (len(elem_list), 4))
            rgba_colors[1:, 0] = rgba_colors[0, 0]
            rgba_colors[1:, 1] = rgba_colors[0, 1]
            rgba_colors[1:, 2] = rgba_colors[0, 2]
        rgba_colors[:, 3] = list(islice(cycle(alpha), len(rgba_colors)))
    except TypeError:
        rgba_colors[:, -1] = alpha
    return rgba_colors
