"""
Various small and named graphs, together with some compact generators.

"""

__all__ = [
    "make_small_graph",
    "LCF_graph",
    "bull_graph",
    "chvatal_graph",
    "cubical_graph",
    "desargues_graph",
    "diamond_graph",
    "dodecahedral_graph",
    "frucht_graph",
    "heawood_graph",
    "hoffman_singleton_graph",
    "house_graph",
    "house_x_graph",
    "icosahedral_graph",
    "krackhardt_kite_graph",
    "moebius_kantor_graph",
    "octahedral_graph",
    "pappus_graph",
    "petersen_graph",
    "sedgewick_maze_graph",
    "tetrahedral_graph",
    "truncated_cube_graph",
    "truncated_tetrahedron_graph",
    "tutte_graph",
]

import networkx as nx
from networkx.generators.classic import (
    empty_graph,
    cycle_graph,
    path_graph,
    complete_graph,
)
from networkx.exception import NetworkXError


def make_small_undirected_graph(graph_description, create_using=None):
    """
    Return a small undirected graph described by graph_description.

    See make_small_graph.
    """
    G = empty_graph(0, create_using)
    if G.is_directed():
        raise NetworkXError("Directed Graph not supported")
    return make_small_graph(graph_description, G)


def make_small_graph(graph_description, create_using=None):
    """
    Return the small graph described by graph_description.

    graph_description is a list of the form [ltype,name,n,xlist]

    Here ltype is one of "adjacencylist" or "edgelist",
    name is the name of the graph and n the number of nodes.
    This constructs a graph of n nodes with integer labels 0,..,n-1.

    If ltype="adjacencylist"  then xlist is an adjacency list
    with exactly n entries, in with the j'th entry (which can be empty)
    specifies the nodes connected to vertex j.
    e.g. the "square" graph C_4 can be obtained by

    >>> G = nx.make_small_graph(
    ...     ["adjacencylist", "C_4", 4, [[2, 4], [1, 3], [2, 4], [1, 3]]]
    ... )

    or, since we do not need to add edges twice,

    >>> G = nx.make_small_graph(["adjacencylist", "C_4", 4, [[2, 4], [3], [4], []]])

    If ltype="edgelist" then xlist is an edge list
    written as [[v1,w2],[v2,w2],...,[vk,wk]],
    where vj and wj integers in the range 1,..,n
    e.g. the "square" graph C_4 can be obtained by

    >>> G = nx.make_small_graph(
    ...     ["edgelist", "C_4", 4, [[1, 2], [3, 4], [2, 3], [4, 1]]]
    ... )

    Use the create_using argument to choose the graph class/type.
    """

    if graph_description[0] not in ("adjacencylist", "edgelist"):
        raise NetworkXError("ltype must be either adjacencylist or edgelist")

    ltype = graph_description[0]
    name = graph_description[1]
    n = graph_description[2]

    G = empty_graph(n, create_using)
    nodes = G.nodes()

    if ltype == "adjacencylist":
        adjlist = graph_description[3]
        if len(adjlist) != n:
            raise NetworkXError("invalid graph_description")
        G.add_edges_from([(u - 1, v) for v in nodes for u in adjlist[v]])
    elif ltype == "edgelist":
        edgelist = graph_description[3]
        for e in edgelist:
            v1 = e[0] - 1
            v2 = e[1] - 1
            if v1 < 0 or v1 > n - 1 or v2 < 0 or v2 > n - 1:
                raise NetworkXError("invalid graph_description")
            else:
                G.add_edge(v1, v2)
    G.name = name
    return G


def LCF_graph(n, shift_list, repeats, create_using=None):
    """
    Return the cubic graph specified in LCF notation.

    LCF notation (LCF=Lederberg-Coxeter-Fruchte) is a compressed
    notation used in the generation of various cubic Hamiltonian
    graphs of high symmetry. See, for example, dodecahedral_graph,
    desargues_graph, heawood_graph and pappus_graph below.

    n (number of nodes)
      The starting graph is the n-cycle with nodes 0,...,n-1.
      (The null graph is returned if n < 0.)

    shift_list = [s1,s2,..,sk], a list of integer shifts mod n,

    repeats
      integer specifying the number of times that shifts in shift_list
      are successively applied to each v_current in the n-cycle
      to generate an edge between v_current and v_current+shift mod n.

    For v1 cycling through the n-cycle a total of k*repeats
    with shift cycling through shiftlist repeats times connect
    v1 with v1+shift mod n

    The utility graph $K_{3,3}$

    >>> G = nx.LCF_graph(6, [3, -3], 3)

    The Heawood graph

    >>> G = nx.LCF_graph(14, [5, -5], 7)

    See http://mathworld.wolfram.com/LCFNotation.html for a description
    and references.

    """
    if n <= 0:
        return empty_graph(0, create_using)

    # start with the n-cycle
    G = cycle_graph(n, create_using)
    if G.is_directed():
        raise NetworkXError("Directed Graph not supported")
    G.name = "LCF_graph"
    nodes = sorted(list(G))

    n_extra_edges = repeats * len(shift_list)
    # edges are added n_extra_edges times
    # (not all of these need be new)
    if n_extra_edges < 1:
        return G

    for i in range(n_extra_edges):
        shift = shift_list[i % len(shift_list)]  # cycle through shift_list
        v1 = nodes[i % n]  # cycle repeatedly through nodes
        v2 = nodes[(i + shift) % n]
        G.add_edge(v1, v2)
    return G


# -------------------------------------------------------------------------------
#   Various small and named graphs
# -------------------------------------------------------------------------------


def bull_graph(create_using=None):
    """
    Returns the Bull Graph

    The Bull Graph has 5 nodes and 5 edges. It is a planar undirected
    graph in the form of a triangle with two disjoint pendant edges [1]_
    The name comes from the triangle and pendant edges representing
    respectively the body and legs of a bull.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        A bull graph with 5 nodes

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Bull_graph.

    """
    description = [
        "adjacencylist",
        "Bull Graph",
        5,
        [[2, 3], [1, 3, 4], [1, 2, 5], [2], [3]],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def chvatal_graph(create_using=None):
    """
    Returns the Chvátal Graph

    The Chvátal Graph is an undirected graph with 12 nodes and 24 edges [1]_.
    It has 370 distinct (directed) Hamiltonian cycles, giving a unique generalized
    LCF notation of order 4, two of order 6 , and 43 of order 1 [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        The Chvátal graph with 12 nodes and 24 edges

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Chv%C3%A1tal_graph
    .. [2] https://mathworld.wolfram.com/ChvatalGraph.html

    """
    description = [
        "adjacencylist",
        "Chvatal Graph",
        12,
        [
            [2, 5, 7, 10],
            [3, 6, 8],
            [4, 7, 9],
            [5, 8, 10],
            [6, 9],
            [11, 12],
            [11, 12],
            [9, 12],
            [11],
            [11, 12],
            [],
            [],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def cubical_graph(create_using=None):
    """
    Returns the 3-regular Platonic Cubical Graph

    The skeleton of the cube (the nodes and edges) form a graph, with 8
    nodes, and 12 edges. It is a special case of the hypercube graph.
    It is one of 5 Platonic graphs, each a skeleton of its
    Platonic solid [1]_.
    Such graphs arise in parallel processing in computers.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        A cubical graph with 8 nodes and 12 edges

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Cube#Cubical_graph

    """
    description = [
        "adjacencylist",
        "Platonic Cubical Graph",
        8,
        [
            [2, 4, 5],
            [1, 3, 8],
            [2, 4, 7],
            [1, 3, 6],
            [1, 6, 8],
            [4, 5, 7],
            [3, 6, 8],
            [2, 5, 7],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def desargues_graph(create_using=None):
    """
    Returns the Desargues Graph

    The Desargues Graph is a non-planar, distance-transitive cubic graph
    with 20 nodes and 30 edges [1]_.
    It is a symmetric graph. It can be represented in LCF notation
    as [5,-5,9,-9]^5 [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Desargues Graph with 20 nodes and 30 edges

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Desargues_graph
    .. [2] https://mathworld.wolfram.com/DesarguesGraph.html
    """
    G = LCF_graph(20, [5, -5, 9, -9], 5, create_using)
    G.name = "Desargues Graph"
    return G


def diamond_graph(create_using=None):
    """
    Returns the Diamond graph

    The Diamond Graph is  planar undirected graph with 4 nodes and 5 edges.
    It is also sometimes known as the double triangle graph or kite graph [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Diamond Graph with 4 nodes and 5 edges

    References
    ----------
    .. [1] https://mathworld.wolfram.com/DiamondGraph.html
    """
    description = [
        "adjacencylist",
        "Diamond Graph",
        4,
        [[2, 3], [1, 3, 4], [1, 2, 4], [2, 3]],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def dodecahedral_graph(create_using=None):
    """
    Returns the Platonic Dodecahedral graph.

    The dodecahedral graph has 20 nodes and 30 edges. The skeleton of the
    dodecahedron forms a graph. It is one of 5 Platonic graphs [1]_.
    It can be described in LCF notation as:
    ``[10, 7, 4, -4, -7, 10, -4, 7, -7, 4]^2`` [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Dodecahedral Graph with 20 nodes and 30 edges

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Regular_dodecahedron#Dodecahedral_graph
    .. [2] https://mathworld.wolfram.com/DodecahedralGraph.html

    """
    G = LCF_graph(20, [10, 7, 4, -4, -7, 10, -4, 7, -7, 4], 2, create_using)
    G.name = "Dodecahedral Graph"
    return G


def frucht_graph(create_using=None):
    """
    Returns the Frucht Graph.

    The Frucht Graph is the smallest cubical graph whose
    automorphism group consists only of the identity element [1]_.
    It has 12 nodes and 18 edges and no nontrivial symmetries.
    It is planar and Hamiltonian [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Frucht Graph with 12 nodes and 18 edges

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Frucht_graph
    .. [2] https://mathworld.wolfram.com/FruchtGraph.html

    """
    G = cycle_graph(7, create_using)
    G.add_edges_from(
        [
            [0, 7],
            [1, 7],
            [2, 8],
            [3, 9],
            [4, 9],
            [5, 10],
            [6, 10],
            [7, 11],
            [8, 11],
            [8, 9],
            [10, 11],
        ]
    )

    G.name = "Frucht Graph"
    return G


def heawood_graph(create_using=None):
    """
    Returns the Heawood Graph, a (3,6) cage.

    The Heawood Graph is an undirected graph with 14 nodes and 21 edges,
    named after Percy John Heawood [1]_.
    It is cubic symmetric, nonplanar, Hamiltonian, and can be represented
    in LCF notation as ``[5,-5]^7`` [2]_.
    It is the unique (3,6)-cage: the regular cubic graph of girth 6 with
    minimal number of vertices [3]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Heawood Graph with 14 nodes and 21 edges

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Heawood_graph
    .. [2] https://mathworld.wolfram.com/HeawoodGraph.html
    .. [3] https://www.win.tue.nl/~aeb/graphs/Heawood.html

    """
    G = LCF_graph(14, [5, -5], 7, create_using)
    G.name = "Heawood Graph"
    return G


def hoffman_singleton_graph():
    """
    Returns the Hoffman-Singleton Graph.

    The Hoffman–Singleton graph is a symmetrical undirected graph
    with 50 nodes and 175 edges.
    All indices lie in ``Z % 5``: that is, the integers mod 5 [1]_.
    It is the only regular graph of vertex degree 7, diameter 2, and girth 5.
    It is the unique (7,5)-cage graph and Moore graph, and contains many
    copies of the Petersen graph [2]_.

    Returns
    -------
    G : networkx Graph
        Hoffman–Singleton Graph with 50 nodes and 175 edges

    Notes
    -----
    Constructed from pentagon and pentagram as follows: Take five pentagons $P_h$
    and five pentagrams $Q_i$ . Join vertex $j$ of $P_h$ to vertex $h·i+j$ of $Q_i$ [3]_.

    References
    ----------
    .. [1] https://blogs.ams.org/visualinsight/2016/02/01/hoffman-singleton-graph/
    .. [2] https://mathworld.wolfram.com/Hoffman-SingletonGraph.html
    .. [3] https://en.wikipedia.org/wiki/Hoffman%E2%80%93Singleton_graph

    """
    G = nx.Graph()
    for i in range(5):
        for j in range(5):
            G.add_edge(("pentagon", i, j), ("pentagon", i, (j - 1) % 5))
            G.add_edge(("pentagon", i, j), ("pentagon", i, (j + 1) % 5))
            G.add_edge(("pentagram", i, j), ("pentagram", i, (j - 2) % 5))
            G.add_edge(("pentagram", i, j), ("pentagram", i, (j + 2) % 5))
            for k in range(5):
                G.add_edge(("pentagon", i, j), ("pentagram", k, (i * k + j) % 5))
    G = nx.convert_node_labels_to_integers(G)
    G.name = "Hoffman-Singleton Graph"
    return G


def house_graph(create_using=None):
    """
    Returns the House graph (square with triangle on top)

    The house graph is a simple undirected graph with
    5 nodes and 6 edges [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        House graph in the form of a square with a triangle on top

    References
    ----------
    .. [1] https://mathworld.wolfram.com/HouseGraph.html
    """
    description = [
        "adjacencylist",
        "House Graph",
        5,
        [[2, 3], [1, 4], [1, 4, 5], [2, 3, 5], [3, 4]],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def house_x_graph(create_using=None):
    """
    Returns the House graph with a cross inside the house square.

    The House X-graph is the House graph plus the two edges connecting diagonally
    opposite vertices of the square base. It is also one of the two graphs
    obtained by removing two edges from the pentatope graph [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        House graph with diagonal vertices connected

    References
    ----------
    .. [1] https://mathworld.wolfram.com/HouseGraph.html
    """
    description = [
        "adjacencylist",
        "House-with-X-inside Graph",
        5,
        [[2, 3, 4], [1, 3, 4], [1, 2, 4, 5], [1, 2, 3, 5], [3, 4]],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def icosahedral_graph(create_using=None):
    """
    Returns the Platonic Icosahedral graph.

    The icosahedral graph has 12 nodes and 30 edges. It is a Platonic graph
    whose nodes have the connectivity of the icosahedron. It is undirected,
    regular and Hamiltonian [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Icosahedral graph with 12 nodes and 30 edges.

    References
    ----------
    .. [1] https://mathworld.wolfram.com/IcosahedralGraph.html
    """
    description = [
        "adjacencylist",
        "Platonic Icosahedral Graph",
        12,
        [
            [2, 6, 8, 9, 12],
            [3, 6, 7, 9],
            [4, 7, 9, 10],
            [5, 7, 10, 11],
            [6, 7, 11, 12],
            [7, 12],
            [],
            [9, 10, 11, 12],
            [10],
            [11],
            [12],
            [],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def krackhardt_kite_graph(create_using=None):
    """
    Returns the Krackhardt Kite Social Network.

    A 10 actor social network introduced by David Krackhardt
    to illustrate different centrality measures [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Krackhardt Kite graph with 10 nodes and 18 edges

    Notes
    -----
    The traditional labeling is:
    Andre=1, Beverley=2, Carol=3, Diane=4,
    Ed=5, Fernando=6, Garth=7, Heather=8, Ike=9, Jane=10.

    References
    ----------
    .. [1] Krackhardt, David. "Assessing the Political Landscape: Structure,
       Cognition, and Power in Organizations". Administrative Science Quarterly.
       35 (2): 342–369. doi:10.2307/2393394. JSTOR 2393394. June 1990.

    """
    description = [
        "adjacencylist",
        "Krackhardt Kite Social Network",
        10,
        [
            [2, 3, 4, 6],
            [1, 4, 5, 7],
            [1, 4, 6],
            [1, 2, 3, 5, 6, 7],
            [2, 4, 7],
            [1, 3, 4, 7, 8],
            [2, 4, 5, 6, 8],
            [6, 7, 9],
            [8, 10],
            [9],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def moebius_kantor_graph(create_using=None):
    """
    Returns the Moebius-Kantor graph.

    The Möbius-Kantor graph is the cubic symmetric graph on 16 nodes.
    Its LCF notation is [5,-5]^8, and it is isomorphic to the generalized
    Petersen graph [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Moebius-Kantor graph

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/M%C3%B6bius%E2%80%93Kantor_graph

    """
    G = LCF_graph(16, [5, -5], 8, create_using)
    G.name = "Moebius-Kantor Graph"
    return G


def octahedral_graph(create_using=None):
    """
    Returns the Platonic Octahedral graph.

    The octahedral graph is the 6-node 12-edge Platonic graph having the
    connectivity of the octahedron [1]_. If 6 couples go to a party,
    and each person shakes hands with every person except his or her partner,
    then this graph describes the set of handshakes that take place;
    for this reason it is also called the cocktail party graph [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Octahedral graph

    References
    ----------
    .. [1] https://mathworld.wolfram.com/OctahedralGraph.html
    .. [2] https://en.wikipedia.org/wiki/Tur%C3%A1n_graph#Special_cases

    """
    description = [
        "adjacencylist",
        "Platonic Octahedral Graph",
        6,
        [[2, 3, 4, 5], [3, 4, 6], [5, 6], [5, 6], [6], []],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def pappus_graph():
    """
    Returns the Pappus graph.

    The Pappus graph is a cubic symmetric distance-regular graph with 18 nodes
    and 27 edges. It is Hamiltonian and can be represented in LCF notation as
    [5,7,-7,7,-7,-5]^3 [1]_.

    Returns
    -------
    G : networkx Graph
        Pappus graph

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Pappus_graph
    """
    G = LCF_graph(18, [5, 7, -7, 7, -7, -5], 3)
    G.name = "Pappus Graph"
    return G


def petersen_graph(create_using=None):
    """
    Returns the Petersen graph.

    The Peterson graph is a cubic, undirected graph with 10 nodes and 15 edges [1]_.
    Julius Petersen constructed the graph as the smallest counterexample
    against the claim that a connected bridgeless cubic graph
    has an edge colouring with three colours [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Petersen graph

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Petersen_graph
    .. [2] https://www.win.tue.nl/~aeb/drg/graphs/Petersen.html
    """
    description = [
        "adjacencylist",
        "Petersen Graph",
        10,
        [
            [2, 5, 6],
            [1, 3, 7],
            [2, 4, 8],
            [3, 5, 9],
            [4, 1, 10],
            [1, 8, 9],
            [2, 9, 10],
            [3, 6, 10],
            [4, 6, 7],
            [5, 7, 8],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def sedgewick_maze_graph(create_using=None):
    """
    Return a small maze with a cycle.

    This is the maze used in Sedgewick, 3rd Edition, Part 5, Graph
    Algorithms, Chapter 18, e.g. Figure 18.2 and following [1]_.
    Nodes are numbered 0,..,7

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Small maze with a cycle

    References
    ----------
    .. [1] Figure 18.2, Chapter 18, Graph Algorithms (3rd Ed), Sedgewick
    """
    G = empty_graph(0, create_using)
    G.add_nodes_from(range(8))
    G.add_edges_from([[0, 2], [0, 7], [0, 5]])
    G.add_edges_from([[1, 7], [2, 6]])
    G.add_edges_from([[3, 4], [3, 5]])
    G.add_edges_from([[4, 5], [4, 7], [4, 6]])
    G.name = "Sedgewick Maze"
    return G


def tetrahedral_graph(create_using=None):
    """
    Returns the 3-regular Platonic Tetrahedral graph.

    Tetrahedral graph has 4 nodes and 6 edges. It is a
    special case of the complete graph, K4, and wheel graph, W4.
    It is one of the 5 platonic graphs [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Tetrahedral Grpah

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Tetrahedron#Tetrahedral_graph

    """
    G = complete_graph(4, create_using)
    G.name = "Platonic Tetrahedral graph"
    return G


def truncated_cube_graph(create_using=None):
    """
    Returns the skeleton of the truncated cube.

    The truncated cube is an Archimedean solid with 14 regular
    faces (6 octagonal and 8 triangular), 36 edges and 24 nodes [1]_.
    The truncated cube is created by truncating (cutting off) the tips
    of the cube one third of the way into each edge [2]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Skeleton of the truncated cube

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Truncated_cube
    .. [2] https://www.coolmath.com/reference/polyhedra-truncated-cube

    """
    description = [
        "adjacencylist",
        "Truncated Cube Graph",
        24,
        [
            [2, 3, 5],
            [12, 15],
            [4, 5],
            [7, 9],
            [6],
            [17, 19],
            [8, 9],
            [11, 13],
            [10],
            [18, 21],
            [12, 13],
            [15],
            [14],
            [22, 23],
            [16],
            [20, 24],
            [18, 19],
            [21],
            [20],
            [24],
            [22],
            [23],
            [24],
            [],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G


def truncated_tetrahedron_graph(create_using=None):
    """
    Returns the skeleton of the truncated Platonic tetrahedron.

    The truncated tetrahedron is an Archimedean solid with 4 regular hexagonal faces,
    4 equilateral triangle faces, 12 nodes and 18 edges. It can be constructed by truncating
    all 4 vertices of a regular tetrahedron at one third of the original edge length [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Skeleton of the truncated tetrahedron

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Truncated_tetrahedron

    """
    G = path_graph(12, create_using)
    #    G.add_edges_from([(1,3),(1,10),(2,7),(4,12),(5,12),(6,8),(9,11)])
    G.add_edges_from([(0, 2), (0, 9), (1, 6), (3, 11), (4, 11), (5, 7), (8, 10)])
    G.name = "Truncated Tetrahedron Graph"
    return G


def tutte_graph(create_using=None):
    """
    Returns the Tutte graph.

    The Tutte graph is a cubic polyhedral, non-Hamiltonian graph. It has
    46 nodes and 69 edges.
    It is a counterexample to Tait's conjecture that every 3-regular polyhedron
    has a Hamiltonian cycle.
    It can be realized geometrically from a tetrahedron by multiply truncating
    three of its vertices [1]_.

    Parameters
    ----------
    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : networkx Graph
        Tutte graph

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Tutte_graph
    """
    description = [
        "adjacencylist",
        "Tutte's Graph",
        46,
        [
            [2, 3, 4],
            [5, 27],
            [11, 12],
            [19, 20],
            [6, 34],
            [7, 30],
            [8, 28],
            [9, 15],
            [10, 39],
            [11, 38],
            [40],
            [13, 40],
            [14, 36],
            [15, 16],
            [35],
            [17, 23],
            [18, 45],
            [19, 44],
            [46],
            [21, 46],
            [22, 42],
            [23, 24],
            [41],
            [25, 28],
            [26, 33],
            [27, 32],
            [34],
            [29],
            [30, 33],
            [31],
            [32, 34],
            [33],
            [],
            [],
            [36, 39],
            [37],
            [38, 40],
            [39],
            [],
            [],
            [42, 45],
            [43],
            [44, 46],
            [45],
            [],
            [],
        ],
    ]
    G = make_small_undirected_graph(description, create_using)
    return G
