import pytest


def test_namespace():
    with pytest.raises(ImportError):
        from networkx import nx
