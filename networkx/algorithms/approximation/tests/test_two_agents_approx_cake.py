import pytest
from networkx.algorithms.approximation import divide_graphical_cake as dgc


class TestTwoAgentsCake:
    def test_agents_approx_algo(self):
        assert 4 / 9 == dgc.two_agents_approx_cake(2)
        assert 1 / 3 == dgc.two_agents_approx_cake(1)
        assert 13 / 27 == dgc.two_agents_approx_cake(3)
