import pytest

import networkx as nx


class TestPowerCentrality:
    @classmethod
    def setup_class(cls):
        global np
        np = pytest.importorskip("numpy")
        pytest.importorskip("scipy")

    def test_K5(self):
        G = nx.complete_graph(5)
        b = nx.power_centrality(G)
        for n in sorted(G):
            assert b[n] == pytest.approx(1, abs=1e-7)

    def test_P3(self):
        G = nx.path_graph(3)
        b = nx.power_centrality(G)
        b_answer = {0: 0.7480544714310444, 1: 1.3714331976235816, 2: 0.7480544714310444}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_S3(self):
        G = nx.star_graph(3)
        b = nx.power_centrality(G)
        b_answer = {
            0: 1.6520663752618043,
            1: 0.6508140266182866,
            2: 0.6508140266182866,
            3: 0.6508140266182866,
        }
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_directed_P3(self):
        G = nx.path_graph(3, nx.DiGraph)
        b = nx.power_centrality(G)
        b_answer = {0: 1.2816138016780187, 1: 1.1651034560709261, 2: 0.0}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_directed_S3(self):
        G = nx.DiGraph([(0, 1), (0, 2), (0, 3)])
        b = nx.power_centrality(G)
        b_answer = {0: 2, 1: 0, 2: 0, 3: 0}
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_directed_C3(self):
        G = nx.cycle_graph(3, nx.DiGraph)
        b = nx.power_centrality(G)
        for n in sorted(G):
            assert b[n] == pytest.approx(1, abs=1e-7)

    def test_weighted(self):
        edges = [
            (0, 1, {"weight": 24}),
            (0, 2, {"weight": 24}),
            (0, 3, {"weight": 24}),
            (1, 2, {"weight": 24}),
            (1, 3, {"weight": 20}),
            (2, 3, {"weight": 20}),
        ]
        G = nx.Graph(edges)
        b = nx.power_centrality(G, beta=0.01, weight="weight")
        b_answer = {
            0: 1.0460403421078126,
            1: 1.0002278950842434,
            2: 1.0002278950842434,
            3: 0.9512559689556005,
        }
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_normalized(self):
        G = nx.complete_graph(5)
        b = nx.power_centrality(G, normalized=True)
        assert pytest.approx(sum(b.values()), abs=1e-7) == 1

    def test_cook_1c(self):
        """Fig. 2 network 1c in Bonacich (1987). Results identical to Tab. 3"""
        G = nx.Graph([(0, 1), (0, 2), (1, 3), (2, 4)])
        b_answers = {
            -0.3: {
                0: 0.9730085108210397,
                1: 1.3378867023789296,
                2: 1.3378867023789296,
                3: 0.48650425541051995,
                4: 0.48650425541051995,
            },
            -0.2: {
                0: 1.0882143751650173,
                1: 1.2695834376925206,
                2: 1.2695834376925204,
                3: 0.5441071875825086,
                4: 0.5441071875825086,
            },
            -0.1: {
                0: 1.1534996014569447,
                1: 1.225593326548004,
                2: 1.2255933265480041,
                3: 0.5767498007284724,
                4: 0.5767498007284724,
            },
            0: {
                0: 1.1952286093343936,
                1: 1.1952286093343936,
                2: 1.1952286093343936,
                3: 0.5976143046671968,
                4: 0.5976143046671968,
            },
            0.1: {
                0: 1.2241074813555017,
                1: 1.173103002965689,
                2: 1.173103002965689,
                3: 0.6120537406777509,
                4: 0.6120537406777509,
            },
            0.2: {
                0: 1.245244117188435,
                1: 1.1562981088178326,
                2: 1.1562981088178326,
                3: 0.6226220585942176,
                4: 0.6226220585942176,
            },
            0.3: {
                0: 1.2613684401582361,
                1: 1.1431151488934015,
                2: 1.1431151488934015,
                3: 0.630684220079118,
                4: 0.6306842200791181,
            },
        }
        for beta, b_answer in b_answers.items():
            b = nx.power_centrality(G, beta=beta)
            for n in sorted(G):
                assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_cook_1d(self):
        """Fig. 2 network 1d in Bonacich (1987). Results identical to Tab. 3"""
        G = nx.Graph([(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6)])
        b_answer = {
            0: 1.6201851746019653,
            1: 1.0801234497346432,
            2: 1.0801234497346432,
            3: 1.0801234497346432,
            4: 0.5400617248673216,
            5: 0.5400617248673216,
            6: 0.5400617248673216,
        }
        for beta in [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]:
            b = nx.power_centrality(G, beta=beta)
            for n in sorted(G):
                assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_cook_1d_directed(self):
        """Fig. 2 network 1d in Bonacich (1987). Results identical to Tab. 4"""
        G = nx.DiGraph(
            [(0, 1), (0, 2), (0, 3), (1, 0), (2, 0), (3, 0), (1, 4), (2, 5), (3, 6)]
        )
        b_answers = {
            -0.3: {
                0: 1.410023290755643,
                1: 1.2925213498593398,
                2: 1.2925213498593398,
                3: 1.2925213498593395,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
            -0.2: {
                0: 1.5769724491135402,
                1: 1.2265341270883094,
                2: 1.2265341270883092,
                3: 1.2265341270883092,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
            -0.1: {
                0: 1.671579730129196,
                1: 1.1840356421748466,
                2: 1.1840356421748468,
                3: 1.1840356421748466,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
            0: {
                0: 1.7320508075688772,
                1: 1.1547005383792515,
                2: 1.1547005383792515,
                3: 1.1547005383792515,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
            0.1: {
                0: 1.773900269015164,
                1: 1.133325171870799,
                2: 1.1333251718707993,
                3: 1.133325171870799,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
            0.2: {
                0: 1.8045301643153684,
                1: 1.1170901017190376,
                2: 1.1170901017190376,
                3: 1.1170901017190376,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
            0.3: {
                0: 1.8278965282086308,
                1: 1.104354152459381,
                2: 1.104354152459381,
                3: 1.104354152459381,
                4: 0.0,
                5: 0.0,
                6: 0.0,
            },
        }
        for beta, b_answer in b_answers.items():
            b = nx.power_centrality(G, beta=beta)
            for n in sorted(G):
                assert b[n] == pytest.approx(b_answer[n], abs=1e-7)

    def test_multigraph(self):
        with pytest.raises(nx.NetworkXException):
            nx.power_centrality(nx.MultiGraph())

    def test_empty(self):
        e = nx.power_centrality(nx.Graph())
        assert e == {}

    def test_singular_matrix(self):
        with pytest.raises(np.linalg.LinAlgError):
            edges = [
                (0, 1, {"weight": -1}),
                (0, 2, {"weight": -1}),
                (0, 0, {"weight": 1}),
                (1, 1, {"weight": 1}),
                (2, 2, {"weight": 1}),
            ]
            nx.power_centrality(nx.Graph(edges), beta=1, weight="weight")
