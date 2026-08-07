# This file contains a draft version of highlights for the next release.
# While not part of the automated release process, it could be in the future.

Highlights for release 3.7

- Leiden based community detection algorithms are now supported via
  `leiden_communities` and `leiden_partitions`. This provides an
  alternative, often improved, community detection algorithm compared
  to the Louvain functions.

- The isomorphism checking suite of tools has been upgraded. The
  ISMAGS symmetry aware isomorphism and subgraph isomorphism checking
  tools now support directed and multigraph Graphs. The VF2++ functions
  now provide subgraph isomorphism and subgraph monomorphism checking.

- The pygraphviz library is now provided via `pip` with wheels that
  include the GraphViz binaries. This should make the NetworkX interface
  to pygraphviz easier to use for graph layout and rendering.
