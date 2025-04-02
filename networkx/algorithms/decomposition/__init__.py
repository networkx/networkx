"""Graph decomposition algorithms.

Graph decomposition algorithms constitute a family of algorithms that divide the
input graph into a series of subgraphs, as opposed to traditional clustering or
partitioning algorithms that do not provide such a guarantee. For example, a
graph can be decomposed in a series of paths (i.e., *path decomposition* [1]_),
in a series of modules (i.e., *modular decomposition* [2]_) and others.

References
----------
.. [1] https://en.wikipedia.org/wiki/Pathwidth
.. [2] https://en.wikipedia.org/wiki/Modular_decomposition

"""

from networkx.algorithms.decomposition.modular_decomposition import modular_decomposition
