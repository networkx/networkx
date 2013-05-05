import networkx as nx
import itertools
import collections

__authors__ = "\n".join(["Alex Roper <aroper@umich.edu>"])
#   Copyright (C) 2013 by
#   Alex Roper <aroper@umich.edu>
#   All rights reserved.
#   BSD license.

def tree_all_pairs_lowest_common_ancestors(G, root=None, pairs=None):
  """Compute the lowest common ancestor for a set of pairs in the graph.

  Parameters
  ----------
  G : NetworkX directed graph

  root : node, optional
    The root of the subtree to operate on. If None, will assume the entire graph
    has exactly one source and use that.

  pairs : container of pairs of nodes, optional
    The pairs of interest. Defaults to all pairs under the root that have a
    lowest common ancestor.

  Returns
  -------
  lcas : generator of tuples ((u, v), lca) where u and v are nodes in pairs and
         lca is their least common ancestor.

  Notes
  -----
  Only defined on trees represented with directed edges from parents to
  children. Uses Tarjan's off-line least-common-ancestors algorithm.

  Tarjan, R. E. (1979), "Applications of path compression on balanced trees",
  Journal of the ACM 26 (4): 690-715, doi:10.1145/322154.322161.

  See Also
  --------
  """

  if not G.is_directed():
    raise nx.NetworkXError("Lowest common ancestor not defined on undirected "
                           "graphs.")

  # Index pairs of interest for efficient lookup from either side.
  if pairs is not None:
    pair_dict = collections.defaultdict(list)
    for u, v in pairs:
      pair_dict[u].append(v)
      pair_dict[v].append(u)
    pairs = pair_dict

  # If root is not specified, find the exactly one node with in degree 0 and
  # use it. Raise an error if none are found, or more than one is. Also check
  # for any nodes with in degree larger than 1, which would imply G is not a
  # tree.
  if root is None:
    for n in G:
      if G.in_degree(n) == 0:
        if root is not None:
          raise NetworkXError("Graph must have exactly one source unless you "
                              "provide a root.")
        root = n
      elif G.in_degree(n) > 1:
        raise NetworkXError("Tree LCA only defined on trees; use DAG routine "
                            "for DAGs.")
  if root is None:
    raise NetworkXError("Tree LCA only defined on trees; use DAG routine "
                        "for DAGs.")

  # Iterative implementation of Tarjan's offline lca algorithm as described in
  # CLRS on page 521.
  uf = nx.utils.union_find.UnionFind()
  ancestors = {}
  for node in G.nodes_iter():
    ancestors[node] = uf[node]
  colors = collections.defaultdict(bool)
  for node in nx.depth_first_search.dfs_postorder_nodes(G, root):
    colors[node] = True
    for v in (pairs[node] if pairs else G.nodes_iter()):
      if colors[v]:
        yield (node, v), ancestors[uf[v]]
    if node != root:
      parent = G.predecessors(node)[0]
      uf.union(parent, node)
      ancestors[uf[parent]] = parent
