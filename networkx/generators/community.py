#    Copyright(C) 2011, 2015, 2018 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    Konstantinos Karakatsanis <dinoskarakas@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:  Ben Edwards (bedwards@cs.unm.edu)
#           Aric Hagberg (hagberg@lanl.gov)
#           Konstantinos Karakatsanis (dinoskarakas@gmail.com)
#           Jean-Gabriel Young (jean.gabriel.young@gmail.com)
"""Generators for classes of graphs used in studying social networks."""
from __future__ import division
import itertools
import math
import networkx as nx
from networkx.utils import py_random_state

__all__ = ['caveman_graph', 'connected_caveman_graph',
           'relaxed_caveman_graph', 'random_partition_graph',
           'planted_partition_graph', 'gaussian_random_partition_graph',
           'ring_of_cliques', 'windmill_graph', 'stochastic_block_model']


def caveman_graph(l, k):
    """Returns a caveman graph of `l` cliques of size `k`.

    Parameters
    ----------
    l : int
      Number of cliques
    k : int
      Size of cliques

    Returns
    -------
    G : NetworkX Graph
      caveman graph

    Notes
    -----
    This returns an undirected graph, it can be converted to a directed
    graph using :func:`nx.to_directed`, or a multigraph using
    ``nx.MultiGraph(nx.caveman_graph(l, k))``. Only the undirected version is
    described in [1]_ and it is unclear which of the directed
    generalizations is most useful.

    Examples
    --------
    >>> G = nx.caveman_graph(3, 3)

    See also
    --------

    connected_caveman_graph

    References
    ----------
    .. [1] Watts, D. J. 'Networks, Dynamics, and the Small-World Phenomenon.'
       Amer. J. Soc. 105, 493-527, 1999.
    """
    # l disjoint cliques of size k
    G = nx.empty_graph(l * k)
    if k > 1:
        for start in range(0, l * k, k):
            edges = itertools.combinations(range(start, start + k), 2)
            G.add_edges_from(edges)
    return G


def connected_caveman_graph(l, k):
    """Returns a connected caveman graph of `l` cliques of size `k`.

    The connected caveman graph is formed by creating `n` cliques of size
    `k`, then a single edge in each clique is rewired to a node in an
    adjacent clique.

    Parameters
    ----------
    l : int
      number of cliques
    k : int
      size of cliques

    Returns
    -------
    G : NetworkX Graph
      connected caveman graph

    Notes
    -----
    This returns an undirected graph, it can be converted to a directed
    graph using :func:`nx.to_directed`, or a multigraph using
    ``nx.MultiGraph(nx.caveman_graph(l, k))``. Only the undirected version is
    described in [1]_ and it is unclear which of the directed
    generalizations is most useful.

    Examples
    --------
    >>> G = nx.connected_caveman_graph(3, 3)

    References
    ----------
    .. [1] Watts, D. J. 'Networks, Dynamics, and the Small-World Phenomenon.'
       Amer. J. Soc. 105, 493-527, 1999.
    """
    G = nx.caveman_graph(l, k)
    for start in range(0, l * k, k):
        G.remove_edge(start, start + 1)
        G.add_edge(start, (start - 1) % (l * k))
    return G


@py_random_state(3)
def relaxed_caveman_graph(l, k, p, seed=None):
    """Return a relaxed caveman graph.

    A relaxed caveman graph starts with `l` cliques of size `k`.  Edges are
    then randomly rewired with probability `p` to link different cliques.

    Parameters
    ----------
    l : int
      Number of groups
    k : int
      Size of cliques
    p : float
      Probabilty of rewiring each edge.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    G : NetworkX Graph
      Relaxed Caveman Graph

    Raises
    ------
    NetworkXError:
     If p is not in [0,1]

    Examples
    --------
    >>> G = nx.relaxed_caveman_graph(2, 3, 0.1, seed=42)

    References
    ----------
    .. [1] Santo Fortunato, Community Detection in Graphs,
       Physics Reports Volume 486, Issues 3-5, February 2010, Pages 75-174.
       https://arxiv.org/abs/0906.0612
    """
    G = nx.caveman_graph(l, k)
    nodes = list(G)
    for (u, v) in G.edges():
        if seed.random() < p:  # rewire the edge
            x = seed.choice(nodes)
            if G.has_edge(u, x):
                continue
            G.remove_edge(u, v)
            G.add_edge(u, x)
    return G


@py_random_state(3)
def random_partition_graph(sizes, p_in, p_out, seed=None, directed=False):
    """Return the random partition graph with a partition of sizes.

    A partition graph is a graph of communities with sizes defined by
    s in sizes. Nodes in the same group are connected with probability
    p_in and nodes of different groups are connected with probability
    p_out.

    Parameters
    ----------
    sizes : list of ints
      Sizes of groups
    p_in : float
      probability of edges with in groups
    p_out : float
      probability of edges between groups
    directed : boolean optional, default=False
      Whether to create a directed graph
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    G : NetworkX Graph or DiGraph
      random partition graph of size sum(gs)

    Raises
    ------
    NetworkXError
      If p_in or p_out is not in [0,1]

    Examples
    --------
    >>> G = nx.random_partition_graph([10,10,10],.25,.01)
    >>> len(G)
    30
    >>> partition = G.graph['partition']
    >>> len(partition)
    3

    Notes
    -----
    This is a generalization of the planted-l-partition described in
    [1]_.  It allows for the creation of groups of any size.

    The partition is store as a graph attribute 'partition'.

    References
    ----------
    .. [1] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174. https://arxiv.org/abs/0906.0612
    """
    # Use geometric method for O(n+m) complexity algorithm
    # partition = nx.community_sets(nx.get_node_attributes(G, 'affiliation'))
    if not 0.0 <= p_in <= 1.0:
        raise nx.NetworkXError("p_in must be in [0,1]")
    if not 0.0 <= p_out <= 1.0:
        raise nx.NetworkXError("p_out must be in [0,1]")

    # create connection matrix
    num_blocks = len(sizes)
    p = [[p_out for s in range(num_blocks)] for r in range(num_blocks)]
    for r in range(num_blocks):
        p[r][r] = p_in

    return stochastic_block_model(sizes, p, nodelist=None, seed=seed,
                                  directed=directed, selfloops=False,
                                  sparse=True)


@py_random_state(4)
def planted_partition_graph(l, k, p_in, p_out, seed=None, directed=False):
    """Return the planted l-partition graph.

    This model partitions a graph with n=l*k vertices in
    l groups with k vertices each. Vertices of the same
    group are linked with a probability p_in, and vertices
    of different groups are linked with probability p_out.

    Parameters
    ----------
    l : int
      Number of groups
    k : int
      Number of vertices in each group
    p_in : float
      probability of connecting vertices within a group
    p_out : float
      probability of connected vertices between groups
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    directed : bool,optional (default=False)
      If True return a directed graph

    Returns
    -------
    G : NetworkX Graph or DiGraph
      planted l-partition graph

    Raises
    ------
    NetworkXError:
      If p_in,p_out are not in [0,1] or

    Examples
    --------
    >>> G = nx.planted_partition_graph(4, 3, 0.5, 0.1, seed=42)

    See Also
    --------
    random_partition_model

    References
    ----------
    .. [1] A. Condon, R.M. Karp, Algorithms for graph partitioning
        on the planted partition model,
        Random Struct. Algor. 18 (2001) 116-140.

    .. [2] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174. https://arxiv.org/abs/0906.0612
    """
    return random_partition_graph([k] * l, p_in, p_out, seed, directed)


@py_random_state(6)
def gaussian_random_partition_graph(n, s, v, p_in, p_out, directed=False,
                                    seed=None):
    """Generate a Gaussian random partition graph.

    A Gaussian random partition graph is created by creating k partitions
    each with a size drawn from a normal distribution with mean s and variance
    s/v. Nodes are connected within clusters with probability p_in and
    between clusters with probability p_out[1]

    Parameters
    ----------
    n : int
      Number of nodes in the graph
    s : float
      Mean cluster size
    v : float
      Shape parameter. The variance of cluster size distribution is s/v.
    p_in : float
      Probabilty of intra cluster connection.
    p_out : float
      Probability of inter cluster connection.
    directed : boolean, optional default=False
      Whether to create a directed graph or not
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    G : NetworkX Graph or DiGraph
      gaussian random partition graph

    Raises
    ------
    NetworkXError
      If s is > n
      If p_in or p_out is not in [0,1]

    Notes
    -----
    Note the number of partitions is dependent on s,v and n, and that the
    last partition may be considerably smaller, as it is sized to simply
    fill out the nodes [1]

    See Also
    --------
    random_partition_graph

    Examples
    --------
    >>> G = nx.gaussian_random_partition_graph(100,10,10,.25,.1)
    >>> len(G)
    100

    References
    ----------
    .. [1] Ulrik Brandes, Marco Gaertler, Dorothea Wagner,
       Experiments on Graph Clustering Algorithms,
       In the proceedings of the 11th Europ. Symp. Algorithms, 2003.
    """
    if s > n:
        raise nx.NetworkXError("s must be <= n")
    assigned = 0
    sizes = []
    while True:
        size = int(seed.gauss(s, float(s) / v + 0.5))
        if size < 1:  # how to handle 0 or negative sizes?
            continue
        if assigned + size >= n:
            sizes.append(n - assigned)
            break
        assigned += size
        sizes.append(size)
    return random_partition_graph(sizes, p_in, p_out, directed, seed)


def ring_of_cliques(num_cliques, clique_size):
    """Defines a "ring of cliques" graph.

    A ring of cliques graph is consisting of cliques, connected through single
    links. Each clique is a complete graph.

    Parameters
    ----------
    num_cliques : int
        Number of cliques
    clique_size : int
        Size of cliques

    Returns
    -------
    G : NetworkX Graph
        ring of cliques graph

    Raises
    ------
    NetworkXError
        If the number of cliques is lower than 2 or
        if the size of cliques is smaller than 2.

    Examples
    --------
    >>> G = nx.ring_of_cliques(8, 4)

    See Also
    --------
    connected_caveman_graph

    Notes
    -----
    The `connected_caveman_graph` graph removes a link from each clique to
    connect it with the next clique. Instead, the `ring_of_cliques` graph
    simply adds the link without removing any link from the cliques.
    """
    if num_cliques < 2:
        raise nx.NetworkXError('A ring of cliques must have at least '
                               'two cliques')
    if clique_size < 2:
        raise nx.NetworkXError('The cliques must have at least two nodes')

    G = nx.Graph()
    for i in range(num_cliques):
        edges = itertools.combinations(range(i * clique_size, i * clique_size +
                                             clique_size), 2)
        G.add_edges_from(edges)
        G.add_edge(i * clique_size + 1, (i + 1) * clique_size %
                   (num_cliques * clique_size))
    return G


def windmill_graph(n, k):
    """Generate a windmill graph.
    A windmill graph is a graph of `n` cliques each of size `k` that are all
    joined at one node.
    It can be thought of as taking a disjoint union of `n` cliques of size `k`,
    selecting one point from each, and contracting all of the selected points.
    Alternatively, one could generate `n` cliques of size `k-1` and one node
    that is connected to all other nodes in the graph.

    Parameters
    ----------
    n : int
        Number of cliques
    k : int
        Size of cliques

    Returns
    -------
    G : NetworkX Graph
        windmill graph with n cliques of size k

    Raises
    ------
    NetworkXError
        If the number of cliques is less than two
        If the size of the cliques are less than two

    Examples
    --------
    >>> G = nx.windmill_graph(4, 5)

    Notes
    -----
    The node labeled `0` will be the node connected to all other nodes.
    Note that windmill graphs are usually denoted `Wd(k,n)`, so the parameters
    are in the opposite order as the parameters of this method.
    """
    if n < 2:
        msg = 'A windmill graph must have at least two cliques'
        raise nx.NetworkXError(msg)
    if k < 2:
        raise nx.NetworkXError('The cliques must have at least two nodes')

    G = nx.disjoint_union_all(itertools.chain([nx.complete_graph(k)],
                                              (nx.complete_graph(k - 1)
                                               for _ in range(n - 1))))
    G.add_edges_from((0, i) for i in range(k, G.number_of_nodes()))
    return G


@py_random_state(3)
def stochastic_block_model(sizes, p, nodelist=None, seed=None,
                           directed=False, selfloops=False, sparse=True):
    """Return a stochastic block model graph.

    This model partitions the nodes in blocks of arbitrary sizes, and places
    edges between pairs of nodes independently, with a probability that depends
    on the blocks.

    Parameters
    ----------
    sizes : list of ints
        Sizes of blocks
    p : list of list of floats
        Element (r,s) gives the density of edges going from the nodes
        of group r to nodes of group s.
        p must match the number of groups (len(sizes) == len(p)),
        and it must be symmetric if the graph is undirected.
    nodelist : list, optional
        The block tags are assigned according to the node identifiers
        in nodelist. If nodelist is None, then the ordering is the
        range [0,sum(sizes)-1].
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    directed : boolean optional, default=False
        Whether to create a directed graph or not.
    selfloops : boolean optional, default=False
        Whether to include self-loops or not.
    sparse: boolean optional, default=True
        Use the sparse heuristic to speed up the generator.

    Returns
    -------
    g : NetworkX Graph or DiGraph
        Stochastic block model graph of size sum(sizes)

    Raises
    ------
    NetworkXError
      If probabilities are not in [0,1].
      If the probability matrix is not square (directed case).
      If the probability matrix is not symmetric (undirected case).
      If the sizes list does not match nodelist or the probability matrix.
      If nodelist contains duplicate.

    Examples
    --------
    >>> sizes = [75, 75, 300]
    >>> probs = [[0.25, 0.05, 0.02],
    ...          [0.05, 0.35, 0.07],
    ...          [0.02, 0.07, 0.40]]
    >>> g = nx.stochastic_block_model(sizes, probs, seed=0)
    >>> len(g)
    450
    >>> H = nx.quotient_graph(g, g.graph['partition'], relabel=True)
    >>> for v in H.nodes(data=True):
    ...     print(round(v[1]['density'], 3))
    ...
    0.245
    0.348
    0.405
    >>> for v in H.edges(data=True):
    ...     print(round(v[2]['weight'] / (sizes[v[0]] * sizes[v[1]]), 3))
    ...
    0.051
    0.022
    0.07

    See Also
    --------
    random_partition_graph
    planted_partition_graph
    gaussian_random_partition_graph
    gnp_random_graph

    References
    ----------
    .. [1] Holland, P. W., Laskey, K. B., & Leinhardt, S.,
           "Stochastic blockmodels: First steps",
           Social networks, 5(2), 109-137, 1983.
    """
    # Check if dimensions match
    if len(sizes) != len(p):
        raise nx.NetworkXException("'sizes' and 'p' do not match.")
    # Check for probability symmetry (undirected) and shape (directed)
    for row in p:
        if len(p) != len(row):
            raise nx.NetworkXException("'p' must be a square matrix.")
    if not directed:
        p_transpose = [list(i) for i in zip(*p)]
        for i in zip(p, p_transpose):
            for j in zip(i[0], i[1]):
                if abs(j[0] - j[1]) > 1e-08:
                    raise nx.NetworkXException("'p' must be symmetric.")
    # Check for probability range
    for row in p:
        for prob in row:
            if prob < 0 or prob > 1:
                raise nx.NetworkXException("Entries of 'p' not in [0,1].")
    # Check for nodelist consistency
    if nodelist is not None:
        if len(nodelist) != sum(sizes):
            raise nx.NetworkXException("'nodelist' and 'sizes' do not match.")
        if len(nodelist) != len(set(nodelist)):
            raise nx.NetworkXException("nodelist contains duplicate.")
    else:
        nodelist = range(0, sum(sizes))

    # Setup the graph conditionally to the directed switch.
    block_range = range(len(sizes))
    if directed:
        g = nx.DiGraph()
        block_iter = itertools.product(block_range, block_range)
    else:
        g = nx.Graph()
        block_iter = itertools.combinations_with_replacement(block_range, 2)
    # Split nodelist in a partition (list of sets).
    size_cumsum = [sum(sizes[0:x]) for x in range(0, len(sizes) + 1)]
    g.graph['partition'] = [set(nodelist[size_cumsum[x]:size_cumsum[x + 1]])
                            for x in range(0, len(size_cumsum) - 1)]
    # Setup nodes and graph name
    for block_id, nodes in enumerate(g.graph['partition']):
        for node in nodes:
            g.add_node(node, block=block_id)

    g.name = "stochastic_block_model"

    # Test for edge existence
    parts = g.graph['partition']
    for i, j in block_iter:
        if i == j:
            if directed:
                if selfloops:
                    edges = itertools.product(parts[i], parts[i])
                else:
                    edges = itertools.permutations(parts[i], 2)
            else:
                edges = itertools.combinations(parts[i], 2)
                if selfloops:
                    edges = itertools.chain(edges, zip(parts[i], parts[i]))
            for e in edges:
                if seed.random() < p[i][j]:
                    g.add_edge(*e)
        else:
            edges = itertools.product(parts[i], parts[j])
        if sparse:
            if p[i][j] == 1:  # Test edges cases p_ij = 0 or 1
                for e in edges:
                    g.add_edge(*e)
            elif p[i][j] > 0:
                while True:
                    try:
                        logrand = math.log(seed.random())
                        skip = math.floor(logrand / math.log(1 - p[i][j]))
                        # consume "skip" edges
                        next(itertools.islice(edges, skip, skip), None)
                        e = next(edges)
                        g.add_edge(*e)  # __safe
                    except StopIteration:
                        break
        else:
            for e in edges:
                if seed.random() < p[i][j]:
                    g.add_edge(*e)  # __safe
    return g
