"""Unit tests for layout functions."""
import networkx as nx
from networkx.testing import almost_equal

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestLayout:
    @classmethod
    def setup_class(cls):
        cls.Gi = nx.grid_2d_graph(5, 5)
        cls.Gs = nx.Graph()
        nx.add_path(cls.Gs, "abcdef")
        cls.DGs = nx.DiGraph()
        nx.add_path(cls.DGs, "abcdef")
        cls.bigG = nx.grid_2d_graph(25, 25)  # > 500 nodes for sparse

    @staticmethod
    def collect_node_distances(positions):
        distances = []
        prev_val = None
        for k in positions:
            if prev_val is not None:
                diff = positions[k] - prev_val
                distances.append((diff @ diff) ** 0.5)
            prev_val = positions[k]
        return distances

    @staticmethod
    def deep_compare_pos(p1, p2):
        if p1.keys() != p2.keys():
            return False
        for k in p1.keys():
            if not np.allclose(p1[k], p2[k]):
                return False
        return True

    def test_deep_compare_pos(self):
        assert not self.deep_compare_pos(  # wrong keys
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
            {"a": np.array([-0.5, 1.0]), "c": np.array([-0.5, -0.5])},
        )
        assert not self.deep_compare_pos(  # wrong values
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
            {"a": np.array([-0.5, -5]), "b": np.array([-0.5, -0.5])},
        )
        assert not self.deep_compare_pos(  # wrong values
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.0])},
        )
        assert not self.deep_compare_pos(  # wrong values without ndarray
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
            {"a": [-0.5, -5], "b": np.array([-0.5, -0.5])},
        )
        assert self.deep_compare_pos(  # good
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
        )
        assert self.deep_compare_pos(  # also good without ndarray
            {"a": np.array([-0.5, 1.0]), "b": np.array([-0.5, -0.5])},
            {"a": [-0.5, 1.0], "b": [-0.5, -0.5]},
        )

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
        # layered_layout only supports DiGraph objects, not lists of nodes

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
        # layered_layout only supports directed acyclic graphs

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
        pytest.raises(nx.NetworkXNotImplemented, nx.layered_layout, G)
        # DiGraph
        G = self.DGs
        nx.layered_layout(G)

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
        # layered_layout only supports directed acyclic graphs

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
        # layered_layout only supports directed acyclic graphs

    def test_circular_planar_and_shell_dim_error(self):
        G = nx.path_graph(4)
        pytest.raises(ValueError, nx.circular_layout, G, dim=1)
        pytest.raises(ValueError, nx.shell_layout, G, dim=1)
        pytest.raises(ValueError, nx.shell_layout, G, dim=3)
        pytest.raises(ValueError, nx.planar_layout, G, dim=1)
        pytest.raises(ValueError, nx.planar_layout, G, dim=3)

    def test_adjacency_interface_numpy(self):
        A = nx.to_numpy_array(self.Gs)
        pos = nx.drawing.layout._fruchterman_reingold(A)
        assert pos.shape == (6, 2)
        pos = nx.drawing.layout._fruchterman_reingold(A, dim=3)
        assert pos.shape == (6, 3)
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A)
        assert pos.shape == (6, 2)

    def test_adjacency_interface_scipy(self):
        A = nx.to_scipy_sparse_matrix(self.Gs, dtype="d")
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A)
        assert pos.shape == (6, 2)
        pos = nx.drawing.layout._sparse_spectral(A)
        assert pos.shape == (6, 2)
        pos = nx.drawing.layout._sparse_fruchterman_reingold(A, dim=3)
        assert pos.shape == (6, 3)

    def test_shell_layout_single_nodes(self):
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

    def test_fixed_node_fruchterman_reingold(self):
        # Dense version (numpy based)
        pos = nx.circular_layout(self.Gi)
        npos = nx.spring_layout(self.Gi, pos=pos, fixed=[(0, 0)])
        assert tuple(pos[(0, 0)]) == tuple(npos[(0, 0)])
        # Sparse version (scipy based)
        pos = nx.circular_layout(self.bigG)
        npos = nx.spring_layout(self.bigG, pos=pos, fixed=[(0, 0)])
        for axis in range(2):
            assert almost_equal(pos[(0, 0)][axis], npos[(0, 0)][axis])

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
        # Layered layout is only implemented for DiGraphs
        G = nx.path_graph(1, create_using=nx.DiGraph)
        vpos, _ = nx.layered_layout(G, center=(1, 1))
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
        G = nx.path_graph(1, create_using=nx.DiGraph)
        pytest.raises(ValueError, nx.layered_layout, G, center=(1, 1, 1))

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
        # Layered layout is only implemented for DiGraphs
        G = nx.empty_graph(create_using=nx.DiGraph)
        vpos, edges_path = nx.layered_layout(G, center=(1, 1))
        assert vpos == {}
        assert edges_path == {}

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

        assert almost_equal(cost, ((3 / 2.0 - 1) ** 2))
        assert almost_equal(grad[0], -0.5)
        assert almost_equal(grad[1], 0.5)

    def check_kamada_kawai_costfn(self, pos, invdist, meanwt, dim):
        costfn = nx.drawing.layout._kamada_kawai_costfn

        cost, grad = costfn(pos.ravel(), np, invdist, meanweight=meanwt, dim=dim)

        expected_cost = 0.5 * meanwt * np.sum(np.sum(pos, axis=0) ** 2)
        for i in range(pos.shape[0]):
            for j in range(i + 1, pos.shape[0]):
                diff = np.linalg.norm(pos[i] - pos[j])
                expected_cost += (diff * invdist[i][j] - 1.0) ** 2

        assert almost_equal(cost, expected_cost)

        dx = 1e-4
        for nd in range(pos.shape[0]):
            for dm in range(pos.shape[1]):
                idx = nd * pos.shape[1] + dm
                ps = pos.flatten()

                ps[idx] += dx
                cplus = costfn(ps, np, invdist, meanweight=meanwt, dim=pos.shape[1])[0]

                ps[idx] -= 2 * dx
                cminus = costfn(ps, np, invdist, meanweight=meanwt, dim=pos.shape[1])[0]

                assert almost_equal(grad[idx], (cplus - cminus) / (2 * dx), places=5)

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
        pos_standard = nx.spiral_layout(G, resolution=0.35)
        pos_tighter = nx.spiral_layout(G, resolution=0.34)
        distances = self.collect_node_distances(pos_standard)
        distances_tighter = self.collect_node_distances(pos_tighter)
        assert sum(distances) > sum(distances_tighter)

        # return near-equidistant points after the first value if set to true
        pos_equidistant = nx.spiral_layout(G, equidistant=True)
        distances_equidistant = self.collect_node_distances(pos_equidistant)
        for d in range(1, len(distances_equidistant) - 1):
            # test similarity to two decimal places
            assert almost_equal(
                distances_equidistant[d], distances_equidistant[d + 1], 2
            )

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
        assert s_vpos == {0: (-1, -1), 1: (1, 1), 2: (0, 0)}
        s_vpos = nx.rescale_layout_dict(vpos, scale=2)
        assert s_vpos == {0: (-2, -2), 1: (2, 2), 2: (0, 0)}

    def test_layered_layout(self):
        test_cases = {
            "single edge": {
                "edges": [(1, 2)],
                "align": "vertical",
                "pos": {1: [0.0, 1.0], 2: [0.0, -1.0]},
                "edges_path": {},
            },
            "stump": {
                "edges": [(1, 2), (1, 3)],
                "align": "vertical",
                "pos": {1: [-0.5, 1.0], 3: [-0.5, -0.5], 2: [1.0, -0.5]},
                "edges_path": {},
            },
            "long edge": {
                "edges": [(1, 2), (2, 3), (1, 3)],
                "align": "vertical",
                "pos": {1: [-0.25, 1.0], 2: [-0.25, 0.0], 3: [-0.25, -1.0]},
                "edges_path": {(1, 3): [[0.75, 0.0]]},
            },
            "two long edges": {
                "edges": [(1, 2), (2, 3), (1, 3), (1, 4), (2, 4)],
                "align": "vertical",
                "pos": {
                    1: [0.0, 1.0],
                    2: [0.0, 0.14285714],
                    3: [-0.85714286, -0.71428571],
                    4: [0.85714286, -0.71428571],
                },
                "edges_path": {
                    (1, 3): [[-0.85714286, 0.14285714]],
                    (1, 4): [[0.85714286, 0.14285714]],
                },
            },
            "30-nodes growing network graph": {
                "edges": [
                    (1, 0),
                    (2, 0),
                    (3, 2),
                    (4, 0),
                    (5, 0),
                    (6, 0),
                    (7, 1),
                    (8, 1),
                    (9, 0),
                    (10, 1),
                    (11, 1),
                    (12, 2),
                    (13, 2),
                    (14, 0),
                    (15, 0),
                    (16, 1),
                    (17, 1),
                    (18, 2),
                    (19, 17),
                    (20, 1),
                    (21, 2),
                    (22, 1),
                    (23, 0),
                    (24, 1),
                    (25, 0),
                    (26, 0),
                    (27, 19),
                    (28, 1),
                    (29, 28),
                ],
                "align": "vertical",
                "pos": {
                    26: [-0.93791574, 0.1075388],
                    25: [-0.85365854, 0.1075388],
                    23: [-0.76940133, 0.1075388],
                    29: [-0.68514412, 0.1075388],
                    27: [-0.60088692, 0.1075388],
                    24: [-0.51662971, 0.1075388],
                    22: [-0.43237251, 0.1075388],
                    20: [-0.3481153, 0.1075388],
                    16: [-0.26385809, 0.1075388],
                    11: [-0.17960089, 0.1075388],
                    10: [-0.09534368, 0.1075388],
                    8: [-0.01108647, 0.1075388],
                    7: [0.07317073, 0.1075388],
                    15: [0.15742794, 0.1075388],
                    14: [0.24168514, 0.1075388],
                    21: [0.32594235, 0.1075388],
                    18: [0.41019956, 0.1075388],
                    13: [0.49445676, 0.1075388],
                    12: [0.57871397, 0.1075388],
                    3: [0.66297118, 0.1075388],
                    9: [0.74722838, 0.1075388],
                    6: [0.83148559, 0.1075388],
                    5: [0.91574279, 0.1075388],
                    4: [1.0, 0.1075388],
                    28: [-0.68514412, 0.0232816],
                    19: [-0.60088692, 0.0232816],
                    2: [0.49445676, 0.0232816],
                    17: [-0.60088692, -0.06097561],
                    1: [-0.26385809, -0.14523282],
                    0: [0.15742794, -0.22949002],
                },
                "edges_path": {
                    (2, 0): [[0.49445676, -0.06097561], [0.49445676, -0.14523282]],
                    (4, 0): [[1.0, 0.0232816], [1.0, -0.06097561], [1.0, -0.14523282]],
                    (5, 0): [
                        [0.91574279, 0.0232816],
                        [0.91574279, -0.06097561],
                        [0.91574279, -0.14523282],
                    ],
                    (6, 0): [
                        [0.83148559, 0.0232816],
                        [0.83148559, -0.06097561],
                        [0.83148559, -0.14523282],
                    ],
                    (7, 1): [[0.07317073, 0.0232816], [0.07317073, -0.06097561]],
                    (8, 1): [[-0.01108647, 0.0232816], [-0.01108647, -0.06097561]],
                    (9, 0): [
                        [0.74722838, 0.0232816],
                        [0.74722838, -0.06097561],
                        [0.74722838, -0.14523282],
                    ],
                    (10, 1): [[-0.09534368, 0.0232816], [-0.09534368, -0.06097561]],
                    (11, 1): [[-0.17960089, 0.0232816], [-0.17960089, -0.06097561]],
                    (14, 0): [
                        [0.24168514, 0.0232816],
                        [0.24168514, -0.06097561],
                        [0.24168514, -0.14523282],
                    ],
                    (15, 0): [
                        [0.15742794, 0.0232816],
                        [0.15742794, -0.06097561],
                        [0.15742794, -0.14523282],
                    ],
                    (16, 1): [[-0.26385809, 0.0232816], [-0.26385809, -0.06097561]],
                    (20, 1): [[-0.3481153, 0.0232816], [-0.3481153, -0.06097561]],
                    (22, 1): [[-0.43237251, 0.0232816], [-0.43237251, -0.06097561]],
                    (23, 0): [
                        [-0.76940133, 0.0232816],
                        [-0.76940133, -0.06097561],
                        [-0.76940133, -0.14523282],
                    ],
                    (24, 1): [[-0.51662971, 0.0232816], [-0.51662971, -0.06097561]],
                    (25, 0): [
                        [-0.85365854, 0.0232816],
                        [-0.85365854, -0.06097561],
                        [-0.85365854, -0.14523282],
                    ],
                    (26, 0): [
                        [-0.93791574, 0.0232816],
                        [-0.93791574, -0.06097561],
                        [-0.93791574, -0.14523282],
                    ],
                    (28, 1): [[-0.68514412, -0.06097561]],
                },
            },
        }

        for test_case_name, test_case in test_cases.items():
            G = nx.DiGraph()
            G.add_edges_from(test_case["edges"])
            pos, edges_path = nx.layered_layout(G, align=test_case["align"])
            if not self.deep_compare_pos(
                pos, test_case["pos"]
            ) or not self.deep_compare_pos(edges_path, test_case["edges_path"]):
                raise ValueError(f"{test_case_name} was not displayed as expected")
