from typing import Any, Dict, Generic, Iterable

from networkx.classes.coreviews import AdjacencyView
from networkx.classes.graph import Graph, _Node
from networkx.classes.reportviews import (
    InDegreeView,
    InEdgeView,
    InMultiDegreeView,
    OutDegreeView,
    OutEdgeView,
    OutMultiDegreeView,
)

class DiGraph(Graph[_Node], Generic[_Node]):
    succ: AdjacencyView[_Node, _Node, Dict[str, Any]]
    pred: AdjacencyView[_Node, _Node, Dict[str, Any]]
    def has_successor(self, u: _Node, v: _Node) -> bool: ...
    def has_predecessor(self, u: _Node, v: _Node) -> bool: ...
    def successors(self, n: _Node) -> Iterable[_Node]: ...
    def predecessors(self, n: _Node) -> Iterable[_Node]: ...
    in_edges: InEdgeView[_Node]
    in_degree: InDegreeView[_Node] | InMultiDegreeView[
        _Node
    ]  # ugly hack to make MultiDiGraph work
    out_edges: OutEdgeView[_Node]
    out_degree: OutDegreeView[_Node] | OutMultiDegreeView[
        _Node
    ]  # ugly hack to make MultiDiGraph work
    def reverse(self, copy: bool = ...) -> DiGraph[_Node]: ...
    def copy(self, as_view: bool = ...) -> DiGraph[_Node]: ...
    def to_undirected(self, reciprocal: bool = ..., as_view: bool = ...) -> Graph[_Node]: ...  # type: ignore
