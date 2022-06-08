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

If you want subfigures each containing one graph, you can use write_latex
or the class AdigraphCollection.

>>> H1 = nx.path_graph(4)
>>> H2 = nx.complete_graph(4)
>>> H3 = nx.path_graph(8)
>>> H4 = nx.complete_graph(8)
>>> captions = ["Path on 4 nodes", "Complete graph on 4 nodes", "Path on 8 nodes", "Complete graph on 8 nodes"]
>>> labels = ["fig2a", "fig2b", "fig2c", "fig2d"]
>>> nx.write_latex([H1, H2, H3, H4], "subfigures.tex", n_rows=2, sub_captions=captions, sub_labels=labels)

>>> ADC = nx.AdigraphCollection()
>>> ADC.add_graph(H1, sub_caption="Path on 4 nodes", sub_label="fig2a")
>>> ADC.add_graph(H2, sub_caption="Complete graph on 4 nodes", sub_label="fig2b")
>>> ADC.add_graph(H3, sub_caption="Path on 8 nodes", sub_label="fig2c")
>>> ADC.add_graph(H4, sub_caption="Complete graph on 8 nodes", sub_label="fig2d")
>>> latex_code = ADC.to_latex_document()

>>> node_color = {0: "red", 1: "orange", 2: "blue", 3: "gray!90"}
>>> edge_width = {e: 1.5 for e in H3.edges}
>>> pos = nx.spring_layout(H3, seed=42)
>>> latex_code = nx.to_latex(H3, pos=pos, node_color=node_color, edge_width=edge_width)
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

__all__ = ["to_latex", "write_latex", "Adigraph", "AdigraphCollection"]


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
        as_document=True,
        n_rows=1,
        caption="",
        latex_label="",
        sub_captions=None,
        sub_labels=None,
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
    pos : dict
    default_node_color : string
    default_edge_color : string
    node_color : string or dict
    edge_color : string or dict
    node_width : string or dict
    edge_width : string or dict
    node_label : string or dict
    edge_label : string or dict
    as_document : bool
        Whether to wrap the latex code in a document envionment for compiling
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

    Returns
    =======
    latex_code : string
        The text string which draws the desired graph(s) when compiled by LaTeX.

    See Also
    ========
    write_latex
    """
    if hasattr(Gbunch, "adj"):
        pos = pos if pos is not None else nx.spring_layout(Gbunch, seed=42)
        ADI_all = Adigraph(Gbunch, pos)
        if as_document:
            fig = ADI_all.to_latex_document(caption, latex_label)
        else:
            fig = ADI_all.to_latex_figure(caption, latex_label)
    else:
        ADI_all = AdigraphCollection(Gbunch, sub_captions=sub_captions, sub_labels=sub_labels)
        if as_document:
            fig = ADI_all.to_latex_document(n_rows, caption, latex_label)
        else:
            fig = ADI_all.to_latex_figure(n_rows, caption, latex_label)
    return fig


@nx.utils.open_file(1, mode="w")
def write_latex(Gbunch, path, as_document=False, **options):
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
    path.write(to_latex(Gbunch, as_document=as_document, **options))


def _make_node_attr_dict(attr, nodes, default):
    if attr is None or isinstance(attr, str):
        return dict(nodes(data=attr, default=default))
    return {x: attr.get(x, default) for x in nodes}


def _make_edge_attr_dict(attr, edges, default):
    if attr is None or isinstance(attr, str):
        return dict((e[:-1], e[-1]) for e in edges(data=attr, default=default))
    return {x: attr.get(x, default) for x in edges}


_DOCUMENT_PLACEHOLDER = r"""\documentclass{{report}}
\usepackage{{adigraph}}
\usepackage{{subcaption}}

\begin{{document}}
{content}
\end{{document}}"""


_FIGURE_PLACEHOLDER = r"""\begin{{figure}}
{content}{caption}{label}
\end{{figure}}"""


_SUBFIGURE_PLACEHOLDER = r"""    \begin{{subfigure}}{{{size}\textwidth}}
    {content}{caption}{label}
    \end{{subfigure}}"""


class Adigraph:
    """Render networkx graph into Latex Adigraph package.

    Parameters
    ----------
    G : NetworkX graph
        Graph to format in latex
    pos : dict or None
        A dict keyed by node to 2-array indicating position.
        If None, nx.spring_layout is used to generate it.
    style : str
        style to use in adigraph (e.g. "", "-", "dashed")
    default_node_color : str, default="red"
        color to use when node color is not given.
    default_edge_color : str, default="black"
        color to use when edge color is not given.
    node_color : attr_name or dict
        When node_color is a string it indicates which node attribute
        name holds the color for each node. When a dict, it is keyed by
        node to the color for that node.
    edge_color : str or dict
        When edge_color is a string it indicates which edge attribute
        name holds the color for each edge. When a dict, it is keyed by
        edge to the color for that edge.
    node_width : str or dict
        When node_width is a string it indicates which node attribute
        name holds the width for each node. When a dict, it is keyed by
        node to the width for that node.
    edge_width : str or dict
        When edge_width is a string it indicates which edge attribute
        name holds the width for each edge. When a dict, it is keyed by
        edge to the width for that edge.
    node_label : str or dict
        When node_label is a string it indicates which node attribute
        name holds the label for each node. When a dict, it is keyed by
        node to the label for that node.
    edge_label : str or dict
        When edge_label is a string it indicates which edge attribute
        name holds the label for each edge. When a dict, it is keyed by
        edge to the label for that edge.
    """
    def __str__(self):
        return self.to_latex_raw()

    __repr__ = __str__
    _SUBFIGURE_PLACEHOLDER = _SUBFIGURE_PLACEHOLDER
    _FIGURE_PLACEHOLDER = _FIGURE_PLACEHOLDER
    _DOCUMENT_PLACEHOLDER = _DOCUMENT_PLACEHOLDER

    def __init__(
        self,
        G,
        pos=None,
        style="",
        default_node_color=None,
        default_edge_color=None,
        node_color=None,
        edge_color=None,
        node_width=None,
        edge_width=None,
        node_label=None,
        edge_label=None,
    ):
        self.G = G
        self.pos = pos if pos is not None else nx.spring_layout(G)
        self.style = style

        self.node_color = _make_node_attr_dict(node_color, G.nodes, default_node_color)
        self.node_width = _make_node_attr_dict(node_width, G.nodes, "")
        self.node_label = _make_node_attr_dict(node_label, G.nodes, "")

        self.edge_color = _make_edge_attr_dict(edge_color, G.edges, default_edge_color)
        self.edge_width = _make_edge_attr_dict(edge_width, G.edges, "")
        self.edge_label = _make_edge_attr_dict(edge_label, G.edges, "")

    def to_latex_raw(self):
        # indent nicely
        i4 = "\n    "
        i8 = "\n        "
        i12 = "\n            "

        result = "    \\NewAdigraph{myAdigraph}{"
        for n in self.G:
            x, y = self.pos[n]
            clr = self.node_color[n]
            wth = self.node_width[n]
            lbl = self.node_label[n]
            result += i12 + f"{n},{clr},{wth}:{x/2}\\textwidth,{y/2}\\textwidth:{lbl};"

        edge_color = self.edge_color
        edge_width = self.edge_width
        edge_label = self.edge_label
        result += i8 + "}{"
        for e in self.G.edges:
            u, v = e
            reverse_e = v, u
            color = edge_color[e] if e in edge_color else edge_color[reverse_e]
            width = edge_width[e] if e in edge_label else edge_label[reverse_e]
            label = edge_label[e] if e in edge_width else edge_width[reverse_e]
            result += i12 + f"{e[0]},{e[1]},{color},{width}::{label};"

        result += i8 + f"}}[{self.style}]" + i8 + "\\myAdigraph{}"
        return result

    def to_latex_document(self, caption="", latex_label=""):
        fig = self.to_latex_figure(caption, latex_label)
        return self._DOCUMENT_PLACEHOLDER.format(content=fig)

    def to_latex_figure(self, caption="", latex_label=""):
        raw = self.to_latex_raw()
        cap = f"    \\caption{{{caption}}}" if caption else ""
        lbl = f"\\label{{{latex_label}}}" if latex_label else ""
        return self._FIGURE_PLACEHOLDER.format(content=raw, caption=cap, label=lbl)

    def to_latex_subfigure(self, size=1, caption="", latex_label=""):
        raw = self.to_latex_raw()
        cap = f"\n    \\caption{{{caption}}}" if caption else ""
        lbl = f"\\label{{{latex_label}}}" if latex_label else ""
        sbf = self._SUBFIGURE_PLACEHOLDER
        return sbf.format(size=size, content=raw, caption=cap, label=lbl)


class AdigraphCollection:
    """Render multiple networkx graphs into Latex Adigraph package.

    Parameters
    ----------
    G : iterable of NetworkX graphs or Adigraphs
        The list of graphs to render in latex
    pos : dict or None
        A dict keyed by node to 2-array indicating position.
        If None, nx.spring_layout is used to generate it.
    style : str
        style to use in adigraph (e.g. "", "-", "dashed")
    default_node_color : str, default="red"
        color to use when node color is not given.
    default_edge_color : str, default="black"
        color to use when edge color is not given.
    node_color : attr_name or dict
        When node_color is a string it indicates which node attribute
        name holds the color for each node. When a dict, it is keyed by
        node to the color for that node.
    edge_color : str or dict
        When edge_color is a string it indicates which edge attribute
        name holds the color for each edge. When a dict, it is keyed by
        edge to the color for that edge.
    node_width : str or dict
        When node_width is a string it indicates which node attribute
        name holds the width for each node. When a dict, it is keyed by
        node to the width for that node.
    edge_width : str or dict
        When edge_width is a string it indicates which edge attribute
        name holds the width for each edge. When a dict, it is keyed by
        edge to the width for that edge.
    node_label : str or dict
        When node_label is a string it indicates which node attribute
        name holds the label for each node. When a dict, it is keyed by
        node to the label for that node.
    edge_label : str or dict
        When edge_label is a string it indicates which edge attribute
        name holds the label for each edge. When a dict, it is keyed by
        edge to the label for that edge.
    sub_caption : str (default="")
        The LaTeX string to be used as the caption of subfigures if not provided
    sub_label : str (default="")
        The LaTeX string to be used as the label of subfigures if not provided
    sub_captions : list of strings or None
        A list of caption strings for each graph in Gbunch.
    sub_labels : list of strings or None
        A list of label strings for each graph in Gbunch.
    caption : str (default="")
        The LaTeX string to be used as the caption of the figure
    label : str (default="")
        The LaTeX string to be used as the label of the figure
    """
    _SUBFIGURE_PLACEHOLDER = _SUBFIGURE_PLACEHOLDER
    _FIGURE_PLACEHOLDER = _FIGURE_PLACEHOLDER
    _DOCUMENT_PLACEHOLDER = _DOCUMENT_PLACEHOLDER

    def __init__(
        self,
        Gbunch=None,
        pos=None,
        style="",
        default_node_color="red",
        default_edge_color="black",
        node_color="color",
        edge_color="color",
        node_width="width",
        edge_width="width",
        node_label="",
        edge_label="",
        sub_caption="",
        sub_label="",
        sub_captions=None,
        sub_labels=None,
        caption="",
        label="",
    ):
        self.options = dict(
            pos=pos,
            style=style,
            default_node_color=default_node_color,
            default_edge_color=default_edge_color,
            node_color=node_color,
            edge_color=edge_color,
            node_width=node_width,
            edge_width=edge_width,
            node_label=node_label,
            edge_label=edge_label,
        )
        if Gbunch is None:
            Gbunch = []
        self.graphs = [(Adigraph(G, **self.options) if hasattr(G, "adj") else G) for G in Gbunch]
        self.sub_captions = [] if sub_captions is None else sub_captions
        self.sub_labels =  [] if sub_labels is None else sub_labels
        self.sub_caption = sub_caption
        self.sub_label = sub_label
        self.caption = caption
        self.label = label

    def add_graph(
            self,
            graph,
            pos=None,
            style=None,
            default_node_color=None,
            default_edge_color=None,
            node_color=None,
            edge_color=None,
            node_width=None,
            edge_width=None,
            node_label=None,
            edge_label=None,
            sub_caption="",
            sub_label=""
        ):
        opts = {}
        for k, v in self.options.items():
            new = eval(k)
            opts[k] = new if new is not None else v
        #opts = {k: (eval(k) if eval(k) else v) for k, v in self.options.items()}
        if hasattr(graph, "adj"):
            if graph.is_multigraph():
                raise nx.NetworkXError("Multigraphs not supported for Adigraph.add_graph")
            self.graphs.append(Adigraph(graph, **opts))
        else:
            self.graphs.append(graph)
        self.sub_captions.append(sub_caption if sub_caption else self.sub_caption)
        self.sub_labels.append(sub_label if sub_label else self.sub_label)

    def to_latex_subfigures(self, n_rows=1, captions=None, latex_labels=None):
        N = len(self.graphs)
        size = 1 / n_rows
        if captions is None:
            captions = self.sub_captions
        if latex_labels is None:
            latex_labels = self.sub_labels

        result = ""
        for i, (ADIG, cap, lbl) in enumerate(zip(self.graphs, captions, latex_labels)):
            caption = cap.format(i=i + 1, n=N)
            latex_label = lbl.format(i=i + 1, n=N)
            if i > 0:
                result += "\n"
            result += ADIG.to_latex_subfigure(size, caption, latex_label)
        return result

    def to_latex_figure(self, n_rows=1, caption="", latex_label=""):
        raw = self.to_latex_subfigures(n_rows)
        caption = caption if caption else self.caption
        cap = f"\n    \\caption{{{caption}}}" if caption else ""
        latex_label = latex_label if latex_label else self.label
        lbl = f"\\label{{{latex_label}}}" if latex_label else ""
        return self._FIGURE_PLACEHOLDER.format(content=raw, caption=cap, label=lbl)

    def to_latex_document(self, n_rows=1, caption="", latex_label=""):
        fig = self.to_latex_figure(n_rows, caption, latex_label)
        return self._DOCUMENT_PLACEHOLDER.format(content=fig)
