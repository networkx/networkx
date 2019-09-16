# -*- coding: utf-8 -*-
# Copyright (C) 2019 by
#   Luca Cappelletti <luca.cappelletti@studenti.unimi.it>
#
# All rights reserved.
# BSD license.
"""
*****
LaTeX
*****

Export NetworkX graphs in LaTeX format using Adigraph LaTeX library.

See Also
--------
Adigraph:      https://ctan.org/pkg/adigraph
"""
from typing import Dict, Tuple, List, Union
import os
import networkx as nx

__all__ = ["Adigraph"]

class Adigraph:
    def __init__(self,
                 row_size: int = 2,
                 vertices_color_fallback: str = "",
                 edges_color_fallback: str = "",
                 layout: Dict[str, Tuple[float, float]] = None,
                 weights: Dict[str, float] = None,
                 style: str = "",
                 directed: bool = True,
                 vertices_color: Dict[str, str] = None,
                 edges_color: Dict[str, str] = None,
                 vertices_width: Dict[str, float] = None,
                 edges_width: Dict[str, float] = None,
                 vertices_label: Dict[str, str] = None,
                 edges_label: Dict[str, str] = None,
                 sub_caption: str = "",
                 sub_label: str = "",
                 caption: str = "",
                 label: str = "",
                 ):
        """Render networkx graph into Latex Adigraph package.
            row_size: int=2, number of Adigraphs per row.
            vertices_color_fallback: str="", color to use when vertex color is not given.
            edges_color_fallback: str="", color to use when edge color is not given.
            layout: Dict[str, Tuple[float, float]]=None, layout to use when graph layour is not given. If both are not given, spring_layout is used.
            weights: Dict[str, float]=None, weights to use when the graph weights are not given.
            style: str="", style to use when graph style is not given.
            directed: bool = True, directed flag to use when graph directed flag is not given.
            vertices_color: Dict[str, str]=None, colors to use when graph vertices_color is not given.
            edges_color: Dict[str, str]=None, colors to use when graph edges_color is not given.
            vertices_width: Dict[str, float]=None, widths to use when graph edges_width is not given.
            edges_width: Dict[str, float]=None, widths to use when graph edges_width is not given.
            vertices_label: Dict[str, str]=None, labels to use when graph edges_label is not given.
            edges_label: Dict[str, str]=None, labels to use when graph edges_label is not given.
            sub_caption: str="", caption to use when graph caption is not given. Can contain `{i}` and `{n}`.
            sub_label: str="", label to use when graph label is not given. Can contain `{i}` and `{n}`.
            caption: str="", caption for figures
            label: str="", label for figures
        """
        self._load_placeholders()
        self._graphs = []
        self._row_size, self._default_vertices_color_fallback, self._default_edges_color_fallback, self._default_layout, self._default_weights, self._default_style, self._default_vertices_color, self._default_edges_color, self._default_vertices_width, self._default_edges_width, self._default_vertices_label, self._default_edges_label, self._default_caption, self._default_label, self._caption, self._label, self._default_directed = row_size, vertices_color_fallback, edges_color_fallback, layout, weights, style, vertices_color, edges_color, vertices_width, edges_width, vertices_label, edges_label, sub_caption, sub_label, caption, label, directed
        if weights is None:
            self._default_weights = {}
        if vertices_color is None:
            self._default_vertices_color = {}
        if edges_color is None:
            self._default_edges_color = {}
        if vertices_width is None:
            self._default_vertices_width = {}
        if edges_width is None:
            self._default_edges_width = {}
        if vertices_label is None:
            self._default_vertices_label = {}
        if edges_label is None:
            self._default_edges_label = {}
        self._vertices_color_fallbacks = []
        self._edges_color_fallbacks = []
        self._layouts = []
        self._directed = []
        self._weights = []
        self._styles = []
        self._vertices_color = []
        self._edges_color = []
        self._vertices_width = []
        self._edges_width = []
        self._vertices_label = []
        self._edges_label = []
        self._captions = []
        self._labels = []

    def _load_placeholder(self, path: str) -> str:
        """Return given file content.
            path: str, path for the file to load
        """
        with open(path, "r") as f:
            return f.read()

    def _load_placeholders(self):
        """Load placeholder files."""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self._document_placeholder = self._load_placeholder("{dir}/placeholders/document.tex".format(
            dir=script_dir))
        self._figure_placeholder = self._load_placeholder("{dir}/placeholders/figure.tex".format(
            dir=script_dir))
        self._subfigure_placeholder = self._load_placeholder("{dir}/placeholders/subfigure.tex".format(
            dir=script_dir))

    def _format(self, node: str, content: str) -> str:
        if content:
            return "\\{node}{{{content}}}".format(content=content, node=node)
        return ""

    def _get_caption(self, caption: str) -> str:
        return "\n\t"+self._format("caption", caption)

    def _get_label(self, label: str) -> str:
        return self._format("label", label)

    def _subfigure(self, i: int, adigraph: str, caption: str, label: str) -> str:
        """Return subfigure."""
        return self._subfigure_placeholder.format(
            content=adigraph,
            caption=self._get_caption(
                caption.format(i=i, n=len(self._graphs))),
            label=self._get_label(label.format(i=i, n=len(self._graphs))),
            size=1/self._row_size
        )

    def _figure(self, adigraphs: List[str], captions: List[str], labels: List[str]) -> str:
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

    def _vertex(self, vertex: str, x: float, y: float, color: str, width: float, label: str) -> str:
        """Return formatted vertex."""
        return "\n\t\t\t{vertex},{color},{width}:{x}\\textwidth,{y}\\textwidth:{label};".format(
            vertex=vertex,
            color=color,
            x=x/2,
            y=y/2,
            width=width,
            label=label
        )

    def _get(self, dict: Dict, key, default=""):
        return dict.get(key, default)

    def _simmetric_get(self, dict: Dict, key, directed: bool, default=""):
        if directed:
            return self._get(dict, key, default)
        return dict.get(key, dict.get(tuple(reversed(key)), default))

    def _vertices(self, vertices: List[str], layout: Dict[str, Tuple[float, float]], colors: Dict[str, str], default_color: str, widths: Dict[str, float], labels: Dict[str, str]) -> str:
        """Return given vertices in adigraph syntax."""
        return "".join([
            self._vertex(v, *layout[v], self._get(colors, v, default_color), self._get(widths, v), self._get(labels, v)) for v in vertices
        ])

    def _edge(self, start: str, end: str, weight: float, color: str, width: float, label: str) -> str:
        """Return formatted edge."""
        return "\n\t\t\t{start},{end},{color},{width}:{weight}:{label};".format(
            start=start,
            end=end,
            color=color,
            weight=weight,
            width=width,
            label=label
        )

    def _edges(self, edges: List[Tuple[str, str]], weights: Dict[str, float], colors: Dict[str, str], default_color: str, widths: Dict[str, float], labels: Dict[str, str], directed: bool) -> str:
        """Return given edges in adigraph syntax."""
        return "".join([
            self._edge(
                *e,
                self._simmetric_get(weights, e, directed=directed),
                self._simmetric_get(colors, e, directed, default_color),
                self._simmetric_get(widths, e, directed=directed),
                self._simmetric_get(labels, e, directed=directed)) for e in edges
        ])

    def _adigraph(
        self,
        graph: nx.Graph,
        layout: Dict[str, Tuple[float, float]],
        weights: Dict[str, float],
        style: str,
        directed: bool,
        vertices_color: Dict[str, str],
        vertices_color_fallback: str,
        edges_color: Dict[str, str],
        edges_color_fallback: str,
        vertices_width: Dict[str, float],
        edges_width: Dict[str, float],
        vertices_label: Dict[str, str],
        edges_label: Dict[str, str]
    ):
        """Return given graph in adigraph syntax."""
        return "\t\\NewAdigraph{{myAdigraph}}{{{vertices}\n\t\t}}{{{edges}\n\t\t}}[{style}]\n\t\t\\myAdigraph{{}}".format(
            vertices=self._vertices(
                graph.nodes, layout, vertices_color, vertices_color_fallback, vertices_width, vertices_label),
            edges=self._edges(graph.edges, weights, edges_color, edges_color_fallback,
                              edges_width, edges_label, directed),
            style=style
        )

    def _update_lists(self, arg: object, default: object, arg_list: List):
        if arg is None or arg == "":
            arg = default
        arg_list.append(arg)

    def add_graph(
            self,
            graph: nx.Graph,
            vertices_color_fallback: str = "",
            edges_color_fallback: str = "",
            layout: Dict[str, Tuple[float, float]] = None,
            weights: Dict[str, float] = None,
            style: str = "",
            directed: bool = None,
            vertices_color: Dict[str, str] = None,
            edges_color: Dict[str, str] = None,
            vertices_width: Dict[str, float] = None,
            edges_width: Dict[str, float] = None,
            vertices_label: Dict[str, str] = None,
            edges_label: Dict[str, str] = None,
            caption: str = "",
            label: str = "") -> str:
        """Add given graph to adigraph.
            graph: nx.Graph, graph to be added
            vertices_color_fallback: str="",  color to use when vertex color is not given.
            edges_color_fallback: str="", color to use when edge color is not given.
            layout: Dict[str, Tuple[float, float]]=None, layout for given graph. If None, default one is used. If default is None too, spring_layout is used.
            weights: Dict[str, float]=None, weights for given graph. If None, default ones are used.
            style: str="", style for given graph. If None, default one is used.
            directed: bool = None, directed flag for given graph. If None, default one is used.
            vertices_color: Dict[str, str]=None, vertices colors for given graph. If None, default ones are used.
            edges_color: Dict[str, str]=None, edges colors for given graph. If None, default ones are used.
            vertices_width: Dict[str, float]=None, vertices width for given graph. If None, default one is used.
            edges_width: Dict[str, float]=None, edges width for given graph. If None, default one is used.
            vertices_label: Dict[str, str]=None, vertices labels for given graph. If None, default ones are used.
            edges_label: Dict[str, str]=None, edges labels for given graph. If None, default ones are used.
            caption: str="", caption for given graph. If None, default one is used.
            label: str="" label for given graph. If None, default one is used.
        """
        if layout is None and self._default_layout is None:
            layout = nx.spring_layout(graph, iterations=10000)
        [
            self._update_lists(arg, default, arg_list) for arg, default, arg_list in (
                (
                    graph,
                    None,
                    self._graphs
                ),
                (
                    vertices_color_fallback,
                    self._default_vertices_color_fallback,
                    self._vertices_color_fallbacks
                ),
                (
                    edges_color_fallback,
                    self._default_edges_color_fallback,
                    self._edges_color_fallbacks
                ),
                (
                    layout,
                    self._default_layout,
                    self._layouts
                ),
                (
                    weights,
                    self._default_weights,
                    self._weights
                ),
                (
                    style,
                    self._default_style,
                    self._styles
                ),
                (
                    directed,
                    self._default_directed,
                    self._directed
                ),
                (
                    vertices_color,
                    self._default_vertices_color,
                    self._vertices_color
                ),
                (
                    edges_color,
                    self._default_edges_color,
                    self._edges_color
                ),
                (
                    vertices_width,
                    self._default_vertices_width,
                    self._vertices_width
                ),
                (
                    edges_width,
                    self._default_edges_width,
                    self._edges_width
                ),
                (
                    vertices_label,
                    self._default_vertices_label,
                    self._vertices_label
                ),
                (
                    edges_label,
                    self._default_edges_label,
                    self._edges_label
                ),
                (
                    caption,
                    self._default_caption,
                    self._captions
                ),
                (
                    label,
                    self._default_label,
                    self._labels
                )
            )
        ]

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
                    self._vertices_color,
                    self._vertices_color_fallbacks,
                    self._edges_color,
                    self._edges_color_fallbacks,
                    self._vertices_width,
                    self._edges_width,
                    self._vertices_label,
                    self._edges_label
                )
            ],
            self._captions,
            self._labels
        )

    __repr__ = __str__

    def save(self, path: str, document: bool = False):
        """Save Latex representation of current graph to given path.
            path: str, path where to save current Adigraph
            document: bool, whetever to wrap current Adigraph in a compilable document
        """
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(path, "w") as f:
            file = str(self)
            if document:
                file = self._body(file)
            f.write(file)
