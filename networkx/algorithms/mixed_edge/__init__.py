"""
Subpackages related to mixed-edge graphs.

In graph theory, a mixed-edge graph contains edges of different types. For
example, a graph can contain directed and undirected edges in a Markov equivalence
class of a specific type of causal graph [1]_.

References
----------
.. [1] https://en.wikipedia.org/wiki/Mixed_graph
"""

from networkx.algorithms.mixed_edge.mixed_edge_moral import mixed_edge_moral_graph
from networkx.algorithms.mixed_edge.m_separation import (
    m_separated,
    is_minimal_m_separator,
    minimal_m_separator,
)

__all__ = [
    "mixed_edge_moral_graph",
    "m_separated",
    "is_minimal_m_separator",
    "minimal_m_separator",
]
