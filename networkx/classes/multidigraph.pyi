from networkx.classes.digraph import DiGraph
from networkx.classes.graph import _Node
from networkx.classes.multigraph import MultiGraph
from networkx.classes.reportviews import (
    InMultiDegreeView,
    MultiDegreeView,
    OutMultiDegreeView,
)

class MultiDiGraph(MultiGraph[_Node], DiGraph[_Node]):
    degree: MultiDegreeView[_Node]
    in_degree: InMultiDegreeView[_Node]
    out_degree: OutMultiDegreeView[_Node]
    def to_undirected(self, reciprocal: bool = ..., as_view: bool = ...) -> MultiGraph[_Node]: ...  # type: ignore
    def reverse(self, copy: bool = ...) -> MultiDiGraph[_Node]: ...
    def copy(self, as_view: bool = ...) -> MultiDiGraph[_Node]: ...
