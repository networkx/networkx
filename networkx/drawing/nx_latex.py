"""
*****
LaTeX
*****

Export NetworkX graphs in LaTeX format using Adigraph LaTeX library.

See Also
--------
Adigraph:      https://ctan.org/pkg/adigraph
"""
from typing import Dict, Tuple, List
import os
import networkx as nx

__all__ = ["Adigraph"]


class Adigraph:
    def __init__(self,
                 row_size: int = 2,
                 nodes_color_fallback: str = "",
                 edges_color_fallback: str = "",
                 layout: Dict[str, Tuple[float, float]] = None,
                 weights: Dict[str, float] = None,
                 style: str = "",
                 directed: bool = True,
                 nodes_color: Dict[str, str] = None,
                 edges_color: Dict[str, str] = None,
                 nodes_width: Dict[str, float] = None,
                 edges_width: Dict[str, float] = None,
                 nodes_label: Dict[str, str] = None,
                 edges_label: Dict[str, str] = None,
                 sub_caption: str = "",
                 sub_label: str = "",
                 caption: str = "",
                 label: str = "",
                 ):
        """Render networkx graph into Latex Adigraph package.

        Parameters
        ----------
        row_size: int=2
            number of Adigraphs per row.
        nodes_color_fallback: str=""
            color to use when node color is not given.
        edges_color_fallback: str=""
            color to use when edge color is not given.
        layout: Dict[str, Tuple[float, float]]=None
            layout to use when graph layour is not given.
            If both are not given, spring_layout is used.
        weights: Dict[str, float]=None
            weights to use when the graph weights are not given.
        style: str=""
            style to use when graph style is not given.
        directed: bool = True
            directed flag to use when graph directed flag is not given.
        nodes_color: Dict[str, str]=None
            colors to use when graph nodes_color is not given.
        edges_color: Dict[str, str]=None
            colors to use when graph edges_color is not given.
        nodes_width: Dict[str, float]=None
            widths to use when graph edges_width is not given.
        edges_width: Dict[str, float]=None
            widths to use when graph edges_width is not given.
        nodes_label: Dict[str, str]=None
            labels to use when graph edges_label is not given.
        edges_label: Dict[str, str]=None
            labels to use when graph edges_label is not given.
        sub_caption: str=""
            caption to use when graph caption is not given.
            Can contain `{i}` and `{n}`.
        sub_label: str=""
            label to use when graph label is not given.
            Can contain `{i}` and `{n}`.
        caption: str=""
            caption for figures
        label: str=""
            label for figures
        """
        self._load_placeholders()
        self._graphs = []

        self._row_size = row_size
        self._default_nodes_color_fallback = nodes_color_fallback
        self._default_edges_color_fallback = edges_color_fallback
        self._default_layout = layout
        self._default_weights = weights
        self._default_style = style
        self._default_nodes_color = nodes_color
        self._default_edges_color = edges_color
        self._default_nodes_width = nodes_width
        self._default_edges_width = edges_width
        self._default_nodes_label = nodes_label
        self._default_edges_label = edges_label
        self._default_caption = sub_caption
        self._default_label = sub_label
        self._caption = caption
        self._label = label
        self._default_directed = directed

        if weights is None:
            self._default_weights = {}
        if nodes_color is None:
            self._default_nodes_color = {}
        if edges_color is None:
            self._default_edges_color = {}
        if nodes_width is None:
            self._default_nodes_width = {}
        if edges_width is None:
            self._default_edges_width = {}
        if nodes_label is None:
            self._default_nodes_label = {}
        if edges_label is None:
            self._default_edges_label = {}

        self._nodes_color_fallbacks = []
        self._edges_color_fallbacks = []
        self._layouts = []
        self._directed = []
        self._weights = []
        self._styles = []
        self._nodes_color = []
        self._edges_color = []
        self._nodes_width = []
        self._edges_width = []
        self._nodes_label = []
        self._edges_label = []
        self._captions = []
        self._labels = []

    def _load_placeholders(self):
        """Load placeholder files."""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        dir = script_dir + "/placeholders/"
        with open(dir + "document.tex", "r") as f:
            self._document_placeholder = f.read()
        with open(dir + "figure.tex", "r") as f:
            self._figure_placeholder = f.read()
        with open(dir + "subfigure.tex", "r") as f:
            self._subfigure_placeholder = f.read()

    def _get_caption(self, caption: str) -> str:
        return f"\n\t\\caption{{{caption}}}" if caption else ""

    def _get_label(self, label: str) -> str:
        return f"\\label{{{label}}}" if label else ""

    def _subfigure(self, i: int, adigraph: str, caption: str,
                   label: str) -> str:
        """Return subfigure."""
        return self._subfigure_placeholder.format(
            content=adigraph,
            caption=self._get_caption(caption.format(i=i, n=len(self._graphs))),
            label=self._get_label(label.format(i=i, n=len(self._graphs))),
            size=1 / self._row_size
        )

    def _figure(self, adigraphs: List[str], captions: List[str],
                labels: List[str]) -> str:
        """Return set of subfigures."""
        return self._figure_placeholder.format(
            content="\n".join([
                self._subfigure(i, a, c, l) for i, (a, c, l) in enumerate(zip(
                    adigraphs,
                    captions,
                    labels
                ), 1)
            ]),
            caption=self._get_caption(self._caption),
            label=self._get_label(self._label),
        )

    def _body(self, content: str) -> str:
        """Return working Latex document with given content."""
        return self._document_placeholder.format(content=content)

    def _node(self, node: str, x: float, y: float, color: str,
              width: float, label: str) -> str:
        """Return formatted node."""
        return (f"\n\t\t\t{node},{color},{width}:{x/2}"
                f"\\textwidth,{y/2}\\textwidth:{label};"
                )

    def _get(self, dict: Dict, key, default=""):
        return dict.get(key, default)

    def _symmetric_get(self, dict: Dict, key, directed: bool, default=""):
        if directed:
            return self._get(dict, key, default)
        return dict.get(key, dict.get(tuple(reversed(key)), default))

    def _nodes(self,
               nodes: List[str],
               layout: Dict[str, Tuple[float, float]],
               colors: Dict[str, str],
               default_color: str,
               widths: Dict[str, float],
               labels: Dict[str, str],
               ) -> str:
        """Return given nodes in adigraph syntax."""
        return "".join(
            [self._node(v, *layout[v], self._get(colors, v, default_color),
                       self._get(widths, v), self._get(labels, v))
            for v in nodes
            ])

    def _edge(self, start: str, end: str, weight: float,
              color: str, width: float, label: str) -> str:
        """Return formatted edge."""
        return f"\n\t\t\t{start},{end},{color},{width}:{weight}:{label};"

    def _edges(self, edges: List[Tuple[str, str]], weights: Dict[str, float],
               colors: Dict[str, str], default_color: str,
               widths: Dict[str, float], labels: Dict[str, str],
               directed: bool
               ) -> str:
        """Return given edges in adigraph syntax."""
        return "".join(
            [self._edge(
                *e,
                self._symmetric_get(weights, e, directed=directed),
                self._symmetric_get(colors, e, directed, default_color),
                self._symmetric_get(widths, e, directed=directed),
                self._symmetric_get(labels, e, directed=directed))
            for e in edges
            ])

    def _adigraph(
        self,
        graph: nx.Graph,
        layout: Dict[str, Tuple[float, float]],
        weights: Dict[str, float],
        style: str,
        directed: bool,
        nodes_color: Dict[str, str],
        nodes_color_fallback: str,
        edges_color: Dict[str, str],
        edges_color_fallback: str,
        nodes_width: Dict[str, float],
        edges_width: Dict[str, float],
        nodes_label: Dict[str, str],
        edges_label: Dict[str, str]
    ):
        """Return given graph in adigraph syntax."""
        nodes = self._nodes(graph.nodes, layout, nodes_color,
                            nodes_color_fallback, nodes_width,
                            nodes_label)
        edges = self._edges(graph.edges, weights, edges_color,
                            edges_color_fallback, edges_width,
                            edges_label, directed)

        return (f"\t\\NewAdigraph{{myAdigraph}}{{{nodes}\n\t\t}}"
                f"{{{edges}\n\t\t}}[{style}]\n\t\t\\myAdigraph{{}}"
                )

    def add_graph(
            self,
            graph: nx.Graph,
            nodes_color_fallback: str = "",
            edges_color_fallback: str = "",
            layout: Dict[str, Tuple[float, float]] = None,
            weights: Dict[str, float] = None,
            style: str = "",
            directed: bool = None,
            nodes_color: Dict[str, str] = None,
            edges_color: Dict[str, str] = None,
            nodes_width: Dict[str, float] = None,
            edges_width: Dict[str, float] = None,
            nodes_label: Dict[str, str] = None,
            edges_label: Dict[str, str] = None,
            caption: str = "",
            label: str = "") -> str:
        """Add given graph to adigraph.

        Parameters
        ----------
        graph: nx.Graph
            graph to be added
        nodes_color_fallback: str=""
            color to use when node color is not given.
        edges_color_fallback: str=""
            color to use when edge color is not given.
        layout: Dict[str, Tuple[float, float]]=None
            layout for given graph. If None, default one is used.
            If default is None too, spring_layout is used.
        weights: Dict[str, float]=None
            weights for given graph. If None, default ones are used.
        style: str=""
            style for given graph. If None, default one is used.
        directed: bool = None
            directed flag for given graph. If None, default one is used.
        nodes_color: Dict[str, str]=None
            nodes colors for given graph. If None, default ones are used.
        edges_color: Dict[str, str]=None
            edges colors for given graph. If None, default ones are used.
        nodes_width: Dict[str, float]=None
            nodes width for given graph. If None, default one is used.
        edges_width: Dict[str, float]=None
            edges width for given graph. If None, default one is used.
        nodes_label: Dict[str, str]=None
            nodes labels for given graph. If None, default ones are used.
        edges_label: Dict[str, str]=None
            edges labels for given graph. If None, default ones are used.
        caption: str=""
            caption for given graph. If None, default one is used.
        label: str=""
            label for given graph. If None, default one is used.
        """
        if layout is None and self._default_layout is None:
            layout = nx.spring_layout(graph, iterations=10000)

        arg_values = [
            (graph, None, self._graphs),
            (layout, self._default_layout, self._layouts),
            (weights, self._default_weights, self._weights),
            (style, self._default_style, self._styles),
            (directed, self._default_directed, self._directed),
            (edges_color_fallback, self._default_edges_color_fallback, self._edges_color_fallbacks),
            (edges_color, self._default_edges_color, self._edges_color),
            (edges_width, self._default_edges_width, self._edges_width),
            (edges_label, self._default_edges_label, self._edges_label),
            (nodes_color_fallback, self._default_nodes_color_fallback, self._nodes_color_fallbacks),
            (nodes_color, self._default_nodes_color, self._nodes_color),
            (nodes_width, self._default_nodes_width, self._nodes_width),
            (nodes_label, self._default_nodes_label, self._nodes_label),
            (caption, self._default_caption, self._captions),
            (label, self._default_label, self._labels),
        ]

        for arg, default, arg_list in arg_values:
            if arg is None or arg == "":
                arg = default
            arg_list.append(arg)

    def __str__(self):
        """Return Latex representation of current Adigraph."""
        return self._figure(
            [
                self._adigraph(*G) for G in zip(
                    self._graphs,
                    self._layouts,
                    self._weights,
                    self._styles,
                    self._directed,
                    self._nodes_color,
                    self._nodes_color_fallbacks,
                    self._edges_color,
                    self._edges_color_fallbacks,
                    self._nodes_width,
                    self._edges_width,
                    self._nodes_label,
                    self._edges_label
                )
            ],
            self._captions,
            self._labels
        )

    __repr__ = __str__

    def save(self, path: str, document: bool = False):
        """Save Latex representation of current graph to given path.

        Parameters
        ----------
        path: str
            path where to save current Adigraph
        document: bool
            whetever to wrap current Adigraph in a compilable document
        """
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "w") as f:
            file = str(self)
            if document:
                file = self._body(file)
            f.write(file)
