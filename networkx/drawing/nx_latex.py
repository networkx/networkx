r"""
*****
LaTeX
*****

Export NetworkX graphs in LaTeX format using a Adigraph LaTeX library.
Usually, you will want the drawing to appear in a figure environment so
you use :func:`to_latex(G, caption="A caption")`. If you want the raw
drawing commends without a figure environment us `to_latex_raw(G)`.
And it you want to write to a file instead of just returning the latex
code as a string, use `write_latex(G, "filname.tex", caption="A caption")`.

For this drawing feature the drawing attributes should be stored on the
graph as either node attributes or edge attributes. You can point to any
attribute names you like, but the default attributes are:
 - "color" the color of the node/edge
 - "width" the width of the outline of a node, or the edge line of an edge.
 - "label" the string printed inside the node, or along the edge.
 Note that you can put a location inside an edge label to adjust where along
 the edge the label goes with text like:  "My Edge:near end" or "My edge:near start"
 
The edge styles default to arrows for directed graphs and lines for undirected edges.
You can override this for all edges using the `edge_style` keyword argument. For 
individual edges, you can add the style to the edge label.  TODO Does this really work?

To construct a figure with subfigures for each graph to be shown, provide
`to_latex`, or `write_latex` with a list of graphs and a list of sub-captions and
a number of rows of sub-figures inside the figure.

To be able to refer to the figures or subfigures in latex using `\\ref`,
the keyword `latex_label` is available for figures and `sub_labels` for
a list of labels, one for each sub-figure.

Note that some features of TikZ graph drawing are not provided by this interface.
Let us know what you'd like to see available on github, or better yet give us
some code to do it, or even better make a github pull request to add the feature.

Examples
========
>>> G = nx.path_graph(3)
>>> nx.write_latex(G, "my_figure.tex", caption="A path graph", latex_label="fig1")
>>> nx.write_latex(G, "just_my_figure.tex", as_document=True)
>>> latex_code = nx.to_latex(G)  # a string rather than a file

If you want subfigures each containing one graph, you can input a list of graphs.

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
>>> edge_width = {e: 1.5 for e in H3.edges}
>>> nx.set_edge_attributes(G, edge_width, "width")
>>> pos = nx.circular_layout(H3)
>>> latex_code = nx.to_latex(H3, pos=pos, node_color="color", edge_width="width")
>>> print(latex_code)
\documentclass{report}
\usepackage{adigraph}
\usepackage{subcaption}
<BLANKLINE>
\begin{document}
\begin{figure}
    \NewAdigraph{myAdigraph}{
            0,None,:0.5\textwidth,9.189213592397599e-09\textwidth:;
            1,None,:0.35355338839768036\textwidth,0.3535533844243667\textwidth:;
            2,None,:-8.69316629112046e-09\textwidth,0.4999999960266863\textwidth:;
            3,None,:-0.3535533620726258\textwidth,0.3535533844243667\textwidth:;
            4,None,:-0.4999999736749454\textwidth,-3.452217354363565e-08\textwidth:;
            5,None,:-0.3535533918749474\textwidth,-0.35355333624361784\textwidth:;
            6,None,:1.9124967439186124e-08\textwidth,-0.4999999776482591\textwidth:;
            7,None,:0.35355332879303714\textwidth,-0.3535534256505827\textwidth:;
        }{
            0,1,None,::;
            1,2,None,::;
            2,3,None,::;
            3,4,None,::;
            4,5,None,::;
            5,6,None,::;
            6,7,None,::;
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
Adigraph:      https://ctan.org/pkg/adigraph
Tikz:          https://tikz.dev/
Tikz style details:   https://tikz.dev/tikz-shapes#sec-17.11
"""
import os

import networkx as nx

__all__ = ["to_latex_raw", "to_latex", "write_latex"]


@nx.utils.not_implemented_for("multigraph")
def to_latex_raw(
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
            if len(xy) == 2:
                x, y = xy
                adigraph_pos[n] = f"{x/2}\\textwidth,{y/2}\\textwidth"
            elif len(xy) == 1:
                adigraph_pos[n] = xy
            else:
                raise nx.NetworkXError("pos contains values not of length 1 or 2")

    # Setup edge style
    if edge_style is None:
        edge_style = "" if G.is_directed() else "-"

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
        result += i12 + f"{n},{clr},{wth}:{xy}:{lbl};"

    result += i8 + "}{"
    for u, v, data in G.edges(data=True):
        clr = data.get(edge_color, default_edge_color)
        wth = data.get(edge_width, "")
        lbl = data.get(edge_label, "")
        result += i12 + f"{u},{v},{clr},{wth}::{lbl};"

    result += i8 + f"}}[{edge_style}]" + i8 + "\\myAdigraph{}\n"
    return result


_DOC_WRAPPER = r"""\documentclass{{report}}
\usepackage{{adigraph}}
\usepackage{{subcaption}}

\begin{{document}}
{content}
\end{{document}}"""


_FIG_WRAPPER = r"""\begin{{figure}}
{content}{caption}{label}
\end{{figure}}"""


_SUBFIG_WRAPPER = r"""    \begin{{subfigure}}{{{size}\textwidth}}
    {content}{caption}{label}
    \end{{subfigure}}"""


def to_latex(
    Gbunch,
    pos=None,
    default_node_color=None,
    default_edge_color=None,
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
    document_wrapper=_DOC_WRAPPER,
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
        raw = to_latex_raw(
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
            subraw = to_latex_raw(
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
    cap = f"\n    \\caption{{{caption}}}" if caption else ""
    lbl = f"\\label{{{latex_label}}}" if latex_label else ""
    fig = figure_wrapper.format(content=raw, caption=cap, label=lbl)
    if as_document:
        return document_wrapper.format(content=fig)
    return fig


@nx.utils.open_file(1, mode="w")
def write_latex(Gbunch, path, **options):
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
    options : dict
        keyword arguments that mimic the `to_latex` constructor function
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
    path.write(to_latex(Gbunch, **options))
