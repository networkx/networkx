import pytest

import networkx as nx


def test_random_tree():
    with pytest.raises(AttributeError, match=".*use nx.random_labeled_tree instead"):
        nx.random_tree(3)
