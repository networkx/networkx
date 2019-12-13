import pytest
import networkx as nx


def test_networkx_namespace():
    nx.approximation.ramsey
    nx.algorithms.approximation.ramsey
    with pytest.raises(AttributeError):
        nx.ramsey


def test_import_syntax():
    from networkx.algorithms.approximation import ramsey
    from networkx.algorithms import approximation
    from networkx import approximation


def test_import_limitations():
    with pytest.raises(ModuleNotFoundError):
        from networkx.approximation import ramsey
    with pytest.raises(ImportError):
        from networkx.algorithms import ramsey
    with pytest.raises(ImportError):
        from networkx import ramsey
