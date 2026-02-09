"""
Test for LSAP Solvers
"""

import pytest

from networkx.algorithms.bipartite_ged.solvers import SolverLSAP
from networkx.algorithms.bipartite_ged.tests.test_utils import *

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestSolverLSAP:
    """Tests for `SolverLSAP` output"""

    def setup_method(self):
        self.solver = SolverLSAP()

    def test_constant_cost_function_solution(self):
        cm = constant_cost_matrix()
        rows_res, cols_res = self.solver.solve(cm)
        assert np.sum(cm[rows_res, cols_res]) == 2

    def test_riesen_cost_function_solution(self):
        cm = riesen_cost_matrix()
        rows_res, cols_res = self.solver.solve(cm)
        assert np.sum(cm[rows_res, cols_res]) == 6

    def test_neighborhood_cost_function_solution(self):
        cm = neighborhood_cost_matrix()
        rows_res, cols_res = self.solver.solve(cm)
        assert np.sum(cm[rows_res, cols_res]) == 9
