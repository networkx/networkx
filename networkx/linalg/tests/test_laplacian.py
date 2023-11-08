import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph
from networkx.generators.expanders import margulis_gabber_galil_graph


class TestLaplacian:
    @classmethod
    def setup_class(cls):
        deg = [3, 2, 2, 1, 0]
        cls.G = havel_hakimi_graph(deg)
        cls.WG = nx.Graph(
            (u, v, {"weight": 0.5, "other": 0.3}) for (u, v) in cls.G.edges()
        )
        cls.WG.add_node(4)
        cls.MG = nx.MultiGraph(cls.G)

        # Graph with clsloops
        cls.Gsl = cls.G.copy()
        for node in cls.Gsl.nodes():
            cls.Gsl.add_edge(node, node)

    def test_laplacian(self):
        "Graph Laplacian"
        # fmt: off
        NL = np.array([[ 3, -1, -1, -1,  0],
                       [-1,  2, -1,  0,  0],
                       [-1, -1,  2,  0,  0],
                       [-1,  0,  0,  1,  0],
                       [ 0,  0,  0,  0,  0]])
        # fmt: on
        WL = 0.5 * NL
        OL = 0.3 * NL
        np.testing.assert_equal(nx.laplacian_matrix(self.G).todense(), NL)
        np.testing.assert_equal(nx.laplacian_matrix(self.MG).todense(), NL)
        np.testing.assert_equal(
            nx.laplacian_matrix(self.G, nodelist=[0, 1]).todense(),
            np.array([[1, -1], [-1, 1]]),
        )
        np.testing.assert_equal(nx.laplacian_matrix(self.WG).todense(), WL)
        np.testing.assert_equal(nx.laplacian_matrix(self.WG, weight=None).todense(), NL)
        np.testing.assert_equal(
            nx.laplacian_matrix(self.WG, weight="other").todense(), OL
        )

    def test_normalized_laplacian(self):
        "Generalized Graph Laplacian"
        # fmt: off
        G = np.array([[ 1.   , -0.408, -0.408, -0.577,  0.],
                      [-0.408,  1.   , -0.5  ,  0.   ,  0.],
                      [-0.408, -0.5  ,  1.   ,  0.   ,  0.],
                      [-0.577,  0.   ,  0.   ,  1.   ,  0.],
                      [ 0.   ,  0.   ,  0.   ,  0.   ,  0.]])
        GL = np.array([[ 1.   , -0.408, -0.408, -0.577,  0.   ],
                       [-0.408,  1.   , -0.5  ,  0.   ,  0.   ],
                       [-0.408, -0.5  ,  1.   ,  0.   ,  0.   ],
                       [-0.577,  0.   ,  0.   ,  1.   ,  0.   ],
                       [ 0.   ,  0.   ,  0.   ,  0.   ,  0.   ]])
        Lsl = np.array([[ 0.75  , -0.2887, -0.2887, -0.3536,  0.    ],
                        [-0.2887,  0.6667, -0.3333,  0.    ,  0.    ],
                        [-0.2887, -0.3333,  0.6667,  0.    ,  0.    ],
                        [-0.3536,  0.    ,  0.    ,  0.5   ,  0.    ],
                        [ 0.    ,  0.    ,  0.    ,  0.    ,  0.    ]])
        # fmt: on

        np.testing.assert_almost_equal(
            nx.normalized_laplacian_matrix(self.G, nodelist=range(5)).todense(),
            G,
            decimal=3,
        )
        np.testing.assert_almost_equal(
            nx.normalized_laplacian_matrix(self.G).todense(), GL, decimal=3
        )
        np.testing.assert_almost_equal(
            nx.normalized_laplacian_matrix(self.MG).todense(), GL, decimal=3
        )
        np.testing.assert_almost_equal(
            nx.normalized_laplacian_matrix(self.WG).todense(), GL, decimal=3
        )
        np.testing.assert_almost_equal(
            nx.normalized_laplacian_matrix(self.WG, weight="other").todense(),
            GL,
            decimal=3,
        )
        np.testing.assert_almost_equal(
            nx.normalized_laplacian_matrix(self.Gsl).todense(), Lsl, decimal=3
        )


def test_directed_laplacian():
    "Directed Laplacian"
    # Graph used as an example in Sec. 4.1 of Langville and Meyer,
    # "Google's PageRank and Beyond". The graph contains dangling nodes, so
    # the pagerank random walk is selected by directed_laplacian
    G = nx.DiGraph()
    G.add_edges_from(
        (
            (1, 2),
            (1, 3),
            (3, 1),
            (3, 2),
            (3, 5),
            (4, 5),
            (4, 6),
            (5, 4),
            (5, 6),
            (6, 4),
        )
    )
    # fmt: off
    GL = np.array([[ 0.9833, -0.2941, -0.3882, -0.0291, -0.0231, -0.0261],
                   [-0.2941,  0.8333, -0.2339, -0.0536, -0.0589, -0.0554],
                   [-0.3882, -0.2339,  0.9833, -0.0278, -0.0896, -0.0251],
                   [-0.0291, -0.0536, -0.0278,  0.9833, -0.4878, -0.6675],
                   [-0.0231, -0.0589, -0.0896, -0.4878,  0.9833, -0.2078],
                   [-0.0261, -0.0554, -0.0251, -0.6675, -0.2078,  0.9833]])
    # fmt: on
    L = nx.directed_laplacian_matrix(G, alpha=0.9, nodelist=sorted(G))
    np.testing.assert_almost_equal(L, GL, decimal=3)

    # Make the graph strongly connected, so we can use a random and lazy walk
    G.add_edges_from(((2, 5), (6, 1)))
    # fmt: off
    GL = np.array([[ 1.    , -0.3062, -0.4714,  0.    ,  0.    , -0.3227],
                   [-0.3062,  1.    , -0.1443,  0.    , -0.3162,  0.    ],
                   [-0.4714, -0.1443,  1.    ,  0.    , -0.0913,  0.    ],
                   [ 0.    ,  0.    ,  0.    ,  1.    , -0.5   , -0.5   ],
                   [ 0.    , -0.3162, -0.0913, -0.5   ,  1.    , -0.25  ],
                   [-0.3227,  0.    ,  0.    , -0.5   , -0.25  ,  1.    ]])
    # fmt: on
    L = nx.directed_laplacian_matrix(
        G, alpha=0.9, nodelist=sorted(G), walk_type="random"
    )
    np.testing.assert_almost_equal(L, GL, decimal=3)

    # fmt: off
    GL = np.array([[ 0.5   , -0.1531, -0.2357,  0.    ,  0.    , -0.1614],
                   [-0.1531,  0.5   , -0.0722,  0.    , -0.1581,  0.    ],
                   [-0.2357, -0.0722,  0.5   ,  0.    , -0.0456,  0.    ],
                   [ 0.    ,  0.    ,  0.    ,  0.5   , -0.25  , -0.25  ],
                   [ 0.    , -0.1581, -0.0456, -0.25  ,  0.5   , -0.125 ],
                   [-0.1614,  0.    ,  0.    , -0.25  , -0.125 ,  0.5   ]])  
    # fmt: on
    L = nx.directed_laplacian_matrix(G, alpha=0.9, nodelist=sorted(G), walk_type="lazy")
    np.testing.assert_almost_equal(L, GL, decimal=3)

    # Make a strongly connected periodic graph
    G = nx.DiGraph()
    G.add_edges_from(((1, 2), (2, 4), (4, 1), (1, 3), (3, 4)))
    # fmt: off
    GL = np.array([[ 0.5  , -0.176, -0.176, -0.25 ],
                   [-0.176,  0.5  ,  0.   , -0.176],
                   [-0.176,  0.   ,  0.5  , -0.176],
                   [-0.25 , -0.176, -0.176,  0.5  ]])
    # fmt: on
    L = nx.directed_laplacian_matrix(G, alpha=0.9, nodelist=sorted(G))
    np.testing.assert_almost_equal(L, GL, decimal=3)


def test_directed_combinatorial_laplacian():
    "Directed combinatorial Laplacian"
    # Graph used as an example in Sec. 4.1 of Langville and Meyer,
    # "Google's PageRank and Beyond". The graph contains dangling nodes, so
    # the pagerank random walk is selected by directed_laplacian
    G = nx.DiGraph()
    G.add_edges_from(
        (
            (1, 2),
            (1, 3),
            (3, 1),
            (3, 2),
            (3, 5),
            (4, 5),
            (4, 6),
            (5, 4),
            (5, 6),
            (6, 4),
        )
    )
    # fmt: off
    GL = np.array([[ 0.0366, -0.0132, -0.0153, -0.0034, -0.0020, -0.0027],
                   [-0.0132,  0.0450, -0.0111, -0.0076, -0.0062, -0.0069],
                   [-0.0153, -0.0111,  0.0408, -0.0035, -0.0083, -0.0027],
                   [-0.0034, -0.0076, -0.0035,  0.3688, -0.1356, -0.2187],
                   [-0.0020, -0.0062, -0.0083, -0.1356,  0.2026, -0.0505],
                   [-0.0027, -0.0069, -0.0027, -0.2187, -0.0505,  0.2815]])
    # fmt: on

    L = nx.directed_combinatorial_laplacian_matrix(G, alpha=0.9, nodelist=sorted(G))
    np.testing.assert_almost_equal(L, GL, decimal=3)

    # Make the graph strongly connected, so we can use a random and lazy walk
    G.add_edges_from(((2, 5), (6, 1)))

    # fmt: off
    GL = np.array([[ 0.1395, -0.0349, -0.0465,  0.    ,  0.    , -0.0581],
                   [-0.0349,  0.093 , -0.0116,  0.    , -0.0465,  0.    ],
                   [-0.0465, -0.0116,  0.0698,  0.    , -0.0116,  0.    ],
                   [ 0.    ,  0.    ,  0.    ,  0.2326, -0.1163, -0.1163],
                   [ 0.    , -0.0465, -0.0116, -0.1163,  0.2326, -0.0581],
                   [-0.0581,  0.    ,  0.    , -0.1163, -0.0581,  0.2326]])
    # fmt: on

    L = nx.directed_combinatorial_laplacian_matrix(
        G, alpha=0.9, nodelist=sorted(G), walk_type="random"
    )
    np.testing.assert_almost_equal(L, GL, decimal=3)

    # fmt: off
    GL = np.array([[ 0.0698, -0.0174, -0.0233,  0.    ,  0.    , -0.0291],
                   [-0.0174,  0.0465, -0.0058,  0.    , -0.0233,  0.    ],
                   [-0.0233, -0.0058,  0.0349,  0.    , -0.0058,  0.    ],
                   [ 0.    ,  0.    ,  0.    ,  0.1163, -0.0581, -0.0581],
                   [ 0.    , -0.0233, -0.0058, -0.0581,  0.1163, -0.0291],
                   [-0.0291,  0.    ,  0.    , -0.0581, -0.0291,  0.1163]])
    # fmt: on

    L = nx.directed_combinatorial_laplacian_matrix(
        G, alpha=0.9, nodelist=sorted(G), walk_type="lazy"
    )
    np.testing.assert_almost_equal(L, GL, decimal=3)

    E = nx.DiGraph(margulis_gabber_galil_graph(2))
    L = nx.directed_combinatorial_laplacian_matrix(E)
    # fmt: off
    expected = np.array(
        [[ 0.16666667, -0.08333333, -0.08333333,  0.        ],
         [-0.08333333,  0.16666667,  0.        , -0.08333333],
         [-0.08333333,  0.        ,  0.16666667, -0.08333333],
         [ 0.        , -0.08333333, -0.08333333,  0.16666667]]
    )
    # fmt: on
    np.testing.assert_almost_equal(L, expected, decimal=6)

    with pytest.raises(nx.NetworkXError):
        nx.directed_combinatorial_laplacian_matrix(G, walk_type="pagerank", alpha=100)
    with pytest.raises(nx.NetworkXError):
        nx.directed_combinatorial_laplacian_matrix(G, walk_type="silly")


class TestTotalSpanningTreeWeight:
    @classmethod
    def setup_class(cls):
        global np
        np = pytest.importorskip("numpy")

    def test_tstw_disconnected(self):
        G = nx.empty_graph(2)
        with pytest.raises(nx.NetworkXError):
            nx.total_spanning_tree_weight(G)

    def test_tstw_no_nodes(self):
        G = nx.Graph()
        with pytest.raises(nx.NetworkXPointlessConcept):
            nx.total_spanning_tree_weight(G)

    def test_tstw_weight(self):
        # weights are ignored
        G = nx.Graph()
        G.add_edge(1, 2, weight=1)
        G.add_edge(1, 3, weight=1)
        G.add_edge(2, 3, weight=2)
        assert np.isclose(nx.total_spanning_tree_weight(G, "weight"), 5)

    def test_tstw_negative_weight(self):
        # weights are ignored
        G = nx.Graph()
        G.add_edge(1, 2, weight=1)
        G.add_edge(1, 3, weight=-1)
        G.add_edge(2, 3, weight=-2)
        assert np.isclose(nx.total_spanning_tree_weight(G, "weight"), -1)

    def test_tstw_selfloop(self):
        # self-loops are ignored
        G = nx.complete_graph(3)
        G.add_edge(1, 1)
        Nst = nx.total_spanning_tree_weight(G)
        test_data = 3
        assert np.isclose(Nst, test_data)

    def test_tstw_multigraph(self):
        G = nx.MultiGraph()
        G.add_edge(1, 2)
        G.add_edge(1, 2)
        G.add_edge(1, 3)
        G.add_edge(2, 3)
        Nst = nx.total_spanning_tree_weight(G)
        test_data = 5
        assert np.isclose(Nst, test_data)

    def test_tstw_complete_graph(self):
        N = 5
        G = nx.complete_graph(N)
        Nst = nx.total_spanning_tree_weight(G)
        test_data = N ** (N - 2)
        assert np.isclose(Nst, test_data)

    def test_tstw_path_graph(self):
        N = 5
        G = nx.path_graph(N)
        Nst = nx.total_spanning_tree_weight(G)
        test_data = 1
        assert np.isclose(Nst, test_data)

    def test_tstw_cycle_graph(self):
        N = 5
        G = nx.cycle_graph(N)
        Nst = nx.total_spanning_tree_weight(G)
        test_data = N
        assert np.isclose(Nst, test_data)

    def test_tstw_directed_noroot(self):
        G = nx.MultiDiGraph()
        with pytest.raises(nx.NetworkXError):
            nx.total_spanning_tree_weight(G)

    def test_tstw_directed_root_not_exist(self):
        G = nx.MultiDiGraph()
        with pytest.raises(nx.NetworkXError):
            nx.total_spanning_tree_weight(G, root=0)

    def test_tstw_directed_not_weak_connected(self):
        G = nx.MultiDiGraph()
        G.add_edge(1, 2)
        G.add_edge(3, 4)
        with pytest.raises(nx.NetworkXError):
            nx.total_spanning_tree_weight(G, root=0)

    def test_tstw_directed_cycle_graph(self):
        G = nx.DiGraph()
        G = nx.cycle_graph(7, G)
        Nst = nx.total_spanning_tree_weight(G, root=0)
        test_data = 1
        assert np.isclose(Nst, test_data)

    def test_tstw_directed_complete_graph(self):
        G = nx.DiGraph()
        G = nx.complete_graph(7, G)
        Nst = nx.total_spanning_tree_weight(G, root=0)
        test_data = 7**5
        assert np.isclose(Nst, test_data)

    def test_tstw_directed_multi(self):
        G = nx.MultiDiGraph()
        G = nx.cycle_graph(3, G)
        G.add_edge(1, 2)
        Nst = nx.total_spanning_tree_weight(G, root=0)
        test_data = 2
        assert np.isclose(Nst, test_data)

    def test_tstw_directed_selfloop(self):
        G = nx.MultiDiGraph()
        G = nx.cycle_graph(3, G)
        G.add_edge(1, 1)
        Nst = nx.total_spanning_tree_weight(G, root=0)
        test_data = 1
        assert np.isclose(Nst, test_data)

    def test_tstw_directed_weak_connected(self):
        G = nx.MultiDiGraph()
        G = nx.cycle_graph(3, G)
        G.remove_edge(1, 2)
        Nst = nx.total_spanning_tree_weight(G, root=0)
        test_data = 0
        assert np.isclose(Nst, test_data)

    def test_tstw_directed_weighted(self):
        G = nx.DiGraph()
        G.add_edge(1, 2, weight=1)
        G.add_edge(1, 3, weight=2)
        G.add_edge(2, 3, weight=3)
        Nst = nx.total_spanning_tree_weight(G, root=1, weight="weight")
        assert np.isclose(Nst, 0)
        Nst = nx.total_spanning_tree_weight(G, root=2, weight="weight")
        assert np.isclose(Nst, 0)
        Nst = nx.total_spanning_tree_weight(G, root=3, weight="weight")
        assert np.isclose(Nst, 9)
