import networkx as nx
import itertools
import collections

from itertools import count, chain, product

__authors__ = "\n".join(["Alex Roper <aroper@umich.edu>"])
#   Copyright (C) 2013 by
#   Alex Roper <aroper@umich.edu>
#   All rights reserved.
#   BSD license.

__all__ = ["LowestCommonAncestorPrecomputation", "all_pairs_lowest_common_ancestor",
           "lowest_common_ancestor_naive", "tree_all_pairs_lowest_common_ancestor"]

@nx.utils.not_implemented_for("undirected", "multigraph", "graph")
def tree_all_pairs_lowest_common_ancestor(G, root=None, pairs=None):
  """Compute the lowest common ancestor for a set of pairs in the graph.

  Parameters
  ----------
  G : NetworkX directed graph

  root : node, optional
    The root of the subtree to operate on. If None, will assume the entire graph
    has exactly one source and use that.

  pairs : iterable or iterator of pairs of nodes, optional
    The pairs of interest. Defaults to all pairs under the root that have a
    lowest common ancestor. If you pass in (u, v), it may be returned as (v, u).

  Returns
  -------
  lcas : generator of tuples ((u, v), lca) where u and v are nodes in pairs and
         lca is their least common ancestor.

  Notes
  -----
  Only defined on non-null trees represented with directed edges from parents to
  children. Uses Tarjan's off-line least-common-ancestors algorithm. Runs in
  time O((V + E) + P) time, if we consider the inverse Ackerman function constant.

  Tarjan, R. E. (1979), "Applications of path compression on balanced trees",
  Journal of the ACM 26 (4): 690-715, doi:10.1145/322154.322161.

  See Also
  --------
  """

  if not G.is_directed():
    raise nx.NetworkXNotImplemented("Lowest common ancestor not defined on "
                                    "undirected graphs.")
  if not G:
     raise nx.NetworkXPointlessConcept("LCA meaningless on null graphs.")

  # Index pairs of interest for efficient lookup from either side.
  if pairs is not None:
    pair_dict = collections.defaultdict(set)
    pairs = set(pairs)
    for u, v in pairs:
      for n in (u, v):
        if not G.has_node(n):
          raise nx.NetworkXError("The node %s is not in the digraph." % str(n))
      pair_dict[u].add(v)
      pair_dict[v].add(u)

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
    raise nx.NetworkXError("Graph contains a cycle.")

  # Iterative implementation of Tarjan's offline lca algorithm as described in
  # CLRS on page 521.
  uf = nx.utils.union_find.UnionFind()
  ancestors = {}
  for node in G.nodes_iter():
    ancestors[node] = uf[node]
  colors = collections.defaultdict(bool)
  for node in nx.depth_first_search.dfs_postorder_nodes(G, root):
    colors[node] = True
    for v in (pair_dict[node] if pairs else G.nodes_iter()):
      if colors[v]:
        # If the user requested both directions of a pair, give it.
        # Otherwise, just give one.
        if pairs and (node, v) in pairs:
          yield (node, v), ancestors[uf[v]]
        if pairs is None or (v, node) in pairs:
          yield (v, node), ancestors[uf[v]]
    if node != root:
      parent = G.predecessors(node)[0]
      uf.union(parent, node)
      ancestors[uf[parent]] = parent

def get_single_root_dag(G, root):
  """Converts G into a dag with a single root by adding a node with edges to
  all sources. Returns the new DAG (or the original if acceptable) and the root.
  If root is not None, use that for the root.
  """
  if root is not None:
    return G, root, None

  sources = [n for n in G.nodes_iter() if G.in_degree(n) == 0]
  if len(sources) == 1:
    return G, sources[0], None
  else:
    G = G.copy()
    root = nx.utils.generate_unique_node()
    for source in sources:
      G.add_edge(root, source)
    return G, root, root

@nx.utils.not_implemented_for("undirected", "multigraph", "graph")
def lowest_common_ancestor_naive(G, node1, node2, root=None):
  """Compute the lowest common ancestor for two nodes in a graph.

  Parameters
  ----------
  G : NetworkX directed graph

  root : node, optional
    The node to use as a root for the purposes of defining "lowest". We define
    the lca of two nodes as the common ancestor which is farthest from the
    root. Only nodes reachable from root are considered potential ancestors.

    If omitted, the root will be the single source in G. If there are multiple
    sources, G will be copied and the copy will add edges from a unique
    "superroot" to each source.

  node1, node2 : node
    The two nodes to find an ancestor of.

  Returns
  -------
  The lowest common ancestor of node1 and node2 with respect to root. If an
  ancestor is not reachable from root, it is not considered a potential lca.
  Ties are broken arbitrarily. Note that this does NOT imply that n will be
  returned as lca(n, n), only that the value returned is at no lesser a distance
  from root than n.

  Will raise NetworkXUnfeasible if there is no lca reachable from root.

  Notes
  -----
  Only defined on non-null directed acyclic graphs. This implementation is
  designed to be efficient for only extremely small numbers of queries
  (think 1). You should really use LowestCommonAncestorPrecomputation or
  all_pairs_lowest_common_ancestor unless you are sure this is what you want.

  Operates by generating all shortest paths ending at the nodes and taking their
  intersection, then returning the member with the longest shortest path from
  root.

  See Also
  --------
  LowestCommonAncestorPrecomputation
  all_pairs_lowest_common_ancestor
  tree_all_pairs_lowest_common_ancestor
  """

  # Deal with default root
  G, root = get_single_root_dag(G, root)

  # Find all common ancestors.
  ancestors1 = nx.dag.ancestors(G, node1)
  ancestors1.add(node1)
  ancestors2 = nx.dag.ancestors(G, node2)
  ancestors2.add(node2)

  root_distance = nx.shortest_path_length(G, source=root)

  feasible = ancestors1.intersection(ancestors2)
  if feasible:
    return max(feasible, key=root_distance.get)
  else:
    raise nx.NetworkXUnfeasible("Pair has no common ancestors that are "
                                "reachable from the provided root.")

@nx.utils.not_implemented_for("undirected", "multigraph", "graph")
def all_pairs_lowest_common_ancestor(G, root=None, pairs=None):
  """Compute the lowest common ancestor for all pairs of nodes given or all pairs.

  Parameters
  ----------
  G : NetworkX directed graph

  root : node, optional
    The node to use as a root for the purposes of defining "lowest". We define
    the lca of two nodes as the common ancestor which is farthest from the
    root. Only nodes reachable from root are considered potential ancestors.
    If unspecified, and G has a single source, will use that. If G has
    multiple sources, then it will be copied, and a unique single root added
    to the copy.

  pairs : iterable or iterator of pairs of nodes, optional
    The pairs of nodes of interest. If None, will find the LCA of all pairs of
    nodes. Iterators will be materialized and thus decrease efficiency.

  Returns
  -------
  An iterator over ((node1, node2), lca) where (node1, node2) are either all
  pairs or the pairs specified and lca is a lowest common ancestor of the pair.
  Note that we do not duplicate, eg you will not get both (b, a) and (a, b),
  if pairs is unspecifed.

  Notes
  -----
  Only defined on non-null directed acyclic graphs. This implementation is
  efficient if all pairs are necessary, taking cubic time. If you only need
  some pairs, see LowestCommonAncestorPrecomputation.

  Uses the O(n^3) ancestor-list algorithm from:
  M. A. Bender, M. Farach-Colton, G. Pemmasani, S. Skiena, P. Sumazin.
  "Lowest common ancestors in trees and directed acyclic graphs."
  Journal of Algorithms, 57(2): 75-94, 2005.

  See Also
  --------
  LowestCommonAncestorPrecomputation
  lowest_common_ancestor_naive
  tree_all_pairs_lowest_common_ancestor
  """

  # The copy isn't ideal, neither is the switch-on-type, but without it users
  # passing an iterable will encounter confusing errors, and itertools.tee does
  # not appear to handle builtin types efficiently (IE, it materializes another
  # buffer rather than just creating listoperators at the same offset). The
  # Python documentation notes use of tee is unadvised when one is consumed
  # before the other.
  #
  # This will always produce correct results and avoid unnecessary
  # copies in many common cases.
  # 
  # Why is there not a simple, builtin way to upgrade an iterator to an iterable
  # interface if and only if necessary?
  if (not isinstance(pairs, (set, dict, list, tuple, frozenset, basestring)) and
      pairs is not None):
    pairs = set(pairs)
  lcap = LowestCommonAncestorPrecomputation(G, pairs)
  return lcap.all_pairs_lowest_common_ancestor(pairs)

class LowestCommonAncestorPrecomputation(object):
  """Precomputes LCA data and returns a queryable object."""

  def __init__(self, G, pairs=None):
    """
    Parameters
    ----------
    G : NetworkX directed graph
  
    root : node, optional
      The node to use as a root for the purposes of defining "lowest". We define
      the lca of two nodes as the common ancestor which is farthest from the
      root. Only nodes reachable from root are considered potential ancestors.
      If unspecified, and G has a single source, will use that. If G has
      multiple sources, then it will be copied, and a unique single root added
      to the copy.

    pairs : iterable or iterator of pairs of nodes, optional
      Only perform precomputation necessary to answer queries about these
      pairs. Iterators will be materialized and thus decrease efficiency.
  
    Returns
    -------
    A LowestCommonAncestorPrecomputation that can answer each lowest common
    ancestor query in linear time. Can generate all pairs LCA in quadratic time.
  
    Notes
    -----
    Only defined on non-null directed acyclic graphs.

    Uses the O(n^3) ancestor-list algorithm from:
    M. A. Bender, M. Farach-Colton, G. Pemmasani, S. Skiena, P. Sumazin.
    "Lowest common ancestors in trees and directed acyclic graphs."
    Journal of Algorithms, 57(2): 75-94, 2005.

    The precomputation of the object takes O(N ** 2 * log(N)), queries take
    linear time.
    
    Use obj[node1, node2] to throw an exception if node1 and node2 have no lca;
    use obj.lowest_common_ancestor(node1, node2) to return None.
  
    See Also
    --------
    LowestCommonAncestorPrecomputation
    all_pairs_lowest_common_ancestor
    tree_all_pairs_lowest_common_ancestor
    """

    if not nx.is_directed_acyclic_graph(G):
      raise nx.NetworkXError("LCA only defined on directed acyclic graphs.")
    elif not G:
      raise nx.NetworkXPointlessConcept("LCA meaningless on null graphs.")

    # See note in all_pairs_lowest_common_ancestor.
    if (not isinstance(pairs, (set, dict, list, tuple, frozenset, basestring)) and
        pairs is not None):
      pairs = set(pairs)

    # Handle default root.
    G, root, self.superroot = get_single_root_dag(G, root=None)

    # Start by computing a spanning tree, the DAG of all edges not in it,
    # and an Euler tour of the graph. We will then use the tree lca algorithm
    # on the spanning tree, and use the DAG to figure out the set of tree
    # queries necessary.
    euler_tour = list(nx.depth_first_search.dfs_edges(G, root))
    spanning_tree = nx.DiGraph(euler_tour)
    dag = nx.DiGraph((edge for edge in G.edges_iter()
                      if not spanning_tree.has_edge(*edge)))
  
    # Ensure that both the dag and the spanning tree contains all nodes in G,
    # even nodes that are disconnected in the dag.
    for n in G.nodes_iter():
      dag.add_node(n)
  
    counter = count().next
    root_distance = {}

    for edge in nx.breadth_first_search.bfs_edges(spanning_tree, root):
      for node in edge:
        if node not in root_distance:
          root_distance[node] = counter()
  
    # Index the position of all nodes in the Euler tour so we can efficiently
    # sort lists and merge in tour order.
    euler_tour_pos = {}
    for edge in euler_tour:
      for node in edge:
        euler_tour_pos.setdefault(node, counter())

    # Generate the set of all nodes of interest in the pairs.
    pairset = set()
    if pairs is not None:
      pairset = set(chain.from_iterable(pairs))

    # Generate the transitive closure over the dag (not G) of all nodes, and
    # sort each node's closure set by order of first appearance in the Euler
    # tour.
    ancestors = {}
    for v in dag.nodes_iter():
      if pairs is None or v in pairset:
        my_ancestors = nx.dag.ancestors(dag, v)
        my_ancestors.add(v)
        ancestors[v] = sorted(my_ancestors, key=euler_tour_pos.get)

    # Generate the spanning tree lca for all pairs. This doesn't make sense to
    # do incrementally since we are using a linear time offline algorithm for
    # tree lca.
    if pairs is None:
      tree_lca = dict(tree_all_pairs_lowest_common_ancestor(spanning_tree, root))
    else:
      # Generate all tree queries we will need to ask.
      tree_pairs = chain.from_iterable(product(ancestors[a], ancestors[b])
                                       for (a, b) in pairs)
      tree_lca = dict(tree_all_pairs_lowest_common_ancestor(spanning_tree, root, tree_pairs))
  
    self.ancestors = ancestors
    self.euler_tour_pos = euler_tour_pos
    self.tree_lca = tree_lca
    self.root_distance = root_distance 

  def __getitem__(self, nodes):
    ans = self.lowest_common_ancestor(*nodes)
    if ans is None:
      raise nx.NetworkXUnfeasible("Pair has no common ancestors that are "
                                  "reachable from the provided root.")
    else:
      return ans

  def lowest_common_ancestor(self, node1, node2):
    """Returns the lowest common ancestor of the two notes relative to the root
    used in the object's initialization or None if there is no LCA.
    Linear time."""
    if not self.ancestors[node1] or not self.ancestors[node2]:
      return None

    # Not necessary for correctness but fits in with a more "intuitive" notion
    # of LCA to default to the current node in such cases.
    if node1 == node2:
      return node1

    best_root_distance = None
    best = None

    indices = [0, 0]
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
          if best is None or self.root_distance[ans] > best_root_distance:
            best_root_distance = self.root_distance[ans]
            best = ans

    return best

  def all_pairs_lowest_common_ancestor(self, pairs=None):
    """Returns the lowest common ancestor of all pairs of nodes in the graph
    (or in the provided list)."""
    for (n1, n2) in (pairs if pairs is not None else self.tree_lca):
      res = self.lowest_common_ancestor(n1, n2)
      if res is not None and res != self.superroot:
        yield (n1, n2), res
