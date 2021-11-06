"""TODO: Remove this test module for version 3.0."""


import pytest
import sys


# NOTE: It is necessary to prevent previous imports in the test suite from
# "contaminating" the tests for the deprecation warnings by removing
# node_classification from sys.modules.


def test_hmn_deprecation_warning():
    sys.modules.pop("networkx.algorithms.node_classification")
    with pytest.warns(DeprecationWarning):
        from networkx.algorithms.node_classification import hmn


def test_lgc_deprecation_warning():
    sys.modules.pop("networkx.algorithms.node_classification")
    with pytest.warns(DeprecationWarning):
        from networkx.algorithms.node_classification import lgc


def test_no_warn_on_function_or_package_import():
    # Accessing the functions shouldn't raise any warning
    with pytest.warns(None) as record:
        from networkx.algorithms.node_classification import (
            harmonic_function,
            local_and_global_consistency,
        )
    assert len(record) == 0
    with pytest.warns(None) as record:
        from networkx.algorithms import node_classification
    assert len(record) == 0
