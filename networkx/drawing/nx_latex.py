r"""
*****
LaTeX
*****

Export NetworkX graphs in LaTeX format using a Adigraph LaTeX library.

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
>>> pos = nx.spring_layout(H3, seed=42)
>>> latex_code = nx.to_latex(H3, pos=pos, node_color="color", edge_width="width")
>>> print(latex_code)
\documentclass{report}
\usepackage{adigraph}
\usepackage{subcaption}
<BLANKLINE>
\begin{document}
\begin{figure}
    \NewAdigraph{myAdigraph}{
            0,None,:0.13691873391588788\textwidth,0.48252075234621256\textwidth:;
            1,None,:0.07722434611576236\textwidth,0.37392216097885134\textwidth:;
            2,None,:0.020007452362970562\textwidth,0.23772460620435057\textwidth:;
            3,None,:-0.026381163990210173\textwidth,0.08612095850053242\textwidth:;
            4,None,:-0.05452915409975908\textwidth,-0.07222784919699579\textwidth:;
            5,None,:-0.06258014562321262\textwidth,-0.23025586352234492\textwidth:;
            6,None,:-0.055089924341919554\textwidth,-0.37780476531060614\textwidth:;
            7,None,:-0.03557014433951943\textwidth,-0.5\textwidth:;
        }{
            0,1,None,::;
            1,2,None,::;
            2,3,None,::;
            3,4,None,::;
            4,5,None,::;
            5,6,None,::;
            6,7,None,::;
        }[]
        \myAdigraph{}
\end{figure}
\end{document}


See Also
--------
Adigraph:      https://ctan.org/pkg/adigraph
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
    # Setup attribute dicts
    if pos is None:
        pos = nx.spring_layout(G, seed=42)
    else:
        # try pos as attribute name in G.nodes
        try:
            if all(hasattr(data, pos) for n, data in G.nodes(data=True)):
                pos = nx.get_node_attributes(G, pos)
            raise nx.NetworkXError(
                "pos appears to be a node attr name but not for all nodes"
            )
        except TypeError:
            # try pos is dict
            try:
                any(len(pos[n]) != 2 for n in G)
            except KeyError:
                raise nx.NetworkXError(
                    "pos appears to be a dict but not including all nodes"
                )

    if edge_style is None:
        edge_style = "[]" if G.is_directed() else ""

    # indent nicely
    i4 = "\n    "
    i8 = "\n        "
    i12 = "\n            "

    result = "    \\NewAdigraph{myAdigraph}{"
    for n, data in G.nodes(data=True):
        x, y = pos[n]
        clr = data.get(node_color, default_node_color)
        wth = data.get(node_width, "")
        lbl = data.get(node_label, "")
        result += i12 + f"{n},{clr},{wth}:{x/2}\\textwidth,{y/2}\\textwidth:{lbl};"

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
    default_node_color : string
    default_edge_color : string
    node_color : string or dict
    edge_color : string or dict
    node_width : string or dict
    edge_width : string or dict
    node_label : string or dict
    edge_label : string or dict
    edge_style : string or None
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

        if pos is None:
            pos = [nx.spring_layout(G, seed=42) for G in Gbunch]
        if sub_captions is None:
            sub_captions = [""] * len(Gbunch)
        if sub_labels is None:
            sub_labels = [""] * len(Gbunch)
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

    Parameters
    ----------
    Gbunch : NetworkX graph or iterable of NetworkX graphs or Adigraphs
        If Gbunch is a graph, it is drawn in a figure environment.
        If Gbunch is an iterable of graphs, each is drawn in a subfigure
        envionment within a single figure environment.
    path : filename
        Filename or file handle to write to
    as_document : bool
        Whether to wrap the latex code in a document environment ready to be compiled.
    options : dict
        keyword arguments for the `to_latex` constructor function

    The options can be: (others are ignored)

    n_rows : int
        The number of rows of subfigures to arrange for multiple graphs
    caption : string
        The caption string for the figure environment
    latex_label : string
        The latex label used for the figure for easy referral from the main text
    sub_captions : list of strings
        The sub_caption string for each subfigure in the figure
    sub_latex_labels : list of strings
        The latex label for each subfigure in the figure

    See Also
    ========
    to_latex
    """
    path.write(to_latex(Gbunch, **options))
