r"""
*****
LaTeX
*****

Export NetworkX graphs in LaTeX format using the TikZ library within TeX/LaTeX.
Usually, you will want the drawing to appear in a figure environment so
you use :func:`to_latex(G, caption="A caption")`. If you want the raw
drawing commends without a figure environment us `to_latex_raw(G)`.
And it you want to write to a file instead of just returning the latex
code as a string, use `write_latex(G, "filname.tex", caption="A caption")`.

This module also provides a simpler, though feature restricted tools for
formatting the options for each node/edge called AdiGraph.
Note that some features of the Adigraph LaTeX package are not provided here.
The `write_latex` command takes an optional argument `constructor` which
should be set to `to_latex_adigraph` or its default value of `to_latex_tikz`.

To construct a figure with subfigures for each graph to be shown, provide
`to_latex` or `write_latex` a list of graphs, a list of sub-captions,
and a number of rows of sub-figures inside the figure.

To be able to refer to the figures or subfigures in latex using `\\ref`,
the keyword `latex_label` is available for figures and `sub_labels` for
a list of labels, one for each sub-figure.

The TikZ interface (default) allows more options than the adigraph package.
But the adigraph package allows you to store just the e.g. width values
instead of the entire option string. We intend to eventually provide an 
interface to the TikZ Graph features which include e.g. layout algorithms.

Let us know via github what you'd like to see available, or better yet
give us some code to do it, or even better make a github pull request
to add the feature.

The TikZ approach
=================
Drawing options can be stored on the graph as node/edge attributes, or
can be provided as dicts keyed by node/edge to a string of the options
for that node/edge. Similarly a label can be shown for each node/label
by specifying the labels as graph node/edge attributes or by providing
a dict keyed by node/edge to the text to be written for that node/edge.
Edge label options can be specified similarly.

Options for the tikzpicture environment (e.g. "[scale=2]") can be provided
via a keyword argument. Similarly default node and edge options can be
provided through keywords arguments. The default node options are applied
to the single path that draws all nodes (and no edges). The default edge
options are applied to a TikZ "scope" which contains a path for each edge.

Examples
========
>>> G = nx.path_graph(3)
>>> nx.write_latex(G, "my_figure.tex", caption="A path graph", latex_label="fig1")
>>> nx.write_latex(G, "just_my_figure.tex", as_document=True)
>>> latex_code = nx.to_latex(G)  # a string rather than a file

You can change many features of the nodes and edges.

G=nx.path_graph(4, create_using=nx.DiGraph)
pos = {n: (n, n) for n in G}  # nodes set on a line

G.nodes[0]["color"] = "blue"
G.nodes[2]["width"] = "line width=3"
G.nodes[3]["label"] = "Stop"
G.edges[(1, 2)]["width"] = "line width=3"
G.edges[(2, 3)]["color"] = "green"
G.edges[(0, 1)]["label"] = "1st Step:near start"
G.edges[(2, 3)]["label"] = "3rd Step:near end"
G.edges[(1, 2)]["label"] = "2nd Step"

nx.write_latex(G, "latex_graph.tex", pos=pos, as_document=True)

Then compile the LaTeX using something like ``pdflatex latex_graph.tex``
and view the pdf file created: ``latex_graph.pdf``.

If you want **subfigures** each containing one graph, you can input a list of graphs.

>>> H1 = nx.path_graph(4)
>>> H2 = nx.complete_graph(4)
>>> H3 = nx.path_graph(8)
>>> H4 = nx.complete_graph(8)
>>> graphs = [H1, H2, H3, H4]
>>> caps = ["Path 4", "Complete graph 4", "Path 8", "Complete graph 8"]
>>> lbls = ["fig2a", "fig2b", "fig2c", "fig2d"]
>>> nx.write_latex(graphs, "subfigs.tex", n_rows=2, sub_captions=caps, sub_labels=lbls)
>>> latex_code = nx.to_latex(graphs, n_rows=2, sub_captions=caps, sub_labels=lbls)

>>> node_color = {0: "red", 1: "orange", 2: "blue", 3: "gray!90"}
>>> edge_width = {e: "line width=1.5" for e in H3.edges}
>>> pos = nx.circular_layout(H3)
>>> latex_code = nx.to_latex(H3, pos, node_options=node_color, edge_options=edge_width)
>>> print(latex_code)
\documentclass{report}
\usepackage{tikz}
\usepackage{subcaption}
<BLANKLINE>
\begin{document}
\begin{figure}
  \begin{tikzpicture}
      \draw
        (1.0, 0.0) node[red] (0){0}
        (0.707, 0.707) node[orange] (1){1}
        (-0.0, 1.0) node[blue] (2){2}
        (-0.707, 0.707) node[gray!90] (3){3}
        (-1.0, -0.0) node (4){4}
        (-0.707, -0.707) node (5){5}
        (0.0, -1.0) node (6){6}
        (0.707, -0.707) node (7){7};
      \begin{scope}[-]
        \draw (0) to[line width=1.5] (1);
        \draw (1) to[line width=1.5] (2);
        \draw (2) to[line width=1.5] (3);
        \draw (3) to[line width=1.5] (4);
        \draw (4) to[line width=1.5] (5);
        \draw (5) to[line width=1.5] (6);
        \draw (6) to[line width=1.5] (7);
      \end{scope}
    \end{tikzpicture}
\end{figure}
\end{document}


The Adigraph approach
=====================
Drawing attributes should be stored on the graph as node/edge attributes.
The default attribute names are:
 - "color" the color of the node/edge
 - "width" the width of the outline of a node, or the edge line of an edge.
 - "label" the string printed inside the node, or along the edge.
 Note that you can put a location inside an edge label to adjust where along
 the edge the label goes with text like:  "My Edge:near end" or "My edge:near start"
Possible locations are: (with fraction along edge 0, 0.125, 0.25, 0.5, 0.75, 0.875, 1)
at end, very near end, near end, midway, near start, very near start, at start
 
The edge styles default to [->] for directed graphs and [-] for undirected edges.
You can override this (for all edges) using the `edge_style` keyword argument.

Examples
========
>>> G = nx.path_graph(3)
>>> nx.write_latex(G, "my_figure.tex", caption="A path graph", latex_label="fig1")
>>> nx.write_latex(G, "just_my_figure.tex", as_document=True)
>>> latex_code = nx.to_latex(G)  # a string rather than a file

You can change the color, width, label and position of edges.
And you can change color, outline width, and label of nodes.

G=nx.path_graph(4, create_using=nx.DiGraph)
pos = {n: 2 for n in G}  # nodes set on a circle of radius 2

G.nodes[0]["style"] = "blue"
G.nodes[2]["style"] = "line width=3"
G.nodes[3]["label"] = "Stop"
G.edges[(1, 2)]["style"] = "line width=3"
G.edges[(2, 3)]["style"] = "green"
G.edges[(0, 1)]["label"] = "1st Step
G.edges[(0, 1)]["label_opts"] = "near start"
G.edges[(2, 3)]["label"] = "3rd Step"
G.edges[(2, 3)]["label_opts"] = "near end"
G.edges[(1, 2)]["label"] = "2nd Step"

nx.write_latex(
    G,
    "latex_graph.tex",
    pos=pos,
    as_document=True,
    node_options="style",
    node_label="label",
    edge_options="style",
    edge_label="label",
    edge_label_options="label_opts",
    tikz_options="[scale=2]",
)

Then compile the LaTeX using something like ``pdflatex latex_graph.tex``
and view the pdf file created: ``latex_graph.pdf``.

If you want **subfigures** each containing one graph, you can input a list of graphs.

>>> H1 = nx.path_graph(4)
>>> H2 = nx.complete_graph(4)
>>> H3 = nx.path_graph(8)
>>> H4 = nx.complete_graph(8)
>>> graphs = [H1, H2, H3, H4]
>>> caps = ["Path 4", "Complete graph 4", "Path 8", "Complete graph 8"]
>>> lbls = ["fig2a", "fig2b", "fig2c", "fig2d"]
>>> nx.write_latex(graphs, "subfigs.tex", n_rows=2, sub_captions=caps, sub_labels=lbls)
>>> latex_code = nx.to_latex(graphs, n_rows=2, sub_captions=caps, sub_labels=lbls)

>>> node_color = {0: "red", 1: "orange", 2: "blue", 3: "gray!90"}
>>> nx.set_node_attributes(G, node_color, "color")
>>> edge_width = {e: "line width=1.5" for e in H3.edges}
>>> nx.set_node_attributes(G, edge_width, "width")
>>> pos = nx.circular_layout(H3)
>>> print(nx.to_latex_adigraph(H3, pos))
\documentclass{report}
\usepackage{adigraph}
\usepackage{subcaption}
<BLANKLINE>
\begin{document}
\begin{figure}
    \NewAdigraph{myAdigraph}{
        0,red,:0.5\textwidth,9.189213592397599e-09\textwidth:;
        1,red,:0.35355338839768036\textwidth,0.3535533844243667\textwidth:;
        2,red,:-8.69316629112046e-09\textwidth,0.4999999960266863\textwidth:;
        3,red,:-0.3535533620726258\textwidth,0.3535533844243667\textwidth:;
        4,red,:-0.4999999736749454\textwidth,-3.452217354363565e-08\textwidth:;
        5,red,:-0.3535533918749474\textwidth,-0.35355333624361784\textwidth:;
        6,red,:1.9124967439186124e-08\textwidth,-0.4999999776482591\textwidth:;
        7,red,:0.35355332879303714\textwidth,-0.3535534256505827\textwidth:;
    }{
        0,1,black;
        1,2,black;
        2,3,black;
        3,4,black;
        4,5,black;
        5,6,black;
        6,7,black;
    }[-]
    \myAdigraph{}
\end{figure}
\end{document}


Notes
-----
If you want to change the preamble/postamble of the figure/document/subfigure
environment, use the keyword arguments: `figure_wrapper`, `document_wrapper`,
`subfigure_wrapper`. The default values are stored in private variables
``nx.nx_layout._DOCUMENT_WRAPPER``, e.g.


References
----------
TikZ:          https://tikz.dev/
TikZ options details:   https://tikz.dev/tikz-actions
Adigraph:      https://ctan.org/pkg/adigraph
"""
import numbers
import os

import networkx as nx

__all__ = [
    "to_latex_adigraph_raw",
    "to_latex_adigraph",
    "to_latex_tikz_raw",
    "to_latex_tikz",
    "to_latex",
    "write_latex",
]


def to_latex_tikz_raw(
    G,
    pos="pos",
    tikz_options="",
    default_node_options="",
    node_options="node_options",
    node_label="label",
    default_edge_options="",
    edge_options="edge_options",
    edge_label="label",
    edge_label_options="edge_label_options",
):
    """Return a string of the LaTeX/TikZ code to draw `G`

    This function produces just the code for the tikzpicture
    without any enclosing environment.

    Parameters
    ==========
    G : NetworkX graph
        The NetworkX graph to be drawn
    pos : string
        The name of the node attribute on `G` that holds the position of each node.
        Positions can be sequences of length 2 with numbers for (x,y) coordinates.
        They can also be strings to denote positions in TikZ style, such as (x, y)
        or (angle:radius).
        If None, a circular layout is provided by TikZ.
        If you are drawing many graphs in subfigures, use a list of position dicts.
    tikz_options : string
        The tikzpicture options description defining the options for the picture.
        Often large scale options like `[scale=2]`.
    default_node_options : string
        The draw options for a path of nodes. Individual node options override these.
    node_options : string
        The name of the node attribute on `G` that holds the options for each node.
    node_label : string
        The name of the node attribute on `G` that holds the node label (text)
        displayed for each node. If the attribute is "" or not present, the node
        itself is drawn as a string. LaTeX processing such as `"$A_1$" is allowed.
    default_edge_options : string
        The options for the scope drawing all edges. The default is "[-]" for
        undirected graphs and "[->]" for directed graphs.
    edge_options : string
        The name of the edge attribute on `G` that holds the options for each edge.
        If the edge is a self-loop and ``"loop" not in edge_options`` the option
        "loop," is added to the options for the self-loop edge. Hence you can
        use "[loop above]" explicitly, but the default is "[loop]".
    edge_label : string
        The name of the edge attribute on `G` that holds the edge label (text)
        displayed for each edge. If the attribute is "" or not present, no edge
        label is drawn.
    edge_label_options : string
        The name of the edge attribute on `G` that holds the label options for
        each edge. For example, "[sloped,above,blue]". The default is no options.

    Returns
    =======
    latex_code : string
       The text string which draws the desired graph(s) when compiled by LaTeX.

    See Also
    ========
    to_latex_tikz
    write_latex
    """
    i4 = "\n    "
    i8 = "\n        "

    # set up position dict
    # TODO allow pos to be None and use a nice TikZ default
    if not isinstance(pos, dict):
        pos = nx.get_node_attributes(G, pos)
    if not pos:
        # circulr layout with radius 1
        pos = {n: f"({round(2* 3.1415 * i / len(G), 3)}:1)" for i, n in enumerate(G)}
    for node in G:
        if node not in pos:
            raise nx.NetworkXError(f"node {node} has no specified pos {pos}")
        posnode = pos[node]
        if not isinstance(posnode, str):
            try:
                posx, posy = posnode
            except ValueError:
                raise nx.NetworkXError(
                    f"position pos[{node}] is not 2-tuple or a string: {posnode}"
                )
            pos[node] = f"({round(posx, 3)}, {round(posy, 3)})"

    # set up all the dicts
    # TODO allow dicts to be input in addition to attr name strings
    if not isinstance(node_options, dict):
        node_options = nx.get_node_attributes(G, node_options)
    if not isinstance(node_label, dict):
        node_label = nx.get_node_attributes(G, node_label)
    if not isinstance(edge_options, dict):
        edge_options = nx.get_edge_attributes(G, edge_options)
    if not isinstance(edge_label, dict):
        edge_label = nx.get_edge_attributes(G, edge_label)
    if not isinstance(edge_label_options, dict):
        edge_label_options = nx.get_edge_attributes(G, edge_label_options)

    # process default options (add brackets or not)
    topts = "" if tikz_options == "" else f"[{tikz_options.strip('[]')}]"
    defn = "" if default_node_options == "" else f"[{default_node_options.strip('[]')}]"
    linestyle = f"{'->' if G.is_directed() else '-'}"
    if default_edge_options == "":
        defe = "[" + linestyle + "]"
    elif "-" in default_edge_options:
        defe = default_edge_options
    else:
        defe = f"[{linestyle},{default_edge_options.strip('[]')}]"

    # Construct the string line by line
    result = "  \\begin{tikzpicture}" + topts
    result += i4 + "  \\draw" + defn
    # load the nodes
    for n in G:
        # node options goes inside square brackets
        nopts = f"[{node_options[n].strip('[]')}]" if n in node_options else ""
        # node text goes inside curly brackets {}
        ntext = f"{{{node_label[n]}}}" if n in node_label else f"{{{n}}}"

        result += i8 + f"{pos[n]} node{nopts} ({n}){ntext}"
    result += ";\n"

    # load the edges
    result += "      \\begin{scope}" + defe
    for edge in G.edges:
        u, v = edge[:2]
        e_opts = f"{edge_options[edge]}".strip("[]") if edge in edge_options else ""
        # add loop options for selfloops if not present
        if u == v and "loop" not in e_opts:
            e_opts = "loop," + e_opts
        e_opts = f"[{e_opts}]" if e_opts != "" else ""
        # TODO -- handle bending of multiedges

        els = edge_label_options[edge] if edge in edge_label_options else ""
        # edge label options goes inside square brackets []
        els = f"[{els.strip('[]')}]"
        # edge text is drawn using the TikZ node command inside curly brackets {}
        e_label = f" node{els} {{{edge_label[edge]}}}" if edge in edge_label else ""

        result += i8 + f"\\draw ({u}) to{e_opts} ({v}){e_label};"

    result += "\n      \\end{scope}\n    \\end{tikzpicture}\n"
    return result


@nx.utils.not_implemented_for("multigraph")
def to_latex_adigraph_raw(
    G,
    pos=None,
    default_node_color="red",
    default_edge_color="black",
    node_color="color",
    edge_color="color",
    node_width="width",
    edge_width="width",
    node_label="label",
    edge_label="label",
    edge_style=None,
):
    # Setup position dict
    if pos is None:
        # default is a circle with radius 1
        adigraph_pos = {n: 1 for n in G}
    else:
        # try pos as attribute name in G.nodes
        n_pos = {}
        try:
            for n, data in G.nodes(data=True):
                n_pos[n] = data[pos]
            pos = n_pos
        except KeyError:
            raise nx.NetworkXError(
                "pos appears to be a node attr name but not for all nodes"
            )
        except TypeError:
            # try pos is dict
            if G.nodes - pos.keys():
                raise nx.NetworkXError("pos appears as a dict but without all nodes")

        adigraph_pos = {}
        for n, xy in pos.items():
            if isinstance(xy, numbers.Number):
                adigraph_pos[n] = xy
            elif len(xy) == 2:
                x, y = xy
                adigraph_pos[n] = f"{x/2}\\textwidth,{y/2}\\textwidth"
            elif len(xy) == 1:
                adigraph_pos[n] = xy[0]
            else:
                raise nx.NetworkXError("pos contains values not of length 1 or 2")

    # Setup edge style
    if edge_style is None:
        edge_style = "->" if G.is_directed() else "-"

    # indent nicely
    i4 = "\n    "
    i8 = "\n        "
    i12 = "\n            "

    result = "    \\NewAdigraph{myAdigraph}{"
    for n, data in G.nodes(data=True):
        xy = adigraph_pos[n]
        clr = data.get(node_color, default_node_color)
        wth = data.get(node_width, "")
        lbl = data.get(node_label, "")
        result += i8 + f"{n},{clr},{wth}:{xy}:{lbl};"

    result += i4 + "}{"
    for u, v, data in G.edges(data=True):
        clr = data.get(edge_color, default_edge_color)
        wth = data.get(edge_width, "")
        lbl = data.get(edge_label, "")
        # The :1: near lbl is doc'd as a weight which doesn't do anything
        # but is apparently needed for adigraph to show the labels.
        if lbl:
            result += i8 + f"{u},{v},{clr},{wth}:1:{lbl};"
        elif wth:
            result += i8 + f"{u},{v},{clr},{wth};"
        else:
            result += i8 + f"{u},{v},{clr};"

    result += i4 + f"}}[{edge_style}]" + i4 + "\\myAdigraph{}\n"
    return result


_DOC_WRAPPER_TIKZ = r"""\documentclass{{report}}
\usepackage{{tikz}}
\usepackage{{subcaption}}

\begin{{document}}
{content}
\end{{document}}"""


_DOC_WRAPPER_ADIGRAPH = r"""\documentclass{{report}}
\usepackage{{adigraph}}
\usepackage{{subcaption}}

\begin{{document}}
{content}
\end{{document}}"""


_FIG_WRAPPER = r"""\begin{{figure}}
{content}{caption}{label}
\end{{figure}}"""


_SUBFIG_WRAPPER = r"""  \begin{{subfigure}}{{{size}\textwidth}}
{content}{caption}{label}
  \end{{subfigure}}"""


def to_latex_tikz(
    Gbunch,
    pos=None,
    tikz_options="",
    default_node_options="",
    node_options="node_options",
    node_label="node_label",
    default_edge_options="",
    edge_options="edge_options",
    edge_label="edge_label",
    edge_label_options="edge_label_options",
    caption="",
    latex_label="",
    sub_captions=None,
    sub_labels=None,
    n_rows=1,
    as_document=True,
    document_wrapper=_DOC_WRAPPER_TIKZ,
    figure_wrapper=_FIG_WRAPPER,
    subfigure_wrapper=_SUBFIG_WRAPPER,
):
    """Return latex code to draw the graph(s) in Gbunch

    If Gbunch is a graph, it is drawn in a figure environment.
    If Gbunch is an iterable of graphs, each is drawn in a subfigure envionment
    within a single figure environment.

    If `as_document` is True, the figure is wrapped inside a document environment
    so that the resulting string is ready to be compiled by LaTeX. Otherwise,
    the string is ready for inclusion in a larger tex document using `\\include`
    or `\\input` statements.

    Parameters
    ==========
    Gbunch : NetworkX graph or iterable of NetworkX graphs or Adigraphs
        The NetworkX graph to be drawn or an iterable of graphs or Adigraphs
        to be drawn inside subfigures of a single figure.
    pos : string or list of strings
        The name of the node attribute on `G` that holds the position of each node.
        Positions can be sequences of length 2 with numbers for (x,y) coordinates.
        They can also be strings to denote positions in TikZ style, such as (x, y)
        or (angle:radius).
        If None, a circular layout is provided by TikZ.
        If you are drawing many graphs in subfigures, use a list of position dicts.
    tikz_options : string
        The tikzpicture options description defining the options for the picture.
        Often large scale options like `[scale=2]`.
    default_node_options : string
        The draw options for a path of nodes. Individual node options override these.
    node_options : string
        The name of the node attribute on `G` that holds the options for each node.
    node_label : string
        The name of the node attribute on `G` that holds the node label (text)
        displayed for each node. If the attribute is "" or not present, the node
        itself is drawn as a string. LaTeX processing such as `"$A_1$" is allowed.
    default_edge_options : string
        The options for the scope drawing all edges. The default is "[-]" for
        undirected graphs and "[->]" for directed graphs.
    edge_options : string
        The name of the edge attribute on `G` that holds the options for each edge.
        If the edge is a self-loop and ``"loop" not in edge_options`` the option
        "loop," is added to the options for the self-loop edge. Hence you can
        use "[loop above]" explicitly, but the default is "[loop]".
    edge_label : string
        The name of the edge attribute on `G` that holds the edge label (text)
        displayed for each edge. If the attribute is "" or not present, no edge
        label is drawn.
    edge_label_options : string
        The name of the edge attribute on `G` that holds the label options for
        each edge. For example, "[sloped,above,blue]". The default is no options.
    caption : string
        The caption string for the figure environment
    latex_label : string
        The latex label used for the figure for easy referral from the main text
    sub_captions : list of strings
        The sub_caption string for each subfigure in the figure
    sub_latex_labels : list of strings
        The latex label for each subfigure in the figure
    n_rows : int
        The number of rows of subfigures to arrange for multiple graphs
    as_document : bool
        Whether to wrap the latex code in a document envionment for compiling
    document_wrapper : formatted text string with variable ``content``.
        This text is called to evaluate the content embedded in a document
        environment with a preamble setting up the adigraph syntax.
    figure_wrapper : formatted text string
        This text is evaluated with variables ``content``, ``caption`` and ``label``.
        It wraps the content and if a caption is provided, adds the latex code for
        that caption, and if a label is provided, adds the latex code for a label.
    subfigure_wrapper : formatted text string
        This text evaluate variables ``size``, ``content``, ``caption`` and ``label``.
        It wraps the content and if a caption is provided, adds the latex code for
        that caption, and if a label is provided, adds the latex code for a label.
        The size is the vertical size of each row of subfigures as a fraction.

    Returns
    =======
    latex_code : string
        The text string which draws the desired graph(s) when compiled by LaTeX.

    See Also
    ========
    write_latex
    to_latex_tikz_raw
    """
    if hasattr(Gbunch, "adj"):
        raw = to_latex_tikz_raw(
            Gbunch,
            pos,
            tikz_options,
            default_node_options,
            node_options,
            node_label,
            default_edge_options,
            edge_options,
            edge_label,
            edge_label_options,
        )
    else:  # iterator of graphs
        sbf = subfigure_wrapper
        size = 1 / n_rows

        N = len(Gbunch)
        if pos is None:
            pos = [None] * N
        if sub_captions is None:
            sub_captions = [""] * N
        if sub_labels is None:
            sub_labels = [""] * N
        if not (len(Gbunch) == len(pos) == len(sub_captions) == len(sub_labels)):
            raise nx.NetworkXError(
                "length of Gbunch, sub_captions and sub_figures must agree"
            )

        raw = ""
        for G, pos, subcap, sublbl in zip(Gbunch, pos, sub_captions, sub_labels):
            subraw = to_latex_tikz_raw(
                G,
                pos,
                tikz_options,
                default_node_options,
                node_options,
                node_label,
                default_edge_options,
                edge_options,
                edge_label,
                edge_label_options,
            )
            cap = f"    \\caption{{{subcap}}}" if subcap else ""
            lbl = f"\\label{{{sublbl}}}" if sublbl else ""
            raw += sbf.format(size=size, content=subraw, caption=cap, label=lbl)
            raw += "\n"

    # put raw latex code into a figure environment and optionally into a document
    raw = raw[:-1]
    cap = f"\n  \\caption{{{caption}}}" if caption else ""
    lbl = f"\\label{{{latex_label}}}" if latex_label else ""
    fig = figure_wrapper.format(content=raw, caption=cap, label=lbl)
    if as_document:
        return document_wrapper.format(content=fig)
    return fig


to_latex = to_latex_tikz


def to_latex_adigraph(
    Gbunch,
    pos=None,
    default_node_color="red",
    default_edge_color="black",
    node_color="color",
    edge_color="color",
    node_width="width",
    edge_width="width",
    node_label="label",
    edge_label="label",
    edge_style=None,
    caption="",
    latex_label="",
    sub_captions=None,
    sub_labels=None,
    n_rows=1,
    as_document=True,
    document_wrapper=_DOC_WRAPPER_ADIGRAPH,
    figure_wrapper=_FIG_WRAPPER,
    subfigure_wrapper=_SUBFIG_WRAPPER,
):
    """Return latex code to draw the graph(s) in Gbunch

    If Gbunch is a graph, it is drawn in a figure environment.
    If Gbunch is an iterable of graphs, each is drawn in a subfigure envionment
    within a single figure environment.

    If `as_document` is True, the figure is wrapped inside a document environment
    so that the resulting string is ready to be compiled by LaTeX. Otherwise,
    the string is ready for inclusion in a larger tex document using `\\include`
    or `\\input` statements.

    Parameters
    ==========
    Gbunch : NetworkX graph or iterable of NetworkX graphs or Adigraphs
        The NetworkX graph to be drawn or an iterable of graphs or Adigraphs
        to be drawn inside subfigures of a single figure.
    pos : dict or iterable of position dict for each graph or None
        A dict keyed by node to an (x, y) position on the drawing.
        If None, a circular layout is provided by TikZ.
        If you are drawing many graphs in subfigures, use a list of position dicts.
    default_node_color : string
        The color to use if a color is not specified in the `node_color` attribute.
    default_edge_color : string
        The color to use if a color is not specified in the `edge_color` attribute.
    node_color : string or dict
        The name of the node attribute holding a string indicating a color.
        If that attribute does not exist for some node, `default_node_color` is used.
    edge_color : string or dict
        The name of the edge attribute holding a string indicating a color.
        If that attribute does not exist for some edge, `default_edge_color` is used.
    node_width : string or dict (default "")
        The name of the node attribute holding a string indicating node line width.
        If that attribute does not exist for some node, `""` is used.
    edge_width : string or dict (default "")
        The name of the edge attribute holding a string indicating a edge line width.
        If that attribute does not exist for some edge, `""` is used.
    node_label : string or dict (default "")
        The name of node attribute holding a string for that node in the drawing.
        By default `str(node)` is used for each node.
    edge_label : string or dict (default "")
        The name of the edge attribute holding a string indicating a edge line width.
        By default, no label is drawn next to an edge.
    edge_style : string or None
        The ``style`` option for all edges. These can be any valid style previously
        defained in a way TikZ can understand it. Typically this is ``"-"``, ``"->"``,
        ``"dotted"``, or ``"dashed"``.
    caption : string
        The caption string for the figure environment
    latex_label : string
        The latex label used for the figure for easy referral from the main text
    sub_captions : list of strings
        The sub_caption string for each subfigure in the figure
    sub_latex_labels : list of strings
        The latex label for each subfigure in the figure
    n_rows : int
        The number of rows of subfigures to arrange for multiple graphs
    as_document : bool
        Whether to wrap the latex code in a document envionment for compiling
    document_wrapper : formatted text string with variable ``content``.
        This text is called to evaluate the content embedded in a document
        environment with a preamble setting up the adigraph syntax.
    figure_wrapper : formatted text string
        This text is evaluated with variables ``content``, ``caption`` and ``label``.
        It wraps the content and if a caption is provided, adds the latex code for
        that caption, and if a label is provided, adds the latex code for a label.
    subfigure_wrapper : formatted text string
        This text evaluate variables ``size``, ``content``, ``caption`` and ``label``.
        It wraps the content and if a caption is provided, adds the latex code for
        that caption, and if a label is provided, adds the latex code for a label.
        The size is the vertical size of each row of subfigures as a fraction.

    Returns
    =======
    latex_code : string
        The text string which draws the desired graph(s) when compiled by LaTeX.

    See Also
    ========
    write_latex
    """
    if hasattr(Gbunch, "adj"):
        raw = to_latex_adigraph_raw(
            Gbunch,
            pos,
            default_node_color,
            default_edge_color,
            node_color,
            edge_color,
            node_width,
            edge_width,
            node_label,
            edge_label,
        )
    else:  # iterator of graphs
        sbf = subfigure_wrapper
        size = 1 / n_rows

        N = len(Gbunch)
        if pos is None:
            pos = [None] * N
        if sub_captions is None:
            sub_captions = [""] * N
        if sub_labels is None:
            sub_labels = [""] * N
        if not (len(Gbunch) == len(pos) == len(sub_captions) == len(sub_labels)):
            raise nx.NetworkXError(
                "length of Gbunch, sub_captions and sub_figures must agree"
            )

        raw = ""
        for G, pos, subcap, sublbl in zip(Gbunch, pos, sub_captions, sub_labels):
            subraw = to_latex_adigraph_raw(
                G,
                pos,
                default_node_color,
                default_edge_color,
                node_color,
                edge_color,
                node_width,
                edge_width,
                node_label,
                edge_label,
            )
            cap = f"    \\caption{{{subcap}}}" if subcap else ""
            lbl = f"\\label{{{sublbl}}}" if sublbl else ""
            raw += sbf.format(size=size, content=subraw, caption=cap, label=lbl)
            raw += "\n"

    # put raw latex code into a figure environment and optionally into a document
    raw = raw[:-1]
    cap = f"\n  \\caption{{{caption}}}" if caption else ""
    lbl = f"\\label{{{latex_label}}}" if latex_label else ""
    fig = figure_wrapper.format(content=raw, caption=cap, label=lbl)
    if as_document:
        return document_wrapper.format(content=fig)
    return fig


@nx.utils.open_file(1, mode="w")
def write_latex(Gbunch, path, constructor=to_latex_tikz, **options):
    """Write the latex code to draw the graph(s) onto `path`.

    This convenience function creates the latex drawing code as a string
    and writes that to a file ready to be compiled when `as_document is True`
    or ready to be ``\\import``ed or `\\include``ed into your main LaTeX document.

    The `path` argument can be a string filename or a file handle to write to.

    Parameters
    ----------
    Gbunch : NetworkX graph or iterable of NetworkX graphs or Adigraphs
        If Gbunch is a graph, it is drawn in a figure environment.
        If Gbunch is an iterable of graphs, each is drawn in a subfigure
        envionment within a single figure environment.
    path : filename
        Filename or file handle to write to
    constructor : function (default: `to_latex_tikz`)
        Either `to_latex_adigraph` or `to_latex_tikz`
    options : dict
        keyword arguments that mimic the `to_latex_*` constructor functions
        The options can be: (others are ignored)
        pos : dict or iterable of position dict for each graph or None
            A dict keyed by node to an (x, y) position on the drawing.
            If None, a circular layout is provided by TikZ.
            If you are drawing many graphs in subfigures, use a list of position dicts.
        default_node_color : string
            The color to use if a color is not specified in the `node_color` attribute.
        default_edge_color : string
            The color to use if a color is not specified in the `edge_color` attribute.
        node_color : string or dict
            The name of the node attribute holding a string indicating a color.
            If that attribute does not exist for some node, `default_node_color` is used.
        edge_color : string or dict
            The name of the edge attribute holding a string indicating a color.
            If that attribute does not exist for some edge, `default_edge_color` is used.
        node_width : string or dict (default "")
            The name of the node attribute holding a string indicating node line width.
            If that attribute does not exist for some node, `""` is used.
        edge_width : string or dict (default "")
            The name of the edge attribute holding a string indicating a edge line width.
            If that attribute does not exist for some edge, `""` is used.
        node_label : string or dict (default "")
            The name of node attribute holding a string for that node in the drawing.
            By default `str(node)` is used for each node.
        edge_label : string or dict (default "")
            The name of the edge attribute holding a string indicating a edge line width.
            By default, no label is drawn next to an edge.
        edge_style : string or None
            The ``style`` option for all edges. These can be any valid style previously
            defained in a way TikZ can understand it. Typically this is ``"-"``, ``"->"``,
            ``"dotted"``, or ``"dashed"``.
        caption : string
            The caption string for the figure environment
        latex_label : string
            The latex label used for the figure for easy referral from the main text
        sub_captions : list of strings
            The sub_caption string for each subfigure in the figure
        sub_latex_labels : list of strings
            The latex label for each subfigure in the figure
        n_rows : int
            The number of rows of subfigures to arrange for multiple graphs
        as_document : bool
            Whether to wrap the latex code in a document envionment for compiling
        document_wrapper : formatted text string with variable ``content``.
            This text is called to evaluate the content embedded in a document
            environment with a preamble setting up the adigraph syntax.
        figure_wrapper : formatted text string
            This text is evaluated with variables ``content``, ``caption`` and ``label``.
            It wraps the content and if a caption is provided, adds the latex code for
            that caption, and if a label is provided, adds the latex code for a label.
        subfigure_wrapper : formatted text string
            This text evaluate variables ``size``, ``content``, ``caption`` and ``label``.
            It wraps the content and if a caption is provided, adds the latex code for
            that caption, and if a label is provided, adds the latex code for a label.
            The size is the vertical size of each row of subfigures as a fraction.

    See Also
    ========
    to_latex
    """
    path.write(constructor(Gbunch, **options))
