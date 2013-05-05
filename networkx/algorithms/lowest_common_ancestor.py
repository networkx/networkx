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

def lowest_common_ancestor_naive(G, root, node1, node2):
  """Compute the lowest common ancestor for two nodes in a graph.

  Parameters
  ----------
  G : NetworkX directed graph

  root : node
    The node to use as a root for the purposes of defining "lowest". We find
    the node with the longest shortest path to the root that is a common
    ancestor of node1 and node2.

  node1, node2 : node
    The two nodes to find an ancestor of.

  Returns
  -------
  The lowest common ancestor of node1 and node2 with respect to root or None
  if one does not exist. If an ancestor is not reachable from root, it is not
  considered a potential lca. Ties are broken arbitrarily. Note that this
  does NOT imply that n will be returned as lca(n, n), only that the value
  returned is at no lesser a depth than n

  Notes
  -----
  Only defined on directed acyclic graphs. This implementation is designed to
  be efficient for only extremely small numbers of queries (think 1). You should
  use lowest_common_ancestor unless you are sure this is what you want.

  Operates by generating all shortest paths ending at the nodes and taking their
  intersection, then returning the member with the longest shortest path from
  root.

  See Also
  --------
  lowest_common_ancestor
  all_pairs_lowest_common_ancestor
  tree_all_pairs_lowest_common_ancestor
  """

  feasible = all_lowest_common_ancestors_naive(G, root, node1, node2)
  if not feasible:
    return None
  else:
    return feasible.pop()

def all_lowest_common_ancestors_naive(G, root, node1, node2):
  """As lowest_common_ancestor_naive except returns the (potentially empty)
  set of all lowest common ancestors instead of just one."""

  # Find all common ancestors.
  ancestors1 = nx.dag.ancestors(G, node1)
  ancestors1.add(node1)
  ancestors2 = nx.dag.ancestors(G, node2)
  ancestors2.add(node2)

  depths = nx.shortest_path_length(G, source=root)

  feasible = ancestors1.intersection(ancestors2)
  maximal_depth = max((depths[n] for n in feasible))
  return set((n for n in feasible if depths[n] == maximal_depth))
