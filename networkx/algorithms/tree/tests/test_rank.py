"""
Test functions and generators in ``rank.py``.

.. [camerini1980ranking]
    Camerini, P. M., Fratta, L., & Maffioli, F. (1980). Ranking
    arborescences in O (Km log n) time. European Journal of Operational
    Research, 4(4), 235-242.

"""
import math
from operator import eq

import networkx as nx
from networkx.algorithms.isomorphism import generic_edge_match
from networkx.algorithms.isomorphism.matchhelpers import close
from networkx.algorithms.tree import rank
import pytest

NODES = {"b1", "b2", "b3", "b4"}
EDGES = {"e1", "e2", "e3", "e4", "e5", "e6"}
SOURCE_MAP = {"e1": "b1", "e2": "b1", "e3": "b2", "e4": "b3", "e5": "b2", "e6": "b3"}
TARGET_MAP = {"e1": "b2", "e2": "b4", "e3": "b3", "e4": "b2", "e5": "b4", "e6": "b4"}
WEIGHT_MAP = {"e1": 6, "e2": 1, "e3": 10, "e4": 10, "e5": 12, "e6": 8}
DEEP_CYCLES = [{"e3", "e4"}, {"e4", "e5", "e6"}]
EM = generic_edge_match(["weight", "label"], [0, "b1"], [close, eq])


@pytest.fixture(scope="module")
def dg() -> nx.MultiDiGraph:
    """Init a case from page 237 in [camerini1980ranking]_ ."""
    res = nx.MultiDiGraph()
    res.add_edge("b1", "b2", label="e1", weight=6)
    res.add_edge("b1", "b4", label="e2", weight=1)
    res.add_edge("b2", "b3", label="e3", weight=10)
    res.add_edge("b3", "b2", label="e4", weight=10)
    res.add_edge("b2", "b4", label="e5", weight=12)
    res.add_edge("b4", "b3", label="e6", weight=8)
    return res


@pytest.fixture(scope="module")
def dg_attr() -> nx.DiGraph:
    """Init the page 237 case with edge attributes named "distance"."""
    dg = nx.DiGraph()
    dg.add_edge("b1", "b2", label="e1", distance=6)
    dg.add_edge("b1", "b4", label="e2", distance=1)
    dg.add_edge("b2", "b3", label="e3", distance=10)
    dg.add_edge("b3", "b2", label="e4", distance=10)
    dg.add_edge("b2", "b4", label="e5", distance=12)
    dg.add_edge("b4", "b3", label="e6", distance=8)
    return dg


@pytest.fixture(scope="module")
def dg_label() -> nx.DiGraph:
    """Init the page 237 case without edge label."""
    dg = nx.DiGraph()
    dg.add_edge("b1", "b2", weight=6)
    dg.add_edge("b1", "b4", weight=1)
    dg.add_edge("b2", "b3", weight=10)
    dg.add_edge("b3", "b2", weight=10)
    dg.add_edge("b2", "b4", weight=12)
    dg.add_edge("b4", "b3", weight=8)
    return dg


def check_example_camerini1980ranking(g: nx.DiGraph, attr: str):
    """Test the example in [camerini1980ranking]_ for ranking SAs.

    Args:
        dg: case in [camerini1980ranking]_ with 4 buses and 6 edges.
        attr: the edge attribute used to in determining optimality.
    """
    solver = rank.DescendSpanningArborescences(g, root="b1", attr=attr)

    assert set(solver.msa.df_edges["label"]) == {"e1", "e3", "e5"}
    assert solver.msa.size(weight=attr) == 28

    res2 = next(solver)[0]
    assert set(res2.df_edges["label"]) == {"e1", "e5", "e6"}
    assert res2.size(weight=attr) == 26

    res3 = next(solver)[0]
    assert set(res3.df_edges["label"]) == {"e2", "e4", "e6"}
    assert res3.size(weight=attr) == 19

    res4 = next(solver)[0]
    assert set(res4.df_edges["label"]) == {"e1", "e2", "e3"}
    assert res3.size(weight=attr) == 19

    res5 = next(solver)[0]
    assert set(res5.df_edges["label"]) == {"e1", "e2", "e6"}
    assert res3.size(weight=attr) == 19

    assert not nx.is_frozen(g)
    assert nx.is_frozen(solver.raw)


def test_descend_sa_attr(dg_attr: nx.DiGraph):
    """Check if another attribute can be used to in determining optimality."""
    check_example_camerini1980ranking(dg_attr, "distance")


def test_descend_sa_label(dg_label: nx.DiGraph):
    """Check if the graph is labelled automatically."""
    attr = "weight"
    solver = rank.DescendSpanningArborescences(
        dg_label,
        root="b1",
        attr=attr,
        labelled=False,
    )
    assert solver.msa.size(weight=attr) == 28


@pytest.fixture(scope="module")
def dgm(dg: nx.MultiDiGraph) -> rank.MultiDiGraphMap:
    """Init the case in [camerini1980ranking]. """
    res = rank.MultiDiGraphMap.from_nx(dg, "weight")
    return res


def test_collapse_into_cycle(dgm: rank.DiGraphMap):
    """Check if the graph collapsed into the deep cycle can be found.

    Note:
        There is only one deep cycle in this case.

    """
    cycle = nx.DiGraph()
    cycle.add_edge("b3", "b2", label="e4", weight=10)
    cycle.add_edge("b2", "b3", label="e3", weight=10)
    cycle = rank.DiGraphMap.from_nx(cycle)

    g, n = rank.collapse_into_cycle(dgm, cycle, "b1", node_corresponding="b2")
    assert set(g.nodes) == {"b1", "b2", "b4"} and n == "b2"


@pytest.fixture(scope="module")
def a2() -> rank.Arborescence:
    """Get the second SA of case in [camerini1980ranking]."""
    g = nx.DiGraph()
    g.add_edge("b1", "b2", label="e1", weight=6)
    g.add_edge("b2", "b4", label="e5", weight=12)
    g.add_edge("b4", "b3", label="e6", weight=8)
    res = rank.Arborescence(g)
    return res


@pytest.fixture(scope="module")
def a3() -> rank.Arborescence:
    """Get the third SA of case in [camerini1980ranking]."""
    g = nx.DiGraph()
    g.add_edge("b1", "b4", label="e2", weight=1)
    g.add_edge("b3", "b2", label="e4", weight=10)
    g.add_edge("b4", "b3", label="e6", weight=8)
    res = rank.Arborescence(g)
    return res


@pytest.fixture(scope="module")
def msa() -> rank.DiGraphMap:
    """Init min spanning arborescence of case in [camerini1980ranking]."""
    g = nx.DiGraph()
    g.add_edge("b1", "b2", weight=6, label="e1")
    g.add_edge("b2", "b3", weight=10, label="e3")
    g.add_edge("b2", "b4", weight=12, label="e5")

    res = rank.DiGraphMap.from_nx(g)
    return res


@pytest.mark.usefixtures("dg", "msa")
def test_next_sa(
    dg: nx.MultiDiGraph,
    msa: rank.DiGraphMap,
    a2: rank.Arborescence,
    a3: rank.Arborescence,
):
    """Check function for next spanning arborescence.

    Args:
        dg: the test case in [camerini1980ranking] with 4 buses and 6
            edges.
        msa: the max spanning arborescence of the test case in
            [camerini1980ranking].
        a2: the second spanning arborescence in [camerini1980ranking].
        a3: the third spanning arborescence in [camerini1980ranking].
    """
    msa.root = "b1"
    assert rank._next_sa(dg, msa, set(), set()) == ("e3", 2)
    assert rank._next_sa(dg, msa, {"e3"}, set()) == ("e5", 11)
    assert rank._next_sa(dg, a2, set(), {"e3"}) == ("e1", 7)
    assert rank._next_sa(dg, a2, {"e1"}, {"e3"}) == ("e5", 11)
    assert rank._next_sa(dg, a3, set(), {"e1", "e3"}) == (None, math.inf)


def test_descend_sa(dg: nx.MultiDiGraph):
    """Check the generator to rank spanning arborescences.

    Args:
        dg: case in [camerini1980ranking]_ with 4 buses and 6 edges.
    """
    check_example_camerini1980ranking(dg, "weight")


@pytest.fixture(scope="module")
def m1() -> nx.MultiDiGraph:
    """Init the first resulted graph in [camerini1980ranking].

    Returns:
        The first resulted graph.
    """
    res = nx.MultiDiGraph()
    res.add_edge("b1", "b2", label="e1", weight=-4)
    res.add_edge("b1", "b4", label="e2", weight=1)
    res.add_edge("b2", "b4", label="e5", weight=12)
    res.add_edge("b4", "b2", label="e6", weight=-2)
    return res


@pytest.fixture(scope="module")
def m2() -> nx.MultiDiGraph:
    """Init the second resulted graph in [camerini1980ranking].

    Returns:
        nx.MultiDiGraph: the second resulted graph
    """
    res = nx.MultiDiGraph()
    res.add_edge("b1", "b4", label="e1", weight=-2)
    res.add_edge("b1", "b4", label="e2", weight=-11)
    return res


@pytest.mark.usefixtures("dg")
def test_init_map(dg: nx.MultiDiGraph):
    """Check if multi directed graph can be defined by lists and maps.

    Args:
        dg (nx.DiGraph): a multi directed graph without
            any cycle.
    """
    graphs = {}
    graphs["full"] = rank.MultiDiGraphMap(
        NODES, EDGES, SOURCE_MAP, TARGET_MAP, WEIGHT_MAP
    )
    for node in graphs["full"].node_set:
        assert node in dg.nodes

    assert set(graphs["full"].edge_dict.keys()) == EDGES

    # There are extra items in maps, but they are not stored afterwards.
    _nodes_without_1 = ["b2", "b3", "b4"]
    _edges_without_12 = ["e3", "e4", "e5", "e6"]
    graphs["small"] = rank.MultiDiGraphMap(
        _nodes_without_1, _edges_without_12, SOURCE_MAP, TARGET_MAP, WEIGHT_MAP
    )
    for node in graphs["small"].node_set:
        assert node in _nodes_without_1
    assert "e1" not in graphs["small"].source_map.keys()
    assert "e1" not in graphs["small"].target_map.keys()
    assert "e1" not in graphs["small"].weight_map.keys()

    # There is an extra node called 'b1', but it is not considered.
    _edges_without_12 = ["e3", "e4", "e5", "e6"]
    graphs["extra_node"] = rank.MultiDiGraphMap(
        NODES, _edges_without_12, SOURCE_MAP, TARGET_MAP, WEIGHT_MAP
    )
    assert "b1" not in graphs["extra_node"].node_set


def test_simple_cycles():
    """Check the ``simple_cycles`` func multi graphs."""
    g = nx.MultiDiGraph()
    g.add_edge("b1", "b2", weight=1)
    g.add_edge("b2", "b3", weight=2)
    g.add_edge("b3", "b1", weight=3)
    g.add_edge("b3", "b1", weight=4)

    cycles = list(nx.simple_cycles(g))
    assert len(cycles) == 1
    assert set(cycles[0]) == {"b3", "b1", "b2"}
    assert g.number_of_edges("b3", "b1") == 2


def test_deep_cycles(dgm: rank.MultiDiGraphMap):
    """Check if the only deep cycle can be found.

    Args:
        dgm: the test case in [camerini1980ranking].
    """
    res = dgm.deep_cycles("b1")

    assert (
        len(res) == 2
        and type(list(res)[0]) is rank.DiGraphMap
        and (
            set(data["label"] for _, _, data in list(res)[0].edges(data=True))
            in DEEP_CYCLES
        )
        and (
            set(data["label"] for _, _, data in list(res)[1].edges(data=True))
            in DEEP_CYCLES
        )
    )


def test_branching(dgm: rank.DiGraphMap):
    """Check if methods for branching work.

    Args:
        dgm: case in [camerini1980ranking] with 4 buses and 6 edges.
    """
    branch = ["e4"]
    assert dgm.get_nodes_in_branch(branch) == {"b2", "b3"}
    assert type(dgm.first_node_exposed(branch, "b1")) is str

    branch = []
    assert type(dgm.first_node_exposed(branch, "b1")) is str


def test_mss(dgm: rank.MultiDiGraphMap, m1: nx.MultiDiGraph, m2: nx.MultiDiGraph):
    """Check if an exposed node can be handled correctly.

    Args:
        dgm: case in [camerini1980ranking] with 4 buses and 6 edges.
        m1: the first resulted graph of the test case
            in [camerini1980ranking].
        m2: the second resulted graph of the test case in
            [camerini1980ranking].
    """
    mss = rank.MinSpanSolver.from_map(dgm, "b1")

    mss.process(v="b2")

    assert set(mss.branch) == {"e4"}
    assert nx.is_isomorphic(dgm, mss.m, edge_match=EM)
    assert not all(mss.cycles.values())
    assert len(mss.lbd) == 1 and mss.lbd["b2"] == "e4"
    assert set(mss.forest.nodes) == {"e4"}
    assert not mss.forest.edges
    assert mss.first_node_exposed

    mss.process(v="b3", node_corresponding="b2")

    assert not mss.branch
    assert nx.is_isomorphic(mss.m, m1, edge_match=EM)
    assert mss.cycles["b2"] == {"e3", "e4"}
    assert mss.lbd["b2"] == "e4" and mss.lbd["b3"] == "e3"
    assert set(mss.forest.nodes) == {"e4", "e3"}
    assert not mss.forest.edges
    assert mss.first_node_exposed

    mss.process(v="b2")

    assert set(mss.branch) == {"e6"}
    assert nx.is_isomorphic(mss.m, m1, edge_match=EM)
    assert mss.cycles["b2"] == {"e3", "e4"}
    assert mss.lbd["b2"] == "e4" and mss.lbd["b3"] == "e3"
    assert set(mss.forest.nodes) == {"e4", "e3", "e6"}
    assert len(mss.forest.edges) == 2
    assert mss.first_node_exposed

    mss.process(v="b4", node_corresponding="b4")

    assert not mss.branch
    assert nx.is_isomorphic(mss.m, m2, edge_match=EM)
    assert mss.cycles["b2"] == {"e3", "e4"} and mss.cycles["b4"] == {"e5", "e6"}
    assert mss.lbd["b2"] == "e4" and mss.lbd["b3"] == "e3" and mss.lbd["b4"] == "e5"
    assert set(mss.forest.nodes) == {"e4", "e3", "e6", "e5"}
    assert set(mss.forest.edges) == {("e6", "e4"), ("e6", "e3")}
    assert mss.first_node_exposed

    mss.process(v="b4")

    assert set(mss.branch) == {"e1"}
    assert nx.is_isomorphic(mss.m, m2, edge_match=EM)
    assert mss.cycles["b2"] == {"e3", "e4"} and mss.cycles["b4"] == {"e5", "e6"}
    assert mss.lbd["b2"] == "e4" and mss.lbd["b3"] == "e3" and mss.lbd["b4"] == "e5"
    assert set(mss.forest.nodes) == {"e4", "e3", "e6", "e1", "e5"}
    assert set(mss.forest.edges) == {
        ("e6", "e4"),
        ("e6", "e3"),
        ("e1", "e6"),
        ("e1", "e5"),
    }
    assert not mss.first_node_exposed

    # Check the second part.
    assert mss.recover_msa() == {"e1", "e5", "e3"}


def test_seek(
    dgm: rank.MultiDiGraphMap,
    msa: rank.DiGraphMap,
    m1: nx.MultiDiGraph,
    m2: nx.MultiDiGraph,
):
    """Check if correct ``next`` edges can be found.

    Args:
        dgm: the test case in [camerini1980ranking] with 4 buses and 6
            edges.
        msa: the min spanning arborescence of the test case in
            [camerini1980ranking].
        m1: the first resulted graph of the test case in
            [camerini1980ranking].
        m2: the second resulted graph of the test case in
            [camerini1980ranking].
    """
    mss = rank.MinSpanSolver.from_map(dgm, "b1")
    assert mss._seek("e3", msa) == ("e6", 2)

    mss.m = rank.MultiDiGraphMap.from_nx(m1)
    assert mss._seek("e5", msa)[0] == "e2"

    mss.m = rank.MultiDiGraphMap.from_nx(m2)
    assert mss._seek("e1", msa)[0] == "e2"


def test_process_next(
    dgm: rank.MultiDiGraphMap,
    msa: rank.DiGraphMap,
    m1: nx.MultiDiGraph,
    m2: nx.MultiDiGraph,
):
    """Check if exposed node in NEXT can be handled correctly.

    Args:
        dgm: the test case in [camerini1980ranking]
            with 4 buses and 6 edges.
        msa: the min spanning arborescence of the test case
            in [camerini1980ranking].
        m1: the first resulted graph of the test case
            in [camerini1980ranking].
        m2: the second resulted graph of the test case
            in [camerini1980ranking].
    """
    mss = rank.MinSpanSolver.from_map(dgm, "b1")
    mss.process_next(msa, "b2")

    assert set(mss.branch) == {"e4"}
    assert nx.is_isomorphic(dgm, mss.m, edge_match=EM)

    mss.process_next(msa, "b3", node_corresponding="b2")
    assert not mss.branch
    assert nx.is_isomorphic(m1, mss.m, edge_match=EM)

    mss.process_next(msa, "b2")
    assert set(mss.branch) == {"e6"}
    assert nx.is_isomorphic(m1, mss.m, edge_match=EM)

    mss.process_next(msa, "b4", node_corresponding="b4")
    assert not mss.branch
    assert nx.is_isomorphic(m2, mss.m, edge_match=EM)

    mss.process_next(msa, "b4")
    assert set(mss.branch) == {"e1"}
    assert nx.is_isomorphic(m2, mss.m, edge_match=EM)


def test_max_sa(dg: nx.MultiDiGraph, msa: rank.DiGraphMap):
    """Check if the function for min span arborescence works.

    Args:
        dg (nx.MultiDiGraph): the test case in [camerini1980ranking]
            with 4 buses and 6 edges.
        msa (DiGraphMap): the max spanning arborescence of the test case
            in [camerini1980ranking].
    """
    msa_result = rank._max_sa(dg, "b1", set(), set())
    assert type(msa_result) is rank.Arborescence
    assert nx.is_isomorphic(msa_result, msa, edge_match=EM)
