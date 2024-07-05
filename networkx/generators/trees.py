"""Functions for generating trees.

The functions sampling trees at random in this module come
in two variants: labeled and unlabeled. The labeled variants
sample from every possible tree with the given number of nodes
uniformly at random. The unlabeled variants sample from every
possible *isomorphism class* of trees with the given number
of nodes uniformly at random.

To understand the difference, consider the following example.
There are two isomorphism classes of trees with four nodes.
One is that of the path graph, the other is that of the
star graph. The unlabeled variant will return a line graph or
a star graph with probability 1/2.

The labeled variant will return the line graph
with probability 3/4 and the star graph with probability 1/4,
because there are more labeled variants of the line graph
than of the star graph. More precisely, the line graph has
an automorphism group of order 2, whereas the star graph has
an automorphism group of order 6, so the line graph has three
times as many labeled variants as the star graph, and thus
three more chances to be drawn.

Additionally, some functions in this module can sample rooted
trees and forests uniformly at random. A rooted tree is a tree
with a designated root node. A rooted forest is a disjoint union
of rooted trees.
"""

import warnings
from collections import Counter, defaultdict
from math import comb, factorial

import networkx as nx
from networkx.utils import py_random_state

__all__ = [
    "prefix_tree",
    "prefix_tree_recursive",
    "random_labeled_tree",
    "random_labeled_rooted_tree",
    "random_labeled_rooted_forest",
    "random_unlabeled_tree",
    "random_unlabeled_rooted_tree",
    "random_unlabeled_rooted_forest",
]


@nx._dispatchable(graphs=None, returns_graph=True)
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


@nx._dispatchable(graphs=None, returns_graph=True)
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


@py_random_state("seed")
@nx._dispatchable(graphs=None, returns_graph=True)
def random_labeled_tree(n, *, seed=None):
    """Returns a labeled tree on `n` nodes chosen uniformly at random.

    Generating uniformly distributed random Prüfer sequences and
    converting them into the corresponding trees is a straightforward
    method of generating uniformly distributed random labeled trees.
    This function implements this method.

    Parameters
    ----------
    n : int
        The number of nodes, greater than zero.
    seed : random_state
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`

    Returns
    -------
     :class:`networkx.Graph`
        A `networkx.Graph` with nodes in the set {0, …, *n* - 1}.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).

    Examples
    --------
    >>> G = nx.random_labeled_tree(5, seed=42)
    >>> nx.is_tree(G)
    True
    >>> G.edges
    EdgeView([(0, 1), (0, 3), (0, 2), (2, 4)])

    A tree with *arbitrarily directed* edges can be created by assigning
    generated edges to a ``DiGraph``:

    >>> DG = nx.DiGraph()
    >>> DG.add_edges_from(G.edges)
    >>> nx.is_tree(DG)
    True
    >>> DG.edges
    OutEdgeView([(0, 1), (0, 3), (0, 2), (2, 4)])
    """
    # Cannot create a Prüfer sequence unless `n` is at least two.
    if n == 0:
        raise nx.NetworkXPointlessConcept("the null graph is not a tree")
    if n == 1:
        return nx.empty_graph(1)
    return nx.from_prufer_sequence([seed.choice(range(n)) for i in range(n - 2)])


@py_random_state("seed")
@nx._dispatchable(graphs=None, returns_graph=True)
def random_labeled_rooted_tree(n, *, seed=None):
    """Returns a labeled rooted tree with `n` nodes.

    The returned tree is chosen uniformly at random from all labeled rooted trees.

    Parameters
    ----------
    n : int
        The number of nodes
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    :class:`networkx.Graph`
        A `networkx.Graph` with integer nodes 0 <= node <= `n` - 1.
        The root of the tree is selected uniformly from the nodes.
        The "root" graph attribute identifies the root of the tree.

    Notes
    -----
    This function returns the result of :func:`random_labeled_tree`
    with a randomly selected root.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).
    """
    t = random_labeled_tree(n, seed=seed)
    t.graph["root"] = seed.randint(0, n - 1)
    return t


@py_random_state("seed")
@nx._dispatchable(graphs=None, returns_graph=True)
def random_labeled_rooted_forest(n, *, seed=None):
    """Returns a labeled rooted forest with `n` nodes.

    The returned forest is chosen uniformly at random using a
    generalization of Prüfer sequences [1]_ in the form described in [2]_.

    Parameters
    ----------
    n : int
        The number of nodes.
    seed : random_state
       See :ref:`Randomness<randomness>`.

    Returns
    -------
    :class:`networkx.Graph`
        A `networkx.Graph` with integer nodes 0 <= node <= `n` - 1.
        The "roots" graph attribute is a set of integers containing the roots.

    References
    ----------
    .. [1] Knuth, Donald E. "Another Enumeration of Trees."
        Canadian Journal of Mathematics, 20 (1968): 1077-1086.
        https://doi.org/10.4153/CJM-1968-104-8
    .. [2] Rubey, Martin. "Counting Spanning Trees". Diplomarbeit
        zur Erlangung des akademischen Grades Magister der
        Naturwissenschaften an der Formal- und Naturwissenschaftlichen
        Fakultät der Universität Wien. Wien, May 2000.
    """

    # Select the number of roots by iterating over the cumulative count of trees
    # with at most k roots
    def _select_k(n, seed):
        r = seed.randint(0, (n + 1) ** (n - 1) - 1)
        cum_sum = 0
        for k in range(1, n):
            cum_sum += (factorial(n - 1) * n ** (n - k)) // (
                factorial(k - 1) * factorial(n - k)
            )
            if r < cum_sum:
                return k

        return n

    F = nx.empty_graph(n)
    if n == 0:
        F.graph["roots"] = {}
        return F
    # Select the number of roots k
    k = _select_k(n, seed)
    if k == n:
        F.graph["roots"] = set(range(n))
        return F  # Nothing to do
    # Select the roots
    roots = seed.sample(range(n), k)
    # Nonroots
    p = set(range(n)).difference(roots)
    # Coding sequence
    N = [seed.randint(0, n - 1) for i in range(n - k - 1)]
    # Multiset of elements in N also in p
    degree = Counter([x for x in N if x in p])
    # Iterator over the elements of p with degree zero
    iterator = iter(x for x in p if degree[x] == 0)
    u = last = next(iterator)
    # This loop is identical to that for Prüfer sequences,
    # except that we can draw nodes only from p
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


# The following functions support generation of unlabeled trees and forests.


def _to_nx(edges, n_nodes, root=None, roots=None):
    """
    Converts the (edges, n_nodes) input to a :class:`networkx.Graph`.
    The (edges, n_nodes) input is a list of even length, where each pair
    of consecutive integers represents an edge, and an integer `n_nodes`.
    Integers in the list are elements of `range(n_nodes)`.

    Parameters
    ----------
    edges : list of ints
        The flattened list of edges of the graph.
    n_nodes : int
        The number of nodes of the graph.
    root: int (default=None)
        If not None, the "root" attribute of the graph will be set to this value.
    roots: collection of ints (default=None)
        If not None, he "roots" attribute of the graph will be set to this value.

    Returns
    -------
    :class:`networkx.Graph`
        The graph with `n_nodes` nodes and edges given by `edges`.
    """
    G = nx.empty_graph(n_nodes)
    G.add_edges_from(edges)
    if root is not None:
        G.graph["root"] = root
    if roots is not None:
        G.graph["roots"] = roots
    return G


def _num_rooted_trees(n, cache_trees):
    """Returns the number of unlabeled rooted trees with `n` nodes.

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
    for n_i in range(len(cache_trees), n + 1):
        cache_trees.append(
            sum(
                [
                    d * cache_trees[n_i - j * d] * cache_trees[d]
                    for d in range(1, n_i)
                    for j in range(1, (n_i - 1) // d + 1)
                ]
            )
            // (n_i - 1)
        )
    return cache_trees[n]


def _select_jd_trees(n, cache_trees, seed):
    """Returns a pair $(j,d)$ with a specific probability.

    Given $n$, returns a pair of positive integers $(j,d)$ with the probability
    specified in formula (5) of Chapter 29 of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes
    cache_trees : list of ints
        Cache for :func:`_num_rooted_trees`.
    seed : random_state
       See :ref:`Randomness<randomness>`.

    Returns
    -------
    (int, int)
        A pair of positive integers $(j,d)$ satisfying formula (5) of
        Chapter 29 of [1]_.

    References
    ----------
    .. [1] Nijenhuis, Albert, and Wilf, Herbert S.
        "Combinatorial algorithms: for computers and calculators."
        Academic Press, 1978.
        https://doi.org/10.1016/C2013-0-11243-3
    """
    p = seed.randint(0, _num_rooted_trees(n, cache_trees) * (n - 1) - 1)
    cumsum = 0
    for d in range(n - 1, 0, -1):
        for j in range(1, (n - 1) // d + 1):
            cumsum += (
                d
                * _num_rooted_trees(n - j * d, cache_trees)
                * _num_rooted_trees(d, cache_trees)
            )
            if p < cumsum:
                return (j, d)


def _random_unlabeled_rooted_tree(n, cache_trees, seed):
    """Returns an unlabeled rooted tree with `n` nodes.

    Returns an unlabeled rooted tree with `n` nodes chosen uniformly
    at random using the "RANRUT" algorithm from [1]_.
    The tree is returned in the form: (list_of_edges, number_of_nodes)

    Parameters
    ----------
    n : int
        The number of nodes, greater than zero.
    cache_trees : list ints
        Cache for :func:`_num_rooted_trees`.
    seed : random_state
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    (list_of_edges, number_of_nodes) : list, int
        A random unlabeled rooted tree with `n` nodes as a 2-tuple
        ``(list_of_edges, number_of_nodes)``.
        The root is node 0.

    References
    ----------
    .. [1] Nijenhuis, Albert, and Wilf, Herbert S.
        "Combinatorial algorithms: for computers and calculators."
        Academic Press, 1978.
        https://doi.org/10.1016/C2013-0-11243-3
    """
    if n == 1:
        edges, n_nodes = [], 1
        return edges, n_nodes
    if n == 2:
        edges, n_nodes = [(0, 1)], 2
        return edges, n_nodes

    j, d = _select_jd_trees(n, cache_trees, seed)
    t1, t1_nodes = _random_unlabeled_rooted_tree(n - j * d, cache_trees, seed)
    t2, t2_nodes = _random_unlabeled_rooted_tree(d, cache_trees, seed)
    t12 = [(0, t2_nodes * i + t1_nodes) for i in range(j)]
    t1.extend(t12)
    for _ in range(j):
        t1.extend((n1 + t1_nodes, n2 + t1_nodes) for n1, n2 in t2)
        t1_nodes += t2_nodes

    return t1, t1_nodes


@py_random_state("seed")
@nx._dispatchable(graphs=None, returns_graph=True)
def random_unlabeled_rooted_tree(n, *, number_of_trees=None, seed=None):
    """Returns a number of unlabeled rooted trees uniformly at random.

    Returns one or more (depending on `number_of_trees`)
    unlabeled rooted trees with `n` nodes drawn uniformly
    at random.

    Parameters
    ----------
    n : int
        The number of nodes
    number_of_trees : int or None (default)
        If not None, this number of trees is generated and returned.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    :class:`networkx.Graph` or list of :class:`networkx.Graph`
        A single `networkx.Graph` (or a list thereof, if `number_of_trees`
        is specified) with nodes in the set {0, …, *n* - 1}.
        The "root" graph attribute identifies the root of the tree.

    Notes
    -----
    The trees are generated using the "RANRUT" algorithm from [1]_.
    The algorithm needs to compute some counting functions
    that are relatively expensive: in case several trees are needed,
    it is advisable to use the `number_of_trees` optional argument
    to reuse the counting functions.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).

    References
    ----------
    .. [1] Nijenhuis, Albert, and Wilf, Herbert S.
        "Combinatorial algorithms: for computers and calculators."
        Academic Press, 1978.
        https://doi.org/10.1016/C2013-0-11243-3
    """
    if n == 0:
        raise nx.NetworkXPointlessConcept("the null graph is not a tree")
    cache_trees = [0, 1]  # initial cache of number of rooted trees
    if number_of_trees is None:
        return _to_nx(*_random_unlabeled_rooted_tree(n, cache_trees, seed), root=0)
    return [
        _to_nx(*_random_unlabeled_rooted_tree(n, cache_trees, seed), root=0)
        for i in range(number_of_trees)
    ]


def _num_rooted_forests(n, q, cache_forests):
    """Returns the number of unlabeled rooted forests with `n` nodes, and with
    no more than `q` nodes per tree. A recursive formula for this is (2) in
    [1]_. This function is implemented using dynamic programming instead of
    recursion.

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
        The number of unlabeled rooted forests with `n` nodes with no more than
        `q` nodes per tree.

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    for n_i in range(len(cache_forests), n + 1):
        q_i = min(n_i, q)
        cache_forests.append(
            sum(
                [
                    d * cache_forests[n_i - j * d] * cache_forests[d - 1]
                    for d in range(1, q_i + 1)
                    for j in range(1, n_i // d + 1)
                ]
            )
            // n_i
        )

    return cache_forests[n]


def _select_jd_forests(n, q, cache_forests, seed):
    r"""Given `n` and `q`, returns a pair of positive integers $(j,d)$
    such that $j\\leq d$, with probability satisfying (F1) of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes.
    q : int
        The maximum number of nodes for each tree of the forest.
    cache_forests : list of ints
        Cache for :func:`_num_rooted_forests`.
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
            cumsum += (
                d
                * _num_rooted_forests(n - j * d, q, cache_forests)
                * _num_rooted_forests(d - 1, q, cache_forests)
            )
            if p < cumsum:
                return (j, d)


def _random_unlabeled_rooted_forest(n, q, cache_trees, cache_forests, seed):
    """Returns an unlabeled rooted forest with `n` nodes, and with no more
    than `q` nodes per tree, drawn uniformly at random. It is an implementation
    of the algorithm "Forest" of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes.
    q : int
        The maximum number of nodes per tree.
    cache_trees :
        Cache for :func:`_num_rooted_trees`.
    cache_forests :
        Cache for :func:`_num_rooted_forests`.
    seed : random_state
       See :ref:`Randomness<randomness>`.

    Returns
    -------
    (edges, n, r) : (list, int, list)
        The forest (edges, n) and a list r of root nodes.

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    if n == 0:
        return ([], 0, [])

    j, d = _select_jd_forests(n, q, cache_forests, seed)
    t1, t1_nodes, r1 = _random_unlabeled_rooted_forest(
        n - j * d, q, cache_trees, cache_forests, seed
    )
    t2, t2_nodes = _random_unlabeled_rooted_tree(d, cache_trees, seed)
    for _ in range(j):
        r1.append(t1_nodes)
        t1.extend((n1 + t1_nodes, n2 + t1_nodes) for n1, n2 in t2)
        t1_nodes += t2_nodes
    return t1, t1_nodes, r1


@py_random_state("seed")
@nx._dispatchable(graphs=None, returns_graph=True)
def random_unlabeled_rooted_forest(n, *, q=None, number_of_forests=None, seed=None):
    """Returns a forest or list of forests selected at random.

    Returns one or more (depending on `number_of_forests`)
    unlabeled rooted forests with `n` nodes, and with no more than
    `q` nodes per tree, drawn uniformly at random.
    The "roots" graph attribute identifies the roots of the forest.

    Parameters
    ----------
    n : int
        The number of nodes
    q : int or None (default)
        The maximum number of nodes per tree.
    number_of_forests : int or None (default)
        If not None, this number of forests is generated and returned.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    :class:`networkx.Graph` or list of :class:`networkx.Graph`
        A single `networkx.Graph` (or a list thereof, if `number_of_forests`
        is specified) with nodes in the set {0, …, *n* - 1}.
        The "roots" graph attribute is a set containing the roots
        of the trees in the forest.

    Notes
    -----
    This function implements the algorithm "Forest" of [1]_.
    The algorithm needs to compute some counting functions
    that are relatively expensive: in case several trees are needed,
    it is advisable to use the `number_of_forests` optional argument
    to reuse the counting functions.

    Raises
    ------
    ValueError
        If `n` is non-zero but `q` is zero.

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    if q is None:
        q = n
    if q == 0 and n != 0:
        raise ValueError("q must be a positive integer if n is positive.")

    cache_trees = [0, 1]  # initial cache of number of rooted trees
    cache_forests = [1]  # initial cache of number of rooted forests

    if number_of_forests is None:
        g, nodes, rs = _random_unlabeled_rooted_forest(
            n, q, cache_trees, cache_forests, seed
        )
        return _to_nx(g, nodes, roots=set(rs))

    res = []
    for i in range(number_of_forests):
        g, nodes, rs = _random_unlabeled_rooted_forest(
            n, q, cache_trees, cache_forests, seed
        )
        res.append(_to_nx(g, nodes, roots=set(rs)))
    return res


def _num_trees(n, cache_trees):
    """Returns the number of unlabeled trees with `n` nodes.

    See also https://oeis.org/A000055.

    Parameters
    ----------
    n : int
        The number of nodes.
    cache_trees : list of ints
        Cache for :func:`_num_rooted_trees`.

    Returns
    -------
    int
        The number of unlabeled trees with `n` nodes.
    """
    r = _num_rooted_trees(n, cache_trees) - sum(
        [
            _num_rooted_trees(j, cache_trees) * _num_rooted_trees(n - j, cache_trees)
            for j in range(1, n // 2 + 1)
        ]
    )
    if n % 2 == 0:
        r += comb(_num_rooted_trees(n // 2, cache_trees) + 1, 2)
    return r


def _bicenter(n, cache, seed):
    """Returns a bi-centroidal tree on `n` nodes drawn uniformly at random.

    This function implements the algorithm Bicenter of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes (must be even).
    cache : list of ints.
        Cache for :func:`_num_rooted_trees`.
    seed : random_state
        See :ref:`Randomness<randomness>`

    Returns
    -------
    (edges, n)
        The tree as a list of edges and number of nodes.

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
    t.extend([(n1 + (n // 2), n2 + (n // 2)) for n1, n2 in t2])
    t.append((0, n // 2))
    return t, t_nodes + t2_nodes


def _random_unlabeled_tree(n, cache_trees, cache_forests, seed):
    """Returns a tree on `n` nodes drawn uniformly at random.
    It implements the Wilf's algorithm "Free" of [1]_.

    Parameters
    ----------
    n : int
        The number of nodes, greater than zero.
    cache_trees : list of ints
        Cache for :func:`_num_rooted_trees`.
    cache_forests : list of ints
        Cache for :func:`_num_rooted_forests`.
    seed : random_state
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`

    Returns
    -------
    (edges, n)
        The tree as a list of edges and number of nodes.

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
        f, n_f, r = _random_unlabeled_rooted_forest(
            n - 1, (n - 1) // 2, cache_trees, cache_forests, seed
        )
        for i in r:
            f.append((i, n_f))
        return f, n_f + 1


@py_random_state("seed")
@nx._dispatchable(graphs=None, returns_graph=True)
def random_unlabeled_tree(n, *, number_of_trees=None, seed=None):
    """Returns a tree or list of trees chosen randomly.

    Returns one or more (depending on `number_of_trees`)
    unlabeled trees with `n` nodes drawn uniformly at random.

    Parameters
    ----------
    n : int
        The number of nodes
    number_of_trees : int or None (default)
        If not None, this number of trees is generated and returned.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    :class:`networkx.Graph` or list of :class:`networkx.Graph`
        A single `networkx.Graph` (or a list thereof, if
        `number_of_trees` is specified) with nodes in the set {0, …, *n* - 1}.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).

    Notes
    -----
    This function generates an unlabeled tree uniformly at random using
    Wilf's algorithm "Free" of [1]_. The algorithm needs to
    compute some counting functions that are relatively expensive:
    in case several trees are needed, it is advisable to use the
    `number_of_trees` optional argument to reuse the counting
    functions.

    References
    ----------
    .. [1] Wilf, Herbert S. "The uniform selection of free trees."
        Journal of Algorithms 2.2 (1981): 204-207.
        https://doi.org/10.1016/0196-6774(81)90021-3
    """
    if n == 0:
        raise nx.NetworkXPointlessConcept("the null graph is not a tree")

    cache_trees = [0, 1]  # initial cache of number of rooted trees
    cache_forests = [1]  # initial cache of number of rooted forests
    if number_of_trees is None:
        return _to_nx(*_random_unlabeled_tree(n, cache_trees, cache_forests, seed))
    else:
        return [
            _to_nx(*_random_unlabeled_tree(n, cache_trees, cache_forests, seed))
            for i in range(number_of_trees)
        ]
