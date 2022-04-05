import pytest
import networkx as nx

# smoke tests for exceptions


def test_raises_Exception():
    with pytest.raises(nx.Exception):
        raise nx.Exception


def test_raises_networkxerr():
    with pytest.raises(nx.Error):
        raise nx.Error


def test_raises_networkx_pointless_concept():
    with pytest.raises(nx.PointlessConcept):
        raise nx.PointlessConcept


def test_raises_networkxalgorithmerr():
    with pytest.raises(nx.AlgorithmError):
        raise nx.AlgorithmError


def test_raises_networkx_unfeasible():
    with pytest.raises(nx.Unfeasible):
        raise nx.Unfeasible


def test_raises_networkx_no_path():
    with pytest.raises(nx.NoPath):
        raise nx.NoPath


def test_raises_networkx_unbounded():
    with pytest.raises(nx.Unbounded):
        raise nx.Unbounded
