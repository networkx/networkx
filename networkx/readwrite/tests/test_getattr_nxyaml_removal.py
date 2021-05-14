"""Test that informative exception messages are raised when attempting to
access nx_yaml."""

import pytest


def test_import_from_module():
    with pytest.raises(ImportError):
        import networkx.readwrite.nx_yaml.read_yaml
    with pytest.raises(ImportError):
        import networkx.readwrite.nx_yaml.write_yaml
