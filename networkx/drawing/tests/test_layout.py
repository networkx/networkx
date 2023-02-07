"""Unit tests for layout functions."""
import pytest

import networkx as nx

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestLayout:
    @classmethod
    def setup_class(cls):
        cls.Gi = nx.grid_2d_graph(5, 5)
        cls.Gs = nx.Graph()
        nx.add_path(cls.Gs, "abcdef")
        cls.bigG = nx.grid_2d_graph(25, 25)  # > 500 nodes for sparse

    def test_spring_fixed_without_pos(self):
        G = nx.path_graph(4)
        pytest.raises(ValueError, nx.spring_layout, G, fixed=[0])
        pos = {0: (1, 1), 2: (0, 0)}
        pytest.raises(ValueError, nx.spring_layout, G, fixed=[0, 1], pos=pos)
        nx.spring_layout(G, fixed=[0, 2], pos=pos)  # No ValueError

    def test_spring_init_pos(self):
        # Tests GH #2448
        import math

        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 0), (2, 3)])

        init_pos = {0: (0.0, 0.0)}
        fixed_pos = [0]
        pos = nx.fruchterman_reingold_layout(G, pos=init_pos, fixed=fixed_pos)
        has_nan = any(math.isnan(c) for coords in pos.values() for c in coords)
        assert not has_nan, "values should not be nan"

    def test_smoke_empty_graph(self):
        G = []
        nx.random_layout(G)
        nx.circular_layout(G)
        nx.planar_layout(G)
        nx.spring_layout(G)
        nx.fruchterman_reingold_layout(G)
        nx.spectral_layout(G)
        nx.shell_layout(G)
        nx.bipartite_layout(G, G)
        nx.spiral_layout(G)
        nx.multipartite_layout(G)
        nx.kamada_kawai_layout(G)

    def test_smoke_int(self):
        G = self.Gi
        nx.random_layout(G)
        nx.circular_layout(G)
        nx.planar_layout(G)
        nx.spring_layout(G)
        nx.fruchterman_reingold_layout(G)
        nx.fruchterman_reingold_layout(self.bigG)
        nx.spectral_layout(G)
        nx.spectral_layout(G.to_directed())
        nx.spectral_layout(self.bigG)
        nx.spectral_layout(self.bigG.to_directed())
        nx.shell_layout(G)
        nx.spiral_layout(G)
        nx.kamada_kawai_layout(G)
        nx.kamada_kawai_layout(G, dim=1)
        nx.kamada_kawai_layout(G, dim=3)
        nx.arf_layout(G)

    def test_smoke_string(self):
        G = self.Gs
        nx.random_layout(G)
        nx.circular_layout(G)
        nx.planar_layout(G)
        nx.spring_layout(G)
        nx.fruchterman_reingold_layout(G)
        nx.spectral_layout(G)
        nx.shell_layout(G)
        nx.spiral_layout(G)
        nx.kamada_kawai_layout(G)
        nx.kamada_kawai_layout(G, dim=1)
        nx.kamada_kawai_layout(G, dim=3)
        nx.arf_layout(G)

    def check_scale_and_center(self, pos, scale, center):
        center = np.array(center)
        low = center - scale
        hi = center + scale
        vpos = np.array(list(pos.values()))
        length = vpos.max(0) - vpos.min(0)
        assert (length <= 2 * scale).all()
        assert (vpos >= low).all()
        assert (vpos <= hi).all()

    def test_scale_and_center_arg(self):
        sc = self.check_scale_and_center
        c = (4, 5)
        G = nx.complete_graph(9)
        G.add_node(9)
        sc(nx.random_layout(G, center=c), scale=0.5, center=(4.5, 5.5))
        # rest can have 2*scale length: [-scale, scale]
        sc(nx.spring_layout(G, scale=2, center=c), scale=2, center=c)
        sc(nx.spectral_layout(G, scale=2, center=c), scale=2, center=c)
        sc(nx.circular_layout(G, scale=2, center=c), scale=2, center=c)
        sc(nx.shell_layout(G, scale=2, center=c), scale=2, center=c)
        sc(nx.spiral_layout(G, scale=2, center=c), scale=2, center=c)
        sc(nx.kamada_kawai_layout(G, scale=2, center=c), scale=2, center=c)

        c = (2, 3, 5)
        sc(nx.kamada_kawai_layout(G, dim=3, scale=2, center=c), scale=2, center=c)

    def test_planar_layout_non_planar_input(self):
        G = nx.complete_graph(9)
        pytest.raises(nx.NetworkXException, nx.planar_layout, G)

    def test_smoke_planar_layout_embedding_input(self):
        embedding = nx.PlanarEmbedding()
        embedding.set_data({0: [1, 2], 1: [0, 2], 2: [0, 1]})
        nx.planar_layout(embedding)

    def test_default_scale_and_center(self):
        sc = self.check_scale_and_center
        c = (0, 0)
        G = nx.complete_graph(9)
        G.add_node(9)
        sc(nx.random_layout(G), scale=0.5, center=(0.5, 0.5))
        sc(nx.spring_layout(G), scale=1, center=c)
        sc(nx.spectral_layout(G), scale=1, center=c)
        sc(nx.circular_layout(G), scale=1, center=c)
        sc(nx.shell_layout(G), scale=1, center=c)
        sc(nx.spiral_layout(G), scale=1, center=c)
        sc(nx.kamada_kawai_layout(G), scale=1, center=c)

        c = (0, 0, 0)
        sc(nx.kamada_kawai_layout(G, dim=3), scale=1, center=c)

    def test_circular_planar_and_shell_dim_error(self):
        G = nx.path_graph(4)
        pytest.raises(ValueError, nx.circular_layout, G, dim=1)
        pytest.raises(ValueError, nx.shell_layout, G, dim=1)
        pytest.raises(ValueError, nx.shell_layout, G, dim=3)
        pytest.raises(ValueError, nx.planar_layout, G, dim=1)
        pytest.raises(ValueError, nx.planar_layout, G, dim=3)

    def test_adjacency_interface_numpy(self):
        A = nx.to_numpy_array(self.Gs)
        frame_2d = (np.zeros(2), np.ones(2))
        frame_3d = (np.zeros(3), np.ones(3))
        pos_2d = np.array([np.zeros(2) for _ in range(len(self.Gs))])
        pos_3d = np.array([np.zeros(3) for _ in range(len(self.Gs))])
        k = 0.1
        pos = nx.drawing.layout._fruchterman_reingold(A, k, frame_2d, pos_2d)
        assert pos.shape == (6, 2)
        pos = nx.drawing.layout._fruchterman_reingold(A, k, frame_3d, pos_3d, dim=3)
        assert pos.shape == (6, 3)
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A)
        assert pos.shape == (6, 2)

    def test_adjacency_interface_scipy(self):
        A = nx.to_scipy_sparse_array(self.Gs, dtype="d")
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A)
        assert pos.shape == (6, 2)
        pos = nx.drawing.layout._sparse_spectral(A)
        assert pos.shape == (6, 2)
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A, dim=3)
        assert pos.shape == (6, 3)

    def test_single_nodes(self):
        G = nx.path_graph(1)
        vpos = nx.shell_layout(G)
        assert not vpos[0].any()
        G = nx.path_graph(4)
        vpos = nx.shell_layout(G, [[0], [1, 2], [3]])
        assert not vpos[0].any()
        assert vpos[3].any()  # ensure node 3 not at origin (#3188)
        assert np.linalg.norm(vpos[3]) <= 1  # ensure node 3 fits (#3753)
        vpos = nx.shell_layout(G, [[0], [1, 2], [3]], rotate=0)
        assert np.linalg.norm(vpos[3]) <= 1  # ensure node 3 fits (#3753)

    def test_smoke_initial_pos_fruchterman_reingold(self):
        pos = nx.circular_layout(self.Gi)
        npos = nx.fruchterman_reingold_layout(self.Gi, pos=pos)

    def test_smoke_initial_pos_arf(self):
        pos = nx.circular_layout(self.Gi)
        npos = nx.arf_layout(self.Gi, pos=pos)

    def test_fixed_node_fruchterman_reingold(self):
        # Dense version (numpy based)
        pos = nx.circular_layout(self.Gi)
        npos = nx.spring_layout(self.Gi, pos=pos, fixed=[(0, 0)])
        assert tuple(pos[(0, 0)]) == tuple(npos[(0, 0)])
        # Sparse version (scipy based)
        pos = nx.circular_layout(self.bigG)
        npos = nx.spring_layout(self.bigG, pos=pos, fixed=[(0, 0)])
        for axis in range(2):
            assert pos[(0, 0)][axis] == pytest.approx(npos[(0, 0)][axis], abs=1e-7)

    def test_center_parameter(self):
        G = nx.path_graph(1)
        nx.random_layout(G, center=(1, 1))
        vpos = nx.circular_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)
        vpos = nx.planar_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)
        vpos = nx.spring_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)
        vpos = nx.fruchterman_reingold_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)
        vpos = nx.spectral_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)
        vpos = nx.shell_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)
        vpos = nx.spiral_layout(G, center=(1, 1))
        assert tuple(vpos[0]) == (1, 1)

    def test_center_wrong_dimensions(self):
        G = nx.path_graph(1)
        assert id(nx.spring_layout) == id(nx.fruchterman_reingold_layout)
        pytest.raises(ValueError, nx.random_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.circular_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.planar_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.spring_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.spring_layout, G, dim=3, center=(1, 1))
        pytest.raises(ValueError, nx.spectral_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.spectral_layout, G, dim=3, center=(1, 1))
        pytest.raises(ValueError, nx.shell_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.spiral_layout, G, center=(1, 1, 1))
        pytest.raises(ValueError, nx.kamada_kawai_layout, G, center=(1, 1, 1))

    def test_empty_graph(self):
        G = nx.empty_graph()
        vpos = nx.random_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.circular_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.planar_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.bipartite_layout(G, G)
        assert vpos == {}
        vpos = nx.spring_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.fruchterman_reingold_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.spectral_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.shell_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.spiral_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.multipartite_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.kamada_kawai_layout(G, center=(1, 1))
        assert vpos == {}
        vpos = nx.arf_layout(G)
        assert vpos == {}

    def test_bipartite_layout(self):
        G = nx.complete_bipartite_graph(3, 5)
        top, bottom = nx.bipartite.sets(G)

        vpos = nx.bipartite_layout(G, top)
        assert len(vpos) == len(G)

        top_x = vpos[list(top)[0]][0]
        bottom_x = vpos[list(bottom)[0]][0]
        for node in top:
            assert vpos[node][0] == top_x
        for node in bottom:
            assert vpos[node][0] == bottom_x

        vpos = nx.bipartite_layout(
            G, top, align="horizontal", center=(2, 2), scale=2, aspect_ratio=1
        )
        assert len(vpos) == len(G)

        top_y = vpos[list(top)[0]][1]
        bottom_y = vpos[list(bottom)[0]][1]
        for node in top:
            assert vpos[node][1] == top_y
        for node in bottom:
            assert vpos[node][1] == bottom_y

        pytest.raises(ValueError, nx.bipartite_layout, G, top, align="foo")

    def test_multipartite_layout(self):
        sizes = (0, 5, 7, 2, 8)
        G = nx.complete_multipartite_graph(*sizes)

        vpos = nx.multipartite_layout(G)
        assert len(vpos) == len(G)

        start = 0
        for n in sizes:
            end = start + n
            assert all(vpos[start][0] == vpos[i][0] for i in range(start + 1, end))
            start += n

        vpos = nx.multipartite_layout(G, align="horizontal", scale=2, center=(2, 2))
        assert len(vpos) == len(G)

        start = 0
        for n in sizes:
            end = start + n
            assert all(vpos[start][1] == vpos[i][1] for i in range(start + 1, end))
            start += n

        pytest.raises(ValueError, nx.multipartite_layout, G, align="foo")

    def test_kamada_kawai_costfn_1d(self):
        costfn = nx.drawing.layout._kamada_kawai_costfn

        pos = np.array([4.0, 7.0])
        invdist = 1 / np.array([[0.1, 2.0], [2.0, 0.3]])

        cost, grad = costfn(pos, np, invdist, meanweight=0, dim=1)

        assert cost == pytest.approx(((3 / 2.0 - 1) ** 2), abs=1e-7)
        assert grad[0] == pytest.approx((-0.5), abs=1e-7)
        assert grad[1] == pytest.approx(0.5, abs=1e-7)

    def check_kamada_kawai_costfn(self, pos, invdist, meanwt, dim):
        costfn = nx.drawing.layout._kamada_kawai_costfn

        cost, grad = costfn(pos.ravel(), np, invdist, meanweight=meanwt, dim=dim)

        expected_cost = 0.5 * meanwt * np.sum(np.sum(pos, axis=0) ** 2)
        for i in range(pos.shape[0]):
            for j in range(i + 1, pos.shape[0]):
                diff = np.linalg.norm(pos[i] - pos[j])
                expected_cost += (diff * invdist[i][j] - 1.0) ** 2

        assert cost == pytest.approx(expected_cost, abs=1e-7)

        dx = 1e-4
        for nd in range(pos.shape[0]):
            for dm in range(pos.shape[1]):
                idx = nd * pos.shape[1] + dm
                ps = pos.flatten()

                ps[idx] += dx
                cplus = costfn(ps, np, invdist, meanweight=meanwt, dim=pos.shape[1])[0]

                ps[idx] -= 2 * dx
                cminus = costfn(ps, np, invdist, meanweight=meanwt, dim=pos.shape[1])[0]

                assert grad[idx] == pytest.approx((cplus - cminus) / (2 * dx), abs=1e-5)

    def test_kamada_kawai_costfn(self):
        invdist = 1 / np.array([[0.1, 2.1, 1.7], [2.1, 0.2, 0.6], [1.7, 0.6, 0.3]])
        meanwt = 0.3

        # 2d
        pos = np.array([[1.3, -3.2], [2.7, -0.3], [5.1, 2.5]])

        self.check_kamada_kawai_costfn(pos, invdist, meanwt, 2)

        # 3d
        pos = np.array([[0.9, 8.6, -8.7], [-10, -0.5, -7.1], [9.1, -8.1, 1.6]])

        self.check_kamada_kawai_costfn(pos, invdist, meanwt, 3)

    def test_spiral_layout(self):

        G = self.Gs

        # a lower value of resolution should result in a more compact layout
        # intuitively, the total distance from the start and end nodes
        # via each node in between (transiting through each) will be less,
        # assuming rescaling does not occur on the computed node positions
        pos_standard = np.array(list(nx.spiral_layout(G, resolution=0.35).values()))
        pos_tighter = np.array(list(nx.spiral_layout(G, resolution=0.34).values()))
        distances = np.linalg.norm(pos_standard[:-1] - pos_standard[1:], axis=1)
        distances_tighter = np.linalg.norm(pos_tighter[:-1] - pos_tighter[1:], axis=1)
        assert sum(distances) > sum(distances_tighter)

        # return near-equidistant points after the first value if set to true
        pos_equidistant = np.array(list(nx.spiral_layout(G, equidistant=True).values()))
        distances_equidistant = np.linalg.norm(
            pos_equidistant[:-1] - pos_equidistant[1:], axis=1
        )
        assert np.allclose(
            distances_equidistant[1:], distances_equidistant[-1], atol=0.01
        )

    def test_spiral_layout_equidistant(self):
        G = nx.path_graph(10)
        pos = nx.spiral_layout(G, equidistant=True)
        # Extract individual node positions as an array
        p = np.array(list(pos.values()))
        # Elementwise-distance between node positions
        dist = np.linalg.norm(p[1:] - p[:-1], axis=1)
        assert np.allclose(np.diff(dist), 0, atol=1e-3)

    def test_rescale_layout_dict(self):
        G = nx.empty_graph()
        vpos = nx.random_layout(G, center=(1, 1))
        assert nx.rescale_layout_dict(vpos) == {}

        G = nx.empty_graph(2)
        vpos = {0: (0.0, 0.0), 1: (1.0, 1.0)}
        s_vpos = nx.rescale_layout_dict(vpos)
        assert np.linalg.norm([sum(x) for x in zip(*s_vpos.values())]) < 1e-6

        G = nx.empty_graph(3)
        vpos = {0: (0, 0), 1: (1, 1), 2: (0.5, 0.5)}
        s_vpos = nx.rescale_layout_dict(vpos)

        expectation = {
            0: np.array((-1, -1)),
            1: np.array((1, 1)),
            2: np.array((0, 0)),
        }
        for k, v in expectation.items():
            assert (s_vpos[k] == v).all()
        s_vpos = nx.rescale_layout_dict(vpos, scale=2)
        expectation = {
            0: np.array((-2, -2)),
            1: np.array((2, 2)),
            2: np.array((0, 0)),
        }
        for k, v in expectation.items():
            assert (s_vpos[k] == v).all()

    def test_arf_layout_partial_input_test(self):
        """
        Checks whether partial pos input still returns a proper position.
        """
        G = self.Gs
        node = nx.utils.arbitrary_element(G)
        pos = nx.circular_layout(G)
        del pos[node]
        pos = nx.arf_layout(G, pos=pos)
        assert len(pos) == len(G)

    def test_arf_layout_negative_a_check(self):
        """
        Checks input parameters correctly raises errors. For example,  `a` should be larger than 1
        """
        G = self.Gs
        pytest.raises(ValueError, nx.arf_layout, G=G, a=-1)


def test_multipartite_layout_nonnumeric_partition_labels():
    """See gh-5123."""
    G = nx.Graph()
    G.add_node(0, subset="s0")
    G.add_node(1, subset="s0")
    G.add_node(2, subset="s1")
    G.add_node(3, subset="s1")
    G.add_edges_from([(0, 2), (0, 3), (1, 2)])
    pos = nx.multipartite_layout(G)
    assert len(pos) == len(G)


def test_multipartite_layout_layer_order():
    """Return the layers in sorted order if the layers of the multipartite
    graph are sortable. See gh-5691"""
    G = nx.Graph()
    for node, layer in zip(("a", "b", "c", "d", "e"), (2, 3, 1, 2, 4)):
        G.add_node(node, subset=layer)

    # Horizontal alignment, therefore y-coord determines layers
    pos = nx.multipartite_layout(G, align="horizontal")

    # Nodes "a" and "d" are in the same layer
    assert pos["a"][-1] == pos["d"][-1]
    # positions should be sorted according to layer
    assert pos["c"][-1] < pos["a"][-1] < pos["b"][-1] < pos["e"][-1]

    # Make sure that multipartite_layout still works when layers are not sortable
    G.nodes["a"]["subset"] = "layer_0"  # Can't sort mixed strs/ints
    pos_nosort = nx.multipartite_layout(G)  # smoke test: this should not raise
    assert pos_nosort.keys() == pos.keys()


def test_get_fr_repulsion():

    from networkx.drawing.layout import _get_fr_repulsion

    k = 0.2

    distance = np.array([[0, 1], [1, 0]])
    distance = np.array([[0.0, 0.3], [0.3, 0.0]])
    direction = np.array(
        [
            [[np.nan, np.nan], [-0.8944271909999159, -0.4472135954999579]],
            [[0.8944271909999159, 0.4472135954999579], [np.nan, np.nan]],
        ]
    )
    repulsion = _get_fr_repulsion(k, distance, direction)

    expected = np.array(
        [
            [-0.11925695879998881, -0.059628479399994404],
            [0.11925695879998881, 0.059628479399994404],
        ]
    )

    assert np.allclose(expected, repulsion)


def test_get_fr_attraction():

    from networkx.drawing.layout import _get_fr_attraction

    k = 0.2

    A = np.array([[0, 1], [1, 0]])
    distance = np.array([[0.0, 0.3], [0.3, 0.0]])
    direction = np.array(
        [
            [[np.nan, np.nan], [-0.8944271909999159, -0.4472135954999579]],
            [[0.8944271909999159, 0.4472135954999579], [np.nan, np.nan]],
        ]
    )
    attraction = _get_fr_attraction(k, distance, direction, A)

    expected = np.array(
        [
            [0.4024922359499621, 0.20124611797498104],
            [-0.4024922359499621, -0.20124611797498104],
        ]
    )

    assert np.allclose(expected, attraction)


def test_initialize_frame_no_inputs():

    from numpy.testing import assert_almost_equal

    from networkx.drawing.layout import _initialize_frame

    # 2D
    origin, dom_size = _initialize_frame(None, None, 2)
    assert_almost_equal(origin, np.zeros(2))
    assert_almost_equal(dom_size, np.ones(2))

    # 3D
    origin, dom_size = _initialize_frame(None, None, 3)
    assert_almost_equal(origin, np.zeros(3))
    assert_almost_equal(dom_size, np.ones(3))


def test_initialize_frame_frame_given():

    from numpy.testing import assert_almost_equal

    from networkx.drawing.layout import _initialize_frame

    frame = (np.array([-1.0, -2.0]), np.array([4, 3]))

    # no position
    origin, dom_size = _initialize_frame(None, frame, 2)
    assert_almost_equal(origin, frame[0])
    assert_almost_equal(dom_size, frame[1])

    # all positions inside
    pos_inside = {
        0: (0.0, 0.0),
        1: (-0.5, 1),
        2: (2.0, 0.75),
        3: (3.0, 0.0),
    }

    origin, dom_size = _initialize_frame(pos_inside, frame, 2)
    assert_almost_equal(origin, frame[0])
    assert_almost_equal(dom_size, frame[1])

    # one position outside
    pos_outside = pos_inside
    pos_outside[4] = (-2.0, 3.0)

    with pytest.raises(ValueError):
        origin, dom_size = _initialize_frame(pos_outside, frame, 2)


def test_initialize_frame_pos_given():

    from numpy.testing import assert_almost_equal

    from networkx.drawing.layout import _initialize_frame

    pos = {0: (-1.0, -1.0), 1: (1.0, 1)}

    expected_origin = np.array((-2.0, -2.0))
    expected_dom_size = np.array((4.0, 4.0))

    origin, dom_size = _initialize_frame(pos, None, 2)
    assert_almost_equal(origin, expected_origin)
    assert_almost_equal(dom_size, expected_dom_size)


def test_initialize_frame_single_pos_given():

    from numpy.testing import assert_almost_equal

    from networkx.drawing.layout import _initialize_frame

    expected_dom_size = np.array((1.0, 1.0))

    pos = {0: (0.0, 0.0)}

    expected_origin = np.array((-0.5, -0.5))

    origin, dom_size = _initialize_frame(pos, None, 2)
    assert_almost_equal(origin, expected_origin)
    assert_almost_equal(dom_size, expected_dom_size)

    pos = {0: (0.5, -0.5)}
    expected_origin = np.array((0.0, -1.0))

    origin, dom_size = _initialize_frame(pos, None, 2)
    assert_almost_equal(origin, expected_origin)
    assert_almost_equal(dom_size, expected_dom_size)
