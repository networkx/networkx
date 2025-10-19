"""Unit tests for the :mod:`networkx.generators.transport_networks` module."""
import itertools
import random

import pytest

import networkx as nx

NODES = range(100)
EDGES = list(itertools.combinations(NODES, 2))
STATIC_SCALAR_FIELD_VALUES = {k: random.uniform(5, 25) for k in NODES}
DYNAMIC_SCALAR_FIELD_VALUES = {
    k: lambda: v + random.uniform(-5.0, 5.0)
    for k, v in STATIC_SCALAR_FIELD_VALUES.items()
}


def test_gradient_network_static_values():
    # arrange
    substrate_network = nx.Graph(EDGES)
    nx.set_node_attributes(substrate_network, STATIC_SCALAR_FIELD_VALUES, "value")

    # act
    actual_gradient_network_1st_run = nx.gradient_network(substrate_network)
    actual_gradient_network_2nd_run = nx.gradient_network(substrate_network)

    # assert
    assert actual_gradient_network_1st_run.number_of_nodes() == len(substrate_network)
    assert actual_gradient_network_2nd_run.number_of_nodes() == len(substrate_network)
    assert nx.utils.graphs_equal(
        actual_gradient_network_1st_run, actual_gradient_network_2nd_run
    )


def test_gradient_network_dynamic_values():
    # arrange
    substrate_network = nx.Graph(EDGES)
    nx.set_node_attributes(substrate_network, DYNAMIC_SCALAR_FIELD_VALUES, "value")

    # act
    actual_gradient_network_1st_run = nx.gradient_network(substrate_network)
    actual_gradient_network_2nd_run = nx.gradient_network(substrate_network)

    # assert
    assert actual_gradient_network_1st_run.number_of_nodes() == len(substrate_network)
    assert actual_gradient_network_2nd_run.number_of_nodes() == len(substrate_network)
    assert not nx.utils.graphs_equal(
        actual_gradient_network_1st_run, actual_gradient_network_2nd_run
    )


@pytest.mark.parametrize("graph_class", (nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph))
def test_gradient_network_raises_error(graph_class):
    # arrange
    substrate_network = graph_class(EDGES)
    nx.set_node_attributes(substrate_network, STATIC_SCALAR_FIELD_VALUES, "value")

    # act + assert
    with pytest.raises(nx.NetworkXNotImplemented):
        _ = nx.gradient_network(substrate_network)
