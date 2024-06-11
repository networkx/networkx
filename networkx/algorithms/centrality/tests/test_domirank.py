from contextlib import nullcontext as does_not_raise

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestDomirank:
    def test_K5(self):
        """DomiRank centrality: K5"""
        G = nx.complete_graph(5)
        b, _, converged = nx.domirank(G)
        assert converged
        b_answer = {
            0: 0.7916655540466309,
            1: 0.7916655540466309,
            2: 0.7916655540466309,
            3: 0.7916655540466309,
            4: 0.7916655540466308,
        }
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)
        b, _, converged = nx.domirank(G, method="analytical")
        assert converged is None
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)
        b_answer = {
            0: 0.7916661947954937,
            1: 0.7916661947954933,
            2: 0.7916661947954919,
            3: 0.791666194795491,
            4: 0.7916661947954975,
        }
        b, _, converged = nx.domirank(G, alpha=0.5)
        assert converged
        b_answer = {
            0: 0.66666579246521,
            1: 0.66666579246521,
            2: 0.66666579246521,
            3: 0.66666579246521,
            4: 0.66666579246521,
        }
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

    def test_P3(self):
        """DomiRank centrality: P3"""
        G = nx.path_graph(3)
        b, _, converged = nx.domirank(G)
        assert converged
        b_answer = {
            0: -2.3477606773376465,
            1: 4.496389865875244,
            2: -2.3477606773376465,
        }
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

        b_answer = {0: -2.366595958759845, 1: 4.523026818398872, 2: -2.366595958759845}
        b, _, converged = nx.domirank(G, method="analytical")
        assert converged is None
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

        b_answer = {
            0: 0.13808214664459229,
            1: 0.609459638595581,
            2: 0.13808214664459229,
        }
        b, _, converged = nx.domirank(G, alpha=0.5)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

    def test_P3_dt(self):
        """DomiRank centrality: P3"""
        G = nx.path_graph(3)
        b_answer = {
            0: -2.3666865825653076,
            1: 4.523157596588135,
            2: -2.3666865825653076,
        }
        b, _, converged = nx.domirank(G, dt=0.5)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

    def test_P3_eps(self):
        """DomiRank centrality: P3"""
        G = nx.path_graph(3)
        b_answer = {
            0: -2.3477983474731445,
            1: 4.496443748474121,
            2: -2.3477983474731445,
        }
        b, _, converged = nx.domirank(G, epsilon=1e-7)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

    def test_P3_max_iter(self):
        """DomiRank centrality: P3"""
        G = nx.path_graph(3)
        b_answer = {0: -2.364804744720459, 1: 4.5204758644104, 2: -2.364804744720459}
        b, _, converged = nx.domirank(G, max_iter=5000)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)

    def test_P3_patience(self):
        """DomiRank centrality: P3"""
        G = nx.path_graph(3)
        b_answer = {0: -2.3474247455596924, 1: 4.49591064453125, 2: -2.3474247455596924}
        b, _, converged = nx.domirank(G, patience=5)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3)


class TestDomirankDirected:
    @classmethod
    def setup_class(cls):
        G = nx.DiGraph()

        edges = [
            (1, 2),
            (1, 3),
            (2, 4),
            (3, 2),
            (3, 5),
            (4, 2),
            (4, 5),
            (4, 6),
            (5, 6),
            (5, 7),
            (5, 8),
            (6, 8),
            (7, 1),
            (7, 5),
            (7, 8),
            (8, 6),
            (8, 7),
        ]

        G.add_edges_from(edges)
        cls.G = G.reverse()
        cls.drc = {
            1: 0.8088147044181824,
            2: 1.3506824970245361,
            3: 0.11302878707647324,
            4: -0.20726482570171356,
            5: 2.0464682579040527,
            6: 0.3447999954223633,
            7: -0.36868923902511597,
            8: 0.5775589942932129,
        }

        cls.drca = {
            1: 0.8100015022345155,
            2: 1.3502259832012713,
            3: 0.11228691263288304,
            4: -0.20697950162756873,
            5: 2.0479405728029034,
            6: 0.3427231477861121,
            7: -0.3705877648939345,
            8: 0.5791237659444093,
        }

    def test_domirank_centrality_directed(self):
        G = self.G
        b, _, converged = nx.domirank(G)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(self.drc[n], abs=5e-3)

    def test_domirank_centrality_directed_analytical(self):
        G = self.G
        b, _, converged = nx.domirank(G, method="analytical")
        assert converged is None
        for n in sorted(G):
            assert b[n] == pytest.approx(self.drca[n], abs=5e-3)


class TestDomirankGraphExceptions:
    @pytest.mark.parametrize(
        (
            "G",
            "expectation",
        ),
        [
            (
                nx.barabasi_albert_graph(25, 1),
                does_not_raise(),
            ),
            (
                nx.path_graph(10),
                does_not_raise(),
            ),
            (
                nx.Graph(),
                pytest.raises(nx.NetworkXPointlessConcept),
            ),
            (
                nx.MultiGraph(),
                pytest.raises(nx.NetworkXNotImplemented),
            ),
        ],
    )
    def test_domirank_exceptions(self, G, expectation):
        with expectation:
            nx.domirank(
                G,
            )


class TestDomirankMethodExceptions:
    @pytest.mark.parametrize(
        (
            "method",
            "expectation",
        ),
        [
            (
                "analytical",
                does_not_raise(),
            ),
            (
                "iterative",
                does_not_raise(),
            ),
            (
                "ThisShouldNotWork",
                pytest.raises(nx.NetworkXUnfeasible),
            ),
        ],
    )
    def test_domirank_exceptions(self, method, expectation):
        with expectation:
            nx.domirank(
                nx.path_graph(10),
                method=method,
            )


class TestDomirankAlphaExceptions:
    @pytest.mark.parametrize(
        (
            "method",
            "alpha",
            "expectation",
        ),
        [
            (
                "analytical",
                2,
                does_not_raise(),
            ),
            (
                "iterative",
                -1,
                pytest.raises(nx.NetworkXUnfeasible),
            ),
            (
                "iterative",
                2,
                pytest.raises(nx.NetworkXUnfeasible),
            ),
            (
                "analytical",
                -1,
                pytest.raises(nx.NetworkXUnfeasible),
            ),
        ],
    )
    def test_domirank_exceptions(self, method, alpha, expectation):
        with expectation:
            nx.domirank(
                nx.path_graph(10),
                alpha=alpha,
                method=method,
            )


class TestDomirankIterExceptions:
    @pytest.mark.parametrize(
        (
            "max_iter",
            "patience",
            "max_depth",
            "expectation",
        ),
        [
            (
                1000,
                10,
                50,
                does_not_raise(),
            ),
            (
                1000,
                10000,
                25,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
            (
                1000,
                0,
                0,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
            (
                1000,
                0,
                25,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
            (
                3,
                1,
                -1,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
        ],
    )
    def test_domirank_exceptions(self, max_iter, patience, max_depth, expectation):
        with expectation:
            nx.domirank(
                nx.path_graph(10),
                max_iter=max_iter,
                patience=patience,
                max_depth=max_depth,
            )


class TestDomirankConvergeParamsExceptions:
    @pytest.mark.parametrize(
        (
            "dt",
            "epsilon",
            "expectation",
        ),
        [
            (
                0.1,
                1e-5,
                does_not_raise(),
            ),
            (
                1.1,
                1e-5,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
            (
                -0.1,
                1e-5,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
            (
                0.1,
                -1,
                pytest.raises(nx.NetworkXAlgorithmError),
            ),
        ],
    )
    def test_domirank_exceptions(self, dt, epsilon, expectation):
        with expectation:
            nx.domirank(
                nx.path_graph(10),
                dt=dt,
                epsilon=epsilon,
            )
