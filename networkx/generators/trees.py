"""Functions for generating trees."""
from collections import defaultdict, Counter
import networkx as nx
import numpy as np
from networkx.utils import py_random_state
from math import comb, factorial

__all__ = ["prefix_tree", "prefix_tree_recursive", "random_tree", "random_rooted_tree", "random_rooted_forest"]


def prefix_tree(paths):
    """Creates a directed prefix tree from a list of paths.

    Usually the paths are described as strings or lists of integers.

    A "prefix tree" represents the prefix structure of the strings.
    Each node represents a prefix of some string. The root represents
    the empty prefix with children for the single letter prefixes which
    in turn have children for each double letter prefix starting with
    the single letter corresponding to the parent node, and so on.

    More generally the prefixes do not need to be strings. A prefix refers
    to the start of a sequence. The root has children for each one element
    prefix and they have children for each two element prefix that starts
    with the one element sequence of the parent, and so on.

    Note that this implementation uses integer nodes with an attribute.
    Each node has an attribute "source" whose value is the original element
    of the path to which this node corresponds. For example, suppose `paths`
    consists of one path: "can". Then the nodes `[1, 2, 3]` which represent
    this path have "source" values "c", "a" and "n".

    All the descendants of a node have a common prefix in the sequence/path
    associated with that node. From the returned tree, the prefix for each
    node can be constructed by traversing the tree up to the root and
    accumulating the "source" values along the way.

    The root node is always `0` and has "source" attribute `None`.
    The root is the only node with in-degree zero.
    The nil node is always `-1` and has "source" attribute `"NIL"`.
    The nil node is the only node with out-degree zero.


    Parameters
    ----------
    paths: iterable of paths
        An iterable of paths which are themselves sequences.
        Matching prefixes among these sequences are identified with
        nodes of the prefix tree. One leaf of the tree is associated
        with each path. (Identical paths are associated with the same
        leaf of the tree.)


    Returns
    -------
    tree: DiGraph
        A directed graph representing an arborescence consisting of the
        prefix tree generated by `paths`. Nodes are directed "downward",
        from parent to child. A special "synthetic" root node is added
        to be the parent of the first node in each path. A special
        "synthetic" leaf node, the "nil" node `-1`, is added to be the child
        of all nodes representing the last element in a path. (The
        addition of this nil node technically makes this not an
        arborescence but a directed acyclic graph; removing the nil node
        makes it an arborescence.)


    Notes
    -----
    The prefix tree is also known as a *trie*.


    Examples
    --------
    Create a prefix tree from a list of strings with common prefixes::

        >>> paths = ["ab", "abs", "ad"]
        >>> T = nx.prefix_tree(paths)
        >>> list(T.edges)
        [(0, 1), (1, 2), (1, 4), (2, -1), (2, 3), (3, -1), (4, -1)]

    The leaf nodes can be obtained as predecessors of the nil node::

        >>> root, NIL = 0, -1
        >>> list(T.predecessors(NIL))
        [2, 3, 4]

    To recover the original paths that generated the prefix tree,
    traverse up the tree from the node `-1` to the node `0`::

        >>> recovered = []
        >>> for v in T.predecessors(NIL):
        ...     prefix = ""
        ...     while v != root:
        ...         prefix = str(T.nodes[v]["source"]) + prefix
        ...         v = next(T.predecessors(v))  # only one predecessor
        ...     recovered.append(prefix)
        >>> sorted(recovered)
        ['ab', 'abs', 'ad']
    """

    def get_children(parent, paths):
        children = defaultdict(list)
        # Populate dictionary with key(s) as the child/children of the root and
        # value(s) as the remaining paths of the corresponding child/children
        for path in paths:
            # If path is empty, we add an edge to the NIL node.
            if not path:
                tree.add_edge(parent, NIL)
                continue
            child, *rest = path
            # `child` may exist as the head of more than one path in `paths`.
            children[child].append(rest)
        return children

    # Initialize the prefix tree with a root node and a nil node.
    tree = nx.DiGraph()
    root = 0
    tree.add_node(root, source=None)
    NIL = -1
    tree.add_node(NIL, source="NIL")
    children = get_children(root, paths)
    stack = [(root, iter(children.items()))]
    while stack:
        parent, remaining_children = stack[-1]
        try:
            child, remaining_paths = next(remaining_children)
        # Pop item off stack if there are no remaining children
        except StopIteration:
            stack.pop()
            continue
        # We relabel each child with an unused name.
        new_name = len(tree) - 1
        # The "source" node attribute stores the original node name.
        tree.add_node(new_name, source=child)
        tree.add_edge(parent, new_name)
        children = get_children(new_name, remaining_paths)
        stack.append((new_name, iter(children.items())))

    return tree


def prefix_tree_recursive(paths):
    """Recursively creates a directed prefix tree from a list of paths.

    The original recursive version of prefix_tree for comparison. It is
    the same algorithm but the recursion is unrolled onto a stack.

    Usually the paths are described as strings or lists of integers.

    A "prefix tree" represents the prefix structure of the strings.
    Each node represents a prefix of some string. The root represents
    the empty prefix with children for the single letter prefixes which
    in turn have children for each double letter prefix starting with
    the single letter corresponding to the parent node, and so on.

    More generally the prefixes do not need to be strings. A prefix refers
    to the start of a sequence. The root has children for each one element
    prefix and they have children for each two element prefix that starts
    with the one element sequence of the parent, and so on.

    Note that this implementation uses integer nodes with an attribute.
    Each node has an attribute "source" whose value is the original element
    of the path to which this node corresponds. For example, suppose `paths`
    consists of one path: "can". Then the nodes `[1, 2, 3]` which represent
    this path have "source" values "c", "a" and "n".

    All the descendants of a node have a common prefix in the sequence/path
    associated with that node. From the returned tree, ehe prefix for each
    node can be constructed by traversing the tree up to the root and
    accumulating the "source" values along the way.

    The root node is always `0` and has "source" attribute `None`.
    The root is the only node with in-degree zero.
    The nil node is always `-1` and has "source" attribute `"NIL"`.
    The nil node is the only node with out-degree zero.


    Parameters
    ----------
    paths: iterable of paths
        An iterable of paths which are themselves sequences.
        Matching prefixes among these sequences are identified with
        nodes of the prefix tree. One leaf of the tree is associated
        with each path. (Identical paths are associated with the same
        leaf of the tree.)


    Returns
    -------
    tree: DiGraph
        A directed graph representing an arborescence consisting of the
        prefix tree generated by `paths`. Nodes are directed "downward",
        from parent to child. A special "synthetic" root node is added
        to be the parent of the first node in each path. A special
        "synthetic" leaf node, the "nil" node `-1`, is added to be the child
        of all nodes representing the last element in a path. (The
        addition of this nil node technically makes this not an
        arborescence but a directed acyclic graph; removing the nil node
        makes it an arborescence.)


    Notes
    -----
    The prefix tree is also known as a *trie*.


    Examples
    --------
    Create a prefix tree from a list of strings with common prefixes::

        >>> paths = ["ab", "abs", "ad"]
        >>> T = nx.prefix_tree(paths)
        >>> list(T.edges)
        [(0, 1), (1, 2), (1, 4), (2, -1), (2, 3), (3, -1), (4, -1)]

    The leaf nodes can be obtained as predecessors of the nil node.

        >>> root, NIL = 0, -1
        >>> list(T.predecessors(NIL))
        [2, 3, 4]

    To recover the original paths that generated the prefix tree,
    traverse up the tree from the node `-1` to the node `0`::

        >>> recovered = []
        >>> for v in T.predecessors(NIL):
        ...     prefix = ""
        ...     while v != root:
        ...         prefix = str(T.nodes[v]["source"]) + prefix
        ...         v = next(T.predecessors(v))  # only one predecessor
        ...     recovered.append(prefix)
        >>> sorted(recovered)
        ['ab', 'abs', 'ad']
    """

    def _helper(paths, root, tree):
        """Recursively create a trie from the given list of paths.

        `paths` is a list of paths, each of which is itself a list of
        nodes, relative to the given `root` (but not including it). This
        list of paths will be interpreted as a tree-like structure, in
        which two paths that share a prefix represent two branches of
        the tree with the same initial segment.

        `root` is the parent of the node at index 0 in each path.

        `tree` is the "accumulator", the :class:`networkx.DiGraph`
        representing the branching to which the new nodes and edges will
        be added.

        """
        # For each path, remove the first node and make it a child of root.
        # Any remaining paths then get processed recursively.
        children = defaultdict(list)
        for path in paths:
            # If path is empty, we add an edge to the NIL node.
            if not path:
                tree.add_edge(root, NIL)
                continue
            child, *rest = path
            # `child` may exist as the head of more than one path in `paths`.
            children[child].append(rest)
        # Add a node for each child, connect root, recurse to remaining paths
        for child, remaining_paths in children.items():
            # We relabel each child with an unused name.
            new_name = len(tree) - 1
            # The "source" node attribute stores the original node name.
            tree.add_node(new_name, source=child)
            tree.add_edge(root, new_name)
            _helper(remaining_paths, new_name, tree)

    # Initialize the prefix tree with a root node and a nil node.
    tree = nx.DiGraph()
    root = 0
    tree.add_node(root, source=None)
    NIL = -1
    tree.add_node(NIL, source="NIL")
    # Populate the tree.
    _helper(paths, root, tree)
    return tree


# From the Wikipedia article on Prüfer sequences:
#
# > Generating uniformly distributed random Prüfer sequences and
# > converting them into the corresponding trees is a straightforward
# > method of generating uniformly distributed random labeled trees.
#
def _random_labeled_tree(n, seed, create_using):
    """Returns a label tree on `n` nodes chosen uniformly at random
        using Prüfer sequences.

    Parameters
    ----------
    n : int
        The number of nodes, greater than zero.
    seed : random_state
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
        Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
     NetworkX graph
        A tree, given as an undirected graph, whose nodes are numbers in
        the set {0, …, *n* - 1}.
    """
    # Cannot create a Prüfer sequence unless `n` is at least two.
    if n == 1:
        utree = nx.empty_graph(1, create_using)
    else:
        sequence = [seed.choice(range(n)) for i in range(n - 2)]
        utree = nx.from_prufer_sequence(sequence)

    if create_using is None:
        tree = utree
    else:
        tree = nx.empty_graph(0, create_using)
        if tree.is_directed():
            # Use a arbitrary root node and dfs to define edge directions
            edges = nx.dfs_edges(utree, source=0)
        else:
            edges = utree.edges

        # Populate the specified graph type
        tree.add_nodes_from(utree.nodes)
        tree.add_edges_from(edges)

    return tree


def _gen_cache_num_rooted_trees():
    return [0, 1]

def _num_rooted_trees(n, cache_trees):
    """Returns the number of unlabeled rooted trees with n nodes. 
    See also https://oeis.org/A000081.

    Parameters
    ----------
    n : int
        The number of nodes
    cache_trees : list of ints 
        The $i$-th element is the number of unlabeled rooted trees with $i$ nodes,
        which is used as a cache (and is extended to length $n+1$ if needed)

    Returns
    -------
    int
        The number of unlabeled rooted trees with `n` nodes.
    """
    
    for n_i in range(len(cache_trees),n+1):
        cache_trees.append(sum([d * cache_trees[n_i - j * d] * cache_trees[d] for d in range(1, n_i) for j in range(1, (n_i - 1) // d + 1)]) // (n_i - 1))
    return cache_trees[n]


def _selectjd_trees(n, cache_trees, seed):
    """Given $n$, returns a pair of positive integers $(j,d)$ with the probability
        specified in formula (5) of Chapter 29 of [1]_. 

    Parameters
    ----------
    n : int
        The number of nodes
    cache_trees : list of ints
        Cache for :ref:`_num_rooted_trees`.
    seed : random_state
       See :ref:`Randomness<randomness>`.

    Returns
    -------
    (int, int)
        A pair of positive integers $(j,d)$.

    References
    ----------
    .. [1] Nijenhuis, Albert, and Wilf, Herbert S. 
        "Combinatorial algorithms: for computers and calculators".
        Academic Press, 1978.
        https://doi.org/10.1016/C2013-0-11243-3
    """
    p = seed.randint(0, _num_rooted_trees(n, cache_trees) * (n - 1) - 1)
    cumsum = 0
    for d in range(n - 1, 0, -1):
        for j in range(1, (n - 1) // d + 1):
            cumsum += d * _num_rooted_trees(n - j * d, cache_trees) * _num_rooted_trees(d, cache_trees)
            if p < cumsum:
                return (j, d)


def _np_to_nx(edges_np, n_nodes, create_using, root=None, roots=None):
    """Converts the np-representation of a graph to a :ref:`networkx.Graph`.

    Parameters
    ----------
    edges_np : list of ints
        The flattened list of edges of the graph: it is a list (of even size), 
        where each pair of consecutive integers represents an edge. Nodes are
        numbered from 0 (inclusive) to `n_nodes` (exclusive).
    n_nodes : int
        The number of nodes of the graph.
    create_using : NetworkX graph constructor.
        Graph type to create. If graph instance, then cleared before populated.
    root: int
        The "root" attribute of the graph will be set to this value.
    roots: collection of ints
        The "roots" attribute of the graph will be set to this value.

    Returns
    -------
    :ref:`networkx.Graph`
        The graph given in input (in its np-representation) as a :ref:`networkx.Graph`.
    """

    G = nx.from_edgelist(list(map(lambda x: (x[0],x[1]), np.reshape(edges_np,(len(edges_np)//2,2)))), create_using)
    G.add_nodes_from(list(range(n_nodes)))
    if root is not None:
        G.graph["root"] = root
    if roots is not None:
        G.graph["roots"] = roots
    return G


def _random_unlabeled_rooted_tree(n, cache_trees, seed):
    """Returns a random unlabeled rooted tree with `n` nodes drawn uniformly
    at random: the tree is returned in its np-representation.

    Parameters
    ----------
    n : int
        The number of nodes, greater than zero.
    cache_trees : list ints
        Cache for :ref:`_num_rooted_trees`.
    seed : random_state
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    (edges, n)
        The tree, in its np-representation. The root is node 0.
    """

    if n == 1:
        edges, n_nodes = np.empty(0,dtype=np.int64), 1
        return edges, n_nodes
    if n == 2:
        edges, n_nodes = np.array([0,1],dtype=np.int64), 2
        return edges, n_nodes

    j, d = _selectjd_trees(n, cache_trees, seed)
    t1, t1_nodes = _random_unlabeled_rooted_tree(n - j * d, cache_trees, seed)
    t2, t2_nodes = _random_unlabeled_rooted_tree(d, cache_trees, seed)
    t12 = np.array([(t2_nodes*((i-1)//2) + t1_nodes)*(i%2) for i in range(2*j)])
    t1 = np.append(t1, t12)
    for i in range(j):
        t1 = np.append(t1, t2+(t2_nodes*i+t1_nodes))
    return t1, t1_nodes+j*t2_nodes


@py_random_state("seed")
def random_rooted_tree(n, number_of_trees=None, labeled=True, seed=None, create_using=None):
    """Returns one or more random rooted trees with n nodes drawn uniformly at 
    random. 

    Note that the interesting case is that of random unlabeled trees.
    In the labeled case, this function just returns the result
    of :ref:`random_tree` with a randomly selected root.

    Parameters
    ----------
    n : int
        The number of nodes
    number_of_trees : int or None (default)
        If not None, this number of trees is generated and returned.
    labeled : bool
        If True (default), generates labeled rooted trees uniformly at 
        random. If False, generates unlabeled rooted trees uniformly at 
        random.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
        Graph type to create. If graph instance, then cleared before populated.
        It cannot be an instance if `number_of_trees` is greater than one.

    Returns
    -------
    :ref:`networkx.Graph` or list of :ref:`networkx.Graph`
        A single `networkx.Graph` (or a list thereof, if `number_of_trees`
        is specified) representing the tree. The "root" graph attribute 
        identifies the root of the tree, which for unlabeled trees is always
        node 0.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).
    NetworkXException
        If `number_of_trees` is greater than one but `create_using` is a
        graph instance.
    """

    def _random_labeled_rooted_tree(n, seed, create_using):
        """Generates a random labeled rooted tree by generating a labeled unrooted tree and selecting a root uniformly at random"""
        t = random_tree(n, seed=seed, create_using=create_using)
        t.graph["root"] = seed.randint(0, n - 1)
        return t

    if number_of_trees != None and number_of_trees > 1 and hasattr(create_using, "adj"):
        raise nx.NetworkXException("Cannot use a graph instance to generate many trees")

    if n == 0:
        raise nx.NetworkXPointlessConcept("The null graph is not a rooted tree")

    if labeled:
        if number_of_trees is None:
            return _random_labeled_rooted_tree(n, seed, create_using)
        
        return [_random_labeled_rooted_tree(n, seed, create_using) for i in range(number_of_trees)]
    else:
        cache_trees = _gen_cache_num_rooted_trees()
        if number_of_trees is None:
            return _np_to_nx(*_random_unlabeled_rooted_tree(n, cache_trees, seed), create_using, root = 0)
        return [_np_to_nx(*_random_unlabeled_rooted_tree(n, cache_trees, seed), create_using, root = 0) for i in range(number_of_trees)]


def _gen_cache_num_rooted_forests():
  return [1]


def _num_rooted_forests(n, q, cache_forests):
    """Returns the number of unlabeled rooted forests with n nodes, and with
    no more than q nodes per tree. A recursive formula for this is (2) in
    [1]_. This function does not use recursion but dynamic programming instead.

    Parameters
    ----------
    n : int
        The number of nodes.
    q : int
        The maximum number of nodes for each tree of the forest.
    cache_forests : list of ints
        The $i$-th element is the number of unlabeled rooted forests with 
        $i$ nodes, and with no more than `q` nodes per tree; this is used 
        as a cache (and is extended to length `n` + 1 if needed).

    Returns
    -------
    int
        The number of unlabeled rooted forests with n nodes having at most q nodes each.

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    for n_i in range(len(cache_forests),n+1):
        q_i = min(n_i, q)
        cache_forests.append(sum([d * cache_forests[n_i - j * d] * cache_forests[d - 1]  for d in range(1, q_i + 1) for j in range(1, n_i // d + 1)]) // n_i)

    return cache_forests[n]


def _selectjd_forests(n, q, cache_forests, seed):
    """Given n, returns a pair of positive integers $(j,d)$ such that $j\\leq d$,
    with probability satisfying (F1) of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes.
    q : int
        The maximum number of nodes for each tree of the forest  .      
    cache_forests : list of ints
        Cache for :ref:`_num_rooted_forests`.
    seed : random_state
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    (int, int)
        A pair of positive integers $(j,d)$

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    p = seed.randint(0, _num_rooted_forests(n, q, cache_forests) * n - 1)
    cumsum = 0
    for d in range(q, 0, -1):
        for j in range(1, n // d + 1):
            cumsum += d * _num_rooted_forests(n - j * d, q, cache_forests) * _num_rooted_forests(d - 1, q, cache_forests)
            if p < cumsum:
                return (j, d)


def _random_unlabeled_rooted_forest(n, q, cache_trees, cache_forests, seed):
    """Returns a random unlabeled rooted forest with n nodes, and with no more
    than q nodes per tree, drawn uniformly at random. It is an implementation
    of algorithm Forest of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes.
    q : int
        The maximum number of nodes per tree.
    cache_trees : 
        Cache for :ref:`_num_rooted_trees`.
    cache_forests :
        Cache for :ref:`_num_rooted_forests`.
    seed : random_state
       See :ref:`Randomness<randomness>`.

    Returns
    -------
    (edges, n, r)
        The tree (edges, n), in its np-representation, and a list r of root nodes.

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.  
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    if n == 0: return (np.empty(0,dtype=np.int64), 0, [])

    j, d = _selectjd_forests(n, q, cache_forests, seed)
    t1, t1_nodes, r1 = _random_unlabeled_rooted_forest(n - j * d, q, cache_trees, cache_forests, seed)
    t2, t2_nodes = _random_unlabeled_rooted_tree(d, cache_trees, seed)
    for i in range(j):
        r1.append(t1_nodes)
        t1 = np.append(t1, t2+t1_nodes)
        t1_nodes += t2_nodes
    return (t1, t1_nodes, r1)


def _random_labeled_rooted_forest(n, seed, create_using=None):
    """Returns a random labeled rooted forest with n nodes drawn uniformly
    at random using a generalization of Prüfer sequences [1]_.

    Parameters
    ----------
    n : int
        The number of nodes.
    seed : random_state
       See :ref:`Randomness<randomness>`.
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
        Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    A random labeled rooted forest with n nodes drawn uniformly at random.
    The attribute "roots" is a set of integers containing the roots.

    References
    ----------
    .. [1] Rubey, Martin. "Counting Spanning Trees". Diplomarbeit
        zur Erlangung des akademischen Grades Magister der 
        Naturwissenschaften an der Formal- und Naturwissenschaftlichen 
        Fakultät der Universität Wien. Wien, May 2000.

    """
    
    def _select_k(n, seed):
        r = seed.randint(0, (n+1)**(n-1) - 1)
        cum_sum = 0
        for k in range(1, n):
            cum_sum += (factorial(n - 1) * n**(n - k)) // (factorial(k - 1) * factorial(n - k))
            if r < cum_sum:
                return k

        return n 

    
    F = nx.empty_graph(n, create_using);
    if n == 0:
        F.graph["roots"] = {}
        return F
    F.add_nodes_from(range(n))
    # Select the number of roots k
    k = _select_k(n, seed)
    if k == n:
        F.graph["roots"] = set(range(n))
        return F # Nothing to do
    # Select the roots
    roots = seed.sample(range(n), k)
    # Nonroots
    p = set(range(n)).difference(roots)
    # Coding sequence
    N = [seed.choice(range(n)) for i in range(n - k - 1)]
    # Multiset of elements in N also in p
    degree = Counter([x for x in N if x in p])
    # Iterator over the elements of p with degree zero
    iterator = iter(x for x in p if degree[x] == 0)
    u = last = next(iterator)

    for v in N:
        F.add_edge(u, v)
        degree[v] -= 1
        if v < last and degree[v] == 0:
            u = v
        else:
            last = u = next(iterator)

    F.add_edge(u, roots[0])
    F.graph["roots"] = set(roots)
    return F

@py_random_state("seed")
def random_rooted_forest(n, q=None, number_of_forests=None, labeled=True, seed=None, create_using=None):
    """Returns one or more random rooted forests with n nodes,
    and with no more than q nodes per tree, drawn uniformly at random.
    The "roots" graph attribute identifies the roots of the forest.

    Parameters
    ----------
    n : int
        The number of nodes
    q : int or None (default)
        If not None, the maximum number of nodes per tree when `labeled``
        is False. Raises an exception if `labeled` is True.
    number_of_forests : int or None (default)
        If not None, this number of forests is generated and returned
    labeled : bool
        If True (default), generates labeled rooted forests uniformly at 
        random. If False, generates unlabeled rooted forests uniformly at 
        random.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
        Graph type to create. If graph instance, then cleared before populated.
        It cannot be an instance if `number_of_forests` is greater than one.

    Notes
    -----
    The labeled version uses a generalization of Prüfer sequences [2]_.
    The unlabeled version uses the algorithm "Forest" of [1]_.

    Returns
    -------
        A single `networkx.Graph` (or a list thereof, if `number_of_forests`
        is specified) representing the forest. The "roots" graph attribute 
        is a set containing the roots of the trees in the forests.

    Raises
    ------
    NetworkXException
        If `number_of_forests` is greater than one but `create_using` is a
        graph instance.
    NetworkXException
        If `q` is specified for unlabeled forests.

    References
    ----------
    .. [1] Rubey, Martin. "Counting Spanning Trees". Diplomarbeit
        zur Erlangung des akademischen Grades Magister der 
        Naturwissenschaften an der Formal- und Naturwissenschaftlichen 
        Fakultät der Universität Wien. Wien, May 2000.    
    .. [2] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    if number_of_forests != None and number_of_forests > 1 and hasattr(create_using, "adj"):
        raise nx.NetworkXException("Cannot use a graph instance to generate many forests")

    if labeled:
        if q is not None:
            raise nx.NetworkXException("q can only be specified for unlabeled forests")
        if number_of_forests is None:
            return _random_labeled_rooted_forest(n, seed, create_using)
        return [_random_labeled_rooted_forest(n, seed, create_using) for i in range(number_of_forests)]

    if q is None: q = n
    if q == 0 and n != 0:
        raise ValueError("q must be a positive integer if n is positive.")

    cache_trees = _gen_cache_num_rooted_trees()
    cache_forests = _gen_cache_num_rooted_forests()

    if number_of_forests is None:
        g, nodes, rs = _random_unlabeled_rooted_forest(n, q, cache_trees, cache_forests, seed)
        return _np_to_nx(g, nodes, create_using, roots = set(rs))
        
    res = []
    for i in range(number_of_forests):
        g, nodes, rs = _random_unlabeled_rooted_forest(n, q, cache_trees, cache_forests, seed)
        res.append(_np_to_nx(g, nodes, create_using, roots = set(rs)))
    return res


def _num_trees(n, cache_trees):
    """Returns the number of unlabeled trees with n nodes. See also https://oeis.org/A000055.


    Parameters
    ----------
    n : int
        The number of nodes
    cache_trees : list of ints
        Cache for :ref:`_num_rooted_trees`.

    Returns
    -------
    int
        the number of unlabeled trees with n nodes.
    """

    r = _num_rooted_trees(n, cache_trees) - sum([_num_rooted_trees(j, cache_trees) * _num_rooted_trees(n - j, cache_trees) for j in range(1, n // 2 + 1)]) 
    if n % 2 == 0:
        r += comb(_num_rooted_trees(n//2, cache_trees) + 1, 2)
    return r


def _bicenter(n, cache, seed):
    """Returns a bi-centroidal tree on n nodes drawn uniformly at random.
    It implements the algorithm Bicenter of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes (must be even)
    cache : list of ints.
        Cache for :ref:`_num_rooted_trees`.
    seed : random_state
        See :ref:`Randomness<randomness>`

    Returns
    -------
    (edges, n)
        The tree in its np-representation

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    t, t_nodes = _random_unlabeled_rooted_tree(n // 2, cache, seed)
    if seed.randint(0, _num_rooted_trees(n // 2, cache)) == 0:
        t2, t2_nodes = t, t_nodes
    else:
        t2, t2_nodes = _random_unlabeled_rooted_tree(n // 2, cache, seed)
    t = np.append(t, t2 + n // 2)
    t = np.append(t, [0, n // 2])
    return t, t_nodes + t2_nodes


def _random_unlabeled_tree(n, cache_trees, cache_forests, seed):
    """Returns a tree on n nodes drawn uniformly at random.
    It implements the Wilf's algorithm "Free" of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes, greater than zero.
    cache_trees : list of ints
        Cache for :ref:`_num_rooted_trees`.
    cache_forests : list of ints
        Cache for :ref:`_num_rooted_forests`.
    seed : random_state
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`

    Returns
    -------
    (edges, n)
        The tree in its np-representation

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    
    if n % 2 == 1:
        p = 0
    else:
        p = comb(_num_rooted_trees(n // 2, cache_trees) + 1, 2)
    if seed.randint(0, _num_trees(n, cache_trees) - 1) < p:
        return _bicenter(n, cache_trees, seed)
    else:
        f, n_f, r = _random_unlabeled_rooted_forest(n - 1, (n - 1) // 2, cache_trees, cache_forests, seed)
        for i in r:
            f = np.append(f, [i,n_f])
        return f, n_f + 1


@py_random_state("seed")
def random_tree(n, labeled=True, number_of_trees=None, seed=None, create_using=None):
    """Returns one or more random trees with n nodes.

    Parameters
    ----------
    n : int
        The number of nodes
    labeled : bool
        If True (default), generates labeled trees uniformly at random.
        If False, generates unlabeled trees uniformly at random.
    number_of_trees : int or None (default)
        If not None, this number of trees is generated and returned.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
        Graph type to create. If graph instance, then cleared before populated.
        It cannot be an instance if `number_of_trees` is greater than one.

    Returns
    -------
    :ref:`networkx.Graph` or list of :ref:`networkx.Graph`
        A single `networkx.Graph` (or a list thereof, if `number_of_trees` is specified) 
        representing the tree, generated uniformly at random. Each tree is given as an 
        undirected graph, whose nodes are numbers in the set {0, …, *n* - 1}.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).
    NetworkXException
        If `number_of_trees` is greater than one but `create_using` is a
        graph instance.

    Notes
    -----
    The current implementation of this function for labeled trees generates 
    a uniformly random Prüfer sequence then converts that to a tree via the
    :func:`~networkx.from_prufer_sequence` function. Since there is a
    bijection between Prüfer sequences of length *n* - 2 and trees on
    *n* nodes, the tree is chosen uniformly at random from the set of
    all trees on *n* nodes.

    The current implementation of this function for unlabeled trees
    generates an unlabeled tree uniformly at random using Wilf's
    algorithm "Free" of [1]_. The generation needs to
    compute some counting functions that are relatively expensive:
    in case several trees are needed, it is advisable to use the
    `number_of_trees` optional argument to reuse the counting
    functions.

    Examples
    --------
    >>> tree = nx.random_tree(n=10, seed=0)
    >>> nx.write_network_text(tree, sources=[0])
    ╙── 0
        ├── 3
        └── 4
            ├── 6
            │   ├── 1
            │   ├── 2
            │   └── 7
            │       └── 8
            │           └── 5
            └── 9

    >>> tree = nx.random_tree(n=10, seed=0, create_using=nx.DiGraph)
    >>> nx.write_network_text(tree)
    ╙── 0
        ├─╼ 3
        └─╼ 4
            ├─╼ 6
            │   ├─╼ 1
            │   ├─╼ 2
            │   └─╼ 7
            │       └─╼ 8
            │           └─╼ 5
            └─╼ 9

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    if number_of_trees != None and number_of_trees > 1 and hasattr(create_using, "adj"):
        raise nx.NetworkXException("Cannot use a graph instance to generate many trees")

    if n == 0:
        raise nx.NetworkXPointlessConcept("the null graph is not a tree")

    if labeled:
        if number_of_trees is None:
            return _random_labeled_tree(n, seed, create_using)
        else:
            return [_random_labeled_tree(n, seed, create_using) for i in range(number_of_trees)]
    else:
        cache_trees = _gen_cache_num_rooted_trees()
        cache_forests = _gen_cache_num_rooted_forests()
        if number_of_trees is None:
            return _np_to_nx(*_random_unlabeled_tree(n, cache_trees, cache_forests, seed), create_using)
        else:
            return [_np_to_nx(*_random_unlabeled_tree(n, cache_trees, cache_forests, seed), create_using) for i in range(number_of_trees)]
