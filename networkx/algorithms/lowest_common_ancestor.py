import networkx as nx
import itertools
import collections

__authors__ = "\n".join(["Alex Roper <aroper@umich.edu>"])
#   Copyright (C) 2013 by
#   Alex Roper <aroper@umich.edu>
#   All rights reserved.
#   BSD license.

__all__ = ["LCAPrecomputation", "all_pairs_lowest_common_ancestor",
           "lowest_common_ancestor_naive", "tree_all_pairs_lowest_common_ancestors"]

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
  Only defined on non-null trees represented with directed edges from parents to
  children. Uses Tarjan's off-line least-common-ancestors algorithm.

  Tarjan, R. E. (1979), "Applications of path compression on balanced trees",
  Journal of the ACM 26 (4): 690-715, doi:10.1145/322154.322161.

  See Also
  --------
  """

  if not G:
     raise nx.NetworkXPointlessConcept("LCA meaningless on null graphs.")

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
          raise nx.NetworkXError("Tree must have exactly one source unless you "
                                 "provide a root.")
        root = n
      elif G.in_degree(n) > 1:
        raise nx.NetworkXError("Tree LCA only defined on trees; use DAG routine "
                               "for DAGs.")
  if root is None:
    raise nx.NetworkXError("Tree LCA only defined on trees; use DAG routine "
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
  returned is at no lesser a depth than n.

  Will raise NetworkXUnfeasible if there is no lca reachable from root.

  Notes
  -----
  Only defined on non-null directed acyclic graphs. This implementation is
  designed to be efficient for only extremely small numbers of queries
  (think 1). You should really use LCAPrecomputation or
  all_pairs_lowest_common_ancestor unless you are sure this is what you want.

  Operates by generating all shortest paths ending at the nodes and taking their
  intersection, then returning the member with the longest shortest path from
  root.

  See Also
  --------
  lowest_common_ancestor
  all_pairs_lowest_common_ancestor
  tree_all_pairs_lowest_common_ancestor
  """

  # Find all common ancestors.
  ancestors1 = nx.dag.ancestors(G, node1)
  ancestors1.add(node1)
  ancestors2 = nx.dag.ancestors(G, node2)
  ancestors2.add(node2)

  depths = nx.shortest_path_length(G, source=root)

  feasible = ancestors1.intersection(ancestors2)
  if feasible:
    return max(feasible, key=depths.get)
  else:
    raise nx.NetworkXUnfeasible("Pair has no common ancestors that are "
                                "reachable from the provided root.")

def all_pairs_lowest_common_ancestor(G, root=None, pairs=None):
  """Returns an iterator over ((n1, n2), lca) where (n1, n2) are all pairs of
  nodes and lca is a lowest common ancestor of the pair."""
  return LCAPrecomputation(G, root).all_pairs_lowest_common_ancestor(pairs)

class LCAPrecomputation(object):
  def __init__(self, G, root=None):
    if not nx.is_directed_acyclic_graph(G):
      raise nx.NetworkXError("LCA only defined on directed acyclic graphs.")
    elif not G:
      raise nx.NetworkXPointlessConcept("LCA meaningless on null graphs.")
    if root is None:
      for n in G:
        if G.in_degree(n) == 0:
          if root is not None:
            raise nx.NetworkXError("DAG must have exactly one source unless you "
                                   "provide a root.")
          root = n

    assert root is not None # DAG implies at least one source if not empty.

    # Start by computing a spanning tree, the DAG of all edges not in it,
    # and an Euler tour of the graph. We will then use the tree lca algorithm
    # on the spanning tree, and use the DAG to figure out the set of tree
    # queries necessary.
    euler_tour = list(nx.depth_first_search.dfs_edges(G, root))
    spanning_tree = nx.DiGraph(euler_tour)
    dag = nx.DiGraph((edge for edge in G.edges()
                      if edge not in spanning_tree.edges()))
  
    # Ensure that both the dag and the spanning tree contains all nodes in G,
    # even nodes that are disconnected in the dag.
    for n in G.nodes_iter():
      dag.add_node(n)
  
    counter = itertools.count().next
    depths = {}
    for edge in nx.breadth_first_search.bfs_edges(spanning_tree, euler_tour[0][0]):
      for node in edge:
        if node not in depths:
          depths[node] = counter()
  
    # Index the position of all nodes in the Euler tour so we can efficiently
    # sort lists and merge in tour order.
    euler_tour_pos = {}
    for edge in euler_tour:
      for node in edge:
        euler_tour_pos.setdefault(node, counter())
  
    # Generate the transitive closure over the dag (not G) of all nodes, and
    # sort each node's closure set by order of first appearance in the Euler
    # tour.
    ancestors = {}
    for v in dag.nodes_iter():
      my_ancestors = nx.dag.ancestors(dag, v)
      my_ancestors.add(v)
      ancestors[v] = sorted(my_ancestors, key=euler_tour_pos.get)
  
    # Generate the spanning tree lca for all pairs. This doesn't make sense to
    # do incrementally since we are using a linear time offline algorithm for
    # tree lca.
    tree_lca = dict(tree_all_pairs_lowest_common_ancestors(spanning_tree, root))
  
    self.ancestors = ancestors
    self.euler_tour_pos = euler_tour_pos
    self.tree_lca = tree_lca
    self.depths = depths

  def __getitem__(self, nodes):
    ans = self.lowest_common_ancestor(*nodes)
    if ans is None:
      raise nx.NetworkXUnfeasible("Pair has no common ancestors that are "
                                  "reachable from the provided root.")
    else:
      return ans

  def lowest_common_ancestor(self, node1, node2):
    if not self.ancestors[node1] or not self.ancestors[node2]:
      return None

    # Not necessary for correctness but fits in with a more "intuitive" notion
    # of LCA to default to the current node in such cases.
    if node1 == node2:
      return node1

    best_depth = None
    best = None

    indices = [0, 0]
    vertices = [node1, node2]
    ancestors = [self.ancestors[node1], self.ancestors[node2]]

    def get_next_in_merged_lists(indices):
      """Returns the index of the list containing the next item in the merged
         order (0 or 1) or None if exhausted."""
      i1, i2 = indices
      if (i1 >= len(self.ancestors[node1]) and
          i2 >= len(self.ancestors[node2])):
        return None
      elif i1 >= len(self.ancestors[node1]):
        return 1
      elif i2 >= len(self.ancestors[node2]):
        return 0
      elif (self.euler_tour_pos[self.ancestors[node1][i1]] <
            self.euler_tour_pos[self.ancestors[node2][i2]]):
        return 0
      else:
        return 1

    # Find the LCA by iterating through the in-order merge of the two nodes
    # of interest ancestor sets. In principle, we need to consider all pairs in
    # the Cartesian product of the ancestor sets, but by the restricted min
    # range query reduction we are guaranteed that one of the pairs of interest
    # is adjacent in the merged list iff one came from each list.
    i = get_next_in_merged_lists(indices)
    cur = ancestors[i][indices[i]], i
    while i is not None:
      prev = cur
      indices[i] += 1
      i = get_next_in_merged_lists(indices)
      if i is not None:
        cur = ancestors[i][indices[i]], i
        if cur[1] != prev[1]:
          tree_node1, tree_node2 = prev[0], cur[0]
          if (tree_node1, tree_node2) in self.tree_lca:
            ans = self.tree_lca[tree_node1, tree_node2]
          else:
            ans = self.tree_lca[tree_node2, tree_node1]
          if best is None or self.depths[ans] > best_depth:
            best_depth = self.depths[ans]
            best = ans

    return best

    def all_pairs_lowest_common_ancestor(self):
      for (n1, n2) in (pairs if pairs is not None else self.tree_lca):
        res = self.lowest_common_ancestor(n1, n2)
        if res is not None:
          yield res

