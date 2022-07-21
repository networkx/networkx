from typing import Dict, Generic, Optional

from _typeshed import Incomplete

from networkx.classes.graph import Graph, _Node
from networkx.classes.multidigraph import MultiDiGraph

class MultiGraph(Graph[_Node], Generic[_Node]):
    def __init__(self, incoming_graph_data: Data[_Node] | None = ..., multigraph_input: Incomplete | None = ..., **attr: Any) -> None: ...  # type: ignore
    def new_edge_key(self, u: _Node, v: _Node) -> int: ...
    def copy(self, as_view: bool = ...) -> MultiGraph[_Node]: ...
    def to_directed(self, as_view: bool = ...) -> MultiDiGraph[_Node]: ...
    def to_undirected(self, as_view: bool = ...) -> MultiGraph[_Node]: ...
    def number_of_edges(
        self, u: Optional[_Node] = ..., v: Optional[_Node] = ...
    ) -> int: ...
    edge_key_dict_factory: Incomplete
    def add_edge(self, u_for_edge: _Node, v_for_edge: _Node, key: str | None = ..., **attr: Any): ...  # type: ignore
    def get_edge_data(self, u: _Node, v: _Node, key: str | None = ..., default: Any = ...): ...  # type: ignore
    def has_edge(self, u: _Node, v: _node, key: str | None = ...): ...  # type: ignore
    def remove_edge(self, u: _Node, v: _Node, key: str | None = ...): ...  # type: ignore
