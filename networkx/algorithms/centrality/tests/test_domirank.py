from contextlib import nullcontext as does_not_raise

import pytest

import networkx as nx

pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestDomirank:
    def test_K5(self):
        """DomiRank centrality: K5"""
        G = nx.complete_graph(5)
        i, _, iterative_converged = nx.domirank(G, method="iterative")
        a, _, analytical_converged = nx.domirank(G, method="analytical")
        assert iterative_converged and analytical_converged is None
        answer = {
            0: 0.7916655540466309,
            1: 0.7916655540466309,
            2: 0.7916655540466309,
            3: 0.7916655540466309,
            4: 0.7916655540466308,
        }
        for n in sorted(G):
            assert i[n] == pytest.approx(answer[n], abs=5e-3) == a[n]

        b, _, iterative_converged = nx.domirank(G, method="iterative", alpha=0.5)
        a, _, analytical_converged = nx.domirank(G, method="analytical", alpha=0.5)
        assert iterative_converged and analytical_converged is None
        b_answer = {
            0: 0.66666579246521,
            1: 0.66666579246521,
            2: 0.66666579246521,
            3: 0.66666579246521,
            4: 0.66666579246521,
        }
        for n in sorted(G):
            assert b[n] == pytest.approx(b_answer[n], abs=5e-3) == a[n]

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
        b, _, converged = nx.domirank(G, epsilon=1e-9)
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
        G = nx.fast_gnp_random_graph(10, 2 / 10, directed=True, seed=42)
        cls.G = G.reverse()
        cls.drc = {
            0: 0.29488876461982727,
            1: 4.67141313957455e-31,
            2: 0.1227250024676323,
            3: 0.5260046720504761,
            4: 1.7550592422485352,
            5: -0.17216378450393677,
            6: 1.2767128944396973,
            7: 1.2767128944396973,
            8: -0.3470274806022644,
            9: 1.4781757593154907,
        }
        cls.drca = {
            0: 0.294844900617681,
            1: 0.0,
            2: 0.12269064278286526,
            3: 0.5260722943726253,
            4: 1.7549941765830046,
            5: -0.17215425783481575,
            6: 1.2767172579845019,
            7: 1.276717257984502,
            8: -0.3470142938948988,
            9: 1.4782096886790972,
        }
        cls.G_weighted = cls.G.copy()
        counter = 0
        number_of_edges = len(cls.G_weighted.edges())
        for _, _, w in cls.G_weighted.edges(data=True):
            counter += 1
            w["weight"] = counter / number_of_edges
        cls.drcw = {
            0: 0.017124131321907043,
            1: 3.0307206948131452e-18,
            2: 0.08629344403743744,
            3: 0.58540278673172,
            4: 0.5559653043746948,
            5: 0.14745399355888367,
            6: 0.580001950263977,
            7: 0.6754786968231201,
            8: 0.8270763754844666,
            9: 2.3496170043945312,
        }
        cls.drcwa = {
            0: 0.017126419063866822,
            1: 0.0,
            2: 0.08628814481433485,
            3: 0.5853591453037238,
            4: 0.556035199974221,
            5: 0.1474122206518499,
            6: 0.5800646950099848,
            7: 0.6755510836751828,
            8: 0.826982274634672,
            9: 2.3495809294540613,
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

    def test_domirank_centrality_directed_weighted(self):
        G = self.G_weighted
        b, _, converged = nx.domirank(G)
        assert converged
        for n in sorted(G):
            assert b[n] == pytest.approx(self.drcw[n], abs=5e-3)

    def test_domirank_centrality_directed_analytical_weighted(self):
        G = self.G_weighted
        b, _, converged = nx.domirank(G, method="analytical")
        assert converged is None
        for n in sorted(G):
            assert b[n] == pytest.approx(self.drcwa[n], abs=5e-3)


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
                1.5,
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
                500,
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
                5,
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
