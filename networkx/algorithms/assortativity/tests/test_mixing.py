import pytest

np = pytest.importorskip("numpy")
npt = pytest.importorskip("numpy.testing")


import networkx as nx
from .base_test import BaseTestAttributeMixing, BaseTestDegreeMixing


class TestDegreeMixingDict(BaseTestDegreeMixing):
    def test_degree_mixing_dict_undirected(self):
        d = nx.degree_mixing_dict(self.P4)
        d_result = {1: {2: 2}, 2: {1: 2, 2: 2}}
        assert d == d_result

    def test_degree_mixing_dict_undirected_normalized(self):
        d = nx.degree_mixing_dict(self.P4, normalized=True)
        d_result = {1: {2: 1.0 / 3}, 2: {1: 1.0 / 3, 2: 1.0 / 3}}
        assert d == d_result

    def test_degree_mixing_dict_directed(self):
        d = nx.degree_mixing_dict(self.D)
        print(d)
        d_result = {1: {3: 2}, 2: {1: 1, 3: 1}, 3: {}}
        assert d == d_result

    def test_degree_mixing_dict_multigraph(self):
        d = nx.degree_mixing_dict(self.M)
        d_result = {1: {2: 1}, 2: {1: 1, 3: 3}, 3: {2: 3}}
        assert d == d_result


class TestDegreeMixingMatrix(BaseTestDegreeMixing):
    def test_degree_mixing_matrix_undirected(self):
        # fmt: off
        a_result = np.array([[0, 0, 0],
                             [0, 0, 2],
                             [0, 2, 2]]
                            )
        # fmt: on
        a = nx.degree_mixing_matrix(self.P4, normalized=False)
        npt.assert_equal(a, a_result)
        a = nx.degree_mixing_matrix(self.P4)
        npt.assert_equal(a, a_result / float(a_result.sum()))

    def test_degree_mixing_matrix_directed(self):
        # fmt: off
        a_result = np.array([[0, 0, 0, 0],
                             [0, 0, 0, 2],
                             [0, 1, 0, 1],
                             [0, 0, 0, 0]]
                            )
        # fmt: on
        a = nx.degree_mixing_matrix(self.D, normalized=False)
        npt.assert_equal(a, a_result)
        a = nx.degree_mixing_matrix(self.D)
        npt.assert_equal(a, a_result / float(a_result.sum()))

    def test_degree_mixing_matrix_multigraph(self):
        # fmt: off
        a_result = np.array([[0, 0, 0, 0],
                             [0, 0, 1, 0],
                             [0, 1, 0, 3],
                             [0, 0, 3, 0]]
                            )
        # fmt: on
        a = nx.degree_mixing_matrix(self.M, normalized=False)
        npt.assert_equal(a, a_result)
        a = nx.degree_mixing_matrix(self.M)
        npt.assert_equal(a, a_result / float(a_result.sum()))

    def test_degree_mixing_matrix_selfloop(self):
        # fmt: off
        a_result = np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 2]]
                            )
        # fmt: on
        a = nx.degree_mixing_matrix(self.S, normalized=False)
        npt.assert_equal(a, a_result)
        a = nx.degree_mixing_matrix(self.S)
        npt.assert_equal(a, a_result / float(a_result.sum()))


class TestAttributeMixingDict(BaseTestAttributeMixing):
    def test_attribute_mixing_dict_undirected(self):
        d = nx.attribute_mixing_dict(self.G, "fish")
        d_result = {
            "one": {"one": 2, "red": 1},
            "two": {"two": 2, "blue": 1},
            "red": {"one": 1},
            "blue": {"two": 1},
        }
        assert d == d_result

    def test_attribute_mixing_dict_directed(self):
        d = nx.attribute_mixing_dict(self.D, "fish")
        d_result = {
            "one": {"one": 1, "red": 1},
            "two": {"two": 1, "blue": 1},
            "red": {},
            "blue": {},
        }
        assert d == d_result

    def test_attribute_mixing_dict_multigraph(self):
        d = nx.attribute_mixing_dict(self.M, "fish")
        d_result = {"one": {"one": 4}, "two": {"two": 2}}
        assert d == d_result


class TestAttributeMixingMatrix(BaseTestAttributeMixing):
    def test_attribute_mixing_matrix_undirected(self):
        mapping = {"one": 0, "two": 1, "red": 2, "blue": 3}
        a_result = np.array([[2, 0, 1, 0], [0, 2, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]])
        a = nx.attribute_mixing_matrix(
            self.G, "fish", mapping=mapping, normalized=False
        )
        npt.assert_equal(a, a_result)
        a = nx.attribute_mixing_matrix(self.G, "fish", mapping=mapping)
        npt.assert_equal(a, a_result / float(a_result.sum()))

    def test_attribute_mixing_matrix_directed(self):
        mapping = {"one": 0, "two": 1, "red": 2, "blue": 3}
        a_result = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]])
        a = nx.attribute_mixing_matrix(
            self.D, "fish", mapping=mapping, normalized=False
        )
        npt.assert_equal(a, a_result)
        a = nx.attribute_mixing_matrix(self.D, "fish", mapping=mapping)
        npt.assert_equal(a, a_result / float(a_result.sum()))

    def test_attribute_mixing_matrix_multigraph(self):
        mapping = {"one": 0, "two": 1, "red": 2, "blue": 3}
        a_result = np.array([[4, 0, 0, 0], [0, 2, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        a = nx.attribute_mixing_matrix(
            self.M, "fish", mapping=mapping, normalized=False
        )
        npt.assert_equal(a, a_result)
        a = nx.attribute_mixing_matrix(self.M, "fish", mapping=mapping)
        npt.assert_equal(a, a_result / float(a_result.sum()))
