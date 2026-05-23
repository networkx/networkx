"""
Tests for directed k-components algorithm.

These tests define the expected behavior of:
- weak_k_components: k-components ignoring edge direction
- strong_k_components: k-components respecting edge direction

Written following TDD approach as suggested by NetworkX
maintainers in Issue #7106.

References
----------
.. [1] White, D. R., & Harary, F. (2001). 
   The cohesiveness of blocks in social networks: 
   Node connectivity and conditional density.
   Paths and Semipaths: Reconceptualizing Structural 
   Cohesion in Terms of Directed Relations.
"""
import pytest
import networkx as nx


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _check_weak_connectivity(G, k_comps):
    """
    Verify weak k-components have correct node connectivity
    when direction is ignored.
    """
    G_undirected = G.to_undirected()
    for k, components in k_comps.items():
        if k < 3:
            continue
        for component in components:
            C = G_undirected.subgraph(component)
            K = nx.node_connectivity(C)
            assert K >= k, (
                f"Component {component} has connectivity "
                f"{K} but expected >= {k}"
            )


def _check_strong_connectivity(G, k_comps):
    """
    Verify strong k-components have correct node connectivity
    respecting edge direction.
    """
    for k, components in k_comps.items():
        if k < 3:
            continue
        for component in components:
            C = G.subgraph(component)
            K = nx.node_connectivity(C)
            assert K >= k, (
                f"Component {component} has connectivity "
                f"{K} but expected >= {k}"
            )


# ============================================================
# BASIC GRAPH FIXTURES
# ============================================================

def simple_directed_graph():
    """
    Simple directed graph for basic tests.
    
    A → B → C
    ↑       ↓
    └── D ──┘
    
    Forms a directed cycle: A→B→C→D→A
    """
    G = nx.DiGraph()
    G.add_edges_from([
        (0, 1), (1, 2), 
        (2, 3), (3, 0)
    ])
    return G


def directed_two_components():
    """
    Directed graph with two clearly separate components.
    
    Component 1: 0→1→2→0 (cycle)
    Component 2: 3→4→5→3 (cycle)
    Connected by: 2→3 (one way bridge)
    """
    G = nx.DiGraph()
    G.add_edges_from([
        (0, 1), (1, 2), (2, 0),  # component 1
        (3, 4), (4, 5), (5, 3),  # component 2
        (2, 3)                    # one-way bridge
    ])
    return G


def strongly_connected_directed_graph():
    """
    Strongly connected directed graph.
    Every node can reach every other node.
    
    0 ⇄ 1 ⇄ 2
    ↕       ↕
    3 ⇄ 4 ⇄ 5
    """
    G = nx.DiGraph()
    G.add_edges_from([
        (0, 1), (1, 0),
        (1, 2), (2, 1),
        (0, 3), (3, 0),
        (2, 5), (5, 2),
        (3, 4), (4, 3),
        (4, 5), (5, 4),
        (1, 4), (4, 1),
    ])
    return G


def directed_complete_graph():
    """
    Directed version of K4 — complete graph.
    Every node connects to every other node
    in both directions. Maximally connected.
    """
    G = nx.DiGraph()
    nodes = [0, 1, 2, 3]
    for u in nodes:
        for v in nodes:
            if u != v:
                G.add_edge(u, v)
    return G


# ============================================================
# SECTION 1: BASIC INPUT VALIDATION TESTS
# ============================================================

def test_weak_k_components_accepts_directed_graph():
    """
    weak_k_components must accept directed graphs
    without raising NetworkXNotImplemented.
    This is the core fix Issue #7106 asks for.
    """
    G = simple_directed_graph()
    # Should NOT raise NetworkXNotImplemented
    result = nx.weak_k_components(G)
    assert result is not None


def test_strong_k_components_accepts_directed_graph():
    """
    strong_k_components must accept directed graphs
    without raising NetworkXNotImplemented.
    """
    G = simple_directed_graph()
    # Should NOT raise NetworkXNotImplemented
    result = nx.strong_k_components(G)
    assert result is not None


def test_weak_k_components_rejects_undirected():
    """
    weak_k_components should only work on directed graphs.
    For undirected graphs, use nx.k_components instead.
    """
    G = nx.petersen_graph()  # undirected
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.weak_k_components(G)


def test_strong_k_components_rejects_undirected():
    """
    strong_k_components should only work on directed graphs.
    """
    G = nx.petersen_graph()  # undirected
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.strong_k_components(G)


# ============================================================
# SECTION 2: RETURN TYPE TESTS
# ============================================================

def test_weak_k_components_returns_dict():
    """
    weak_k_components must return a dictionary
    with integer keys (connectivity levels) and
    list of sets as values — matching k_components format.
    """
    G = simple_directed_graph()
    result = nx.weak_k_components(G)
    assert isinstance(result, dict)
    for k, components in result.items():
        assert isinstance(k, int)
        assert isinstance(components, list)
        for component in components:
            assert isinstance(component, (set, frozenset))


def test_strong_k_components_returns_dict():
    """
    strong_k_components must return a dictionary
    with same structure as weak_k_components.
    """
    G = simple_directed_graph()
    result = nx.strong_k_components(G)
    assert isinstance(result, dict)
    for k, components in result.items():
        assert isinstance(k, int)
        assert isinstance(components, list)
        for component in components:
            assert isinstance(component, (set, frozenset))


# ============================================================
# SECTION 3: EMPTY AND TRIVIAL GRAPH TESTS
# ============================================================

def test_weak_k_components_empty_graph():
    """
    Empty directed graph should return empty dict.
    No nodes = no components at any level.
    """
    G = nx.DiGraph()
    result = nx.weak_k_components(G)
    assert result == {}


def test_strong_k_components_empty_graph():
    """
    Empty directed graph should return empty dict.
    """
    G = nx.DiGraph()
    result = nx.strong_k_components(G)
    assert result == {}


def test_weak_k_components_single_node():
    """
    Single isolated node has no connectivity.
    Should return empty dict or k=0 entry.
    """
    G = nx.DiGraph()
    G.add_node(0)
    result = nx.weak_k_components(G)
    # Single node cannot form a k-component
    # with k >= 1 (needs at least 2 nodes)
    for k, components in result.items():
        for comp in components:
            assert len(comp) > 1, (
                "Single node should not form a k-component"
            )


def test_strong_k_components_single_node():
    """
    Single isolated node — same as weak version.
    """
    G = nx.DiGraph()
    G.add_node(0)
    result = nx.strong_k_components(G)
    for k, components in result.items():
        for comp in components:
            assert len(comp) > 1


def test_weak_k_components_no_edges():
    """
    Directed graph with nodes but no edges.
    Cannot form any k-components with k >= 1.
    """
    G = nx.DiGraph()
    G.add_nodes_from([0, 1, 2, 3, 4])
    result = nx.weak_k_components(G)
    assert result == {}


# ============================================================
# SECTION 4: WEAK vs STRONG DIFFERENCE TESTS
# ============================================================

def test_weak_finds_more_components_than_strong():
    """
    CORE TEST — This is the fundamental difference
    between weak and strong k-components.
    
    Weak ignores direction → finds more connectivity
    Strong respects direction → stricter requirement
    
    Therefore: weak components >= strong components
    in terms of what gets grouped together.
    """
    G = directed_two_components()
    weak_result = nx.weak_k_components(G)
    strong_result = nx.strong_k_components(G)
    
    # Count total components at each level
    weak_total = sum(len(v) for v in weak_result.values())
    strong_total = sum(len(v) for v in strong_result.values())
    
    # Weak should find at least as many components
    # as strong (or more, since it's less strict)
    assert weak_total >= strong_total


def test_symmetric_directed_graph_weak_equals_strong():
    """
    When all edges are bidirectional (symmetric),
    weak and strong k-components should be identical
    because direction doesn't matter.
    """
    G = strongly_connected_directed_graph()
    weak_result = nx.weak_k_components(G)
    strong_result = nx.strong_k_components(G)
    
    # For fully symmetric graph, results should match
    assert weak_result == strong_result


def test_one_way_edge_breaks_strong_not_weak():
    """
    A one-way edge between two groups:
    - Weak: ignores direction, sees it as connected
    - Strong: respects direction, sees it as one-way
    
    Graph: Group A ←→ Group A (bidirectional internally)
           Group B ←→ Group B (bidirectional internally)  
           Group A → Group B (ONE WAY bridge)
    
    Weak sees A and B as connected.
    Strong sees A → B but NOT B → A.
    """
    G = nx.DiGraph()
    # Group A — fully connected internally
    G.add_edges_from([
        (0, 1), (1, 0),
        (1, 2), (2, 1),
        (0, 2), (2, 0)
    ])
    # Group B — fully connected internally
    G.add_edges_from([
        (3, 4), (4, 3),
        (4, 5), (5, 4),
        (3, 5), (5, 3)
    ])
    # One-way bridge A → B only
    G.add_edge(2, 3)
    
    weak_result = nx.weak_k_components(G)
    strong_result = nx.strong_k_components(G)
    
    # Weak connectivity ignores the direction of bridge
    # Strong connectivity must respect it
    # So strong should NOT merge A and B into same component
    if 1 in strong_result:
        strong_nodes = [
            node 
            for comp in strong_result[1] 
            for node in comp
        ]
        # Nodes from A and B should NOT be 
        # in same strong component
        for comp in strong_result.get(1, []):
            has_a = any(n in {0, 1, 2} for n in comp)
            has_b = any(n in {3, 4, 5} for n in comp)
            assert not (has_a and has_b), (
                "Strong components should not merge "
                "one-way connected groups"
            )


# ============================================================
# SECTION 5: KNOWN GRAPH TESTS
# ============================================================

def test_directed_complete_graph_high_connectivity():
    """
    Complete directed graph K4 (all edges both directions).
    Should have very high k-connectivity since every
    node connects to every other node in both directions.
    """
    G = directed_complete_graph()
    result = nx.weak_k_components(G)
    
    # All nodes should be in highest connectivity component
    all_nodes = set(G.nodes())
    found_all_nodes = False
    for k, components in result.items():
        for comp in components:
            if all_nodes.issubset(comp):
                found_all_nodes = True
    assert found_all_nodes, (
        "All nodes should appear in some k-component "
        "for complete directed graph"
    )


def test_directed_cycle_connectivity():
    """
    Directed cycle: 0→1→2→3→0
    This is 1-connected (weakly) since removing
    any node breaks the cycle.
    """
    G = nx.DiGraph()
    G.add_edges_from([(0,1), (1,2), (2,3), (3,0)])
    result = nx.weak_k_components(G)
    
    # Should have a 1-component containing all nodes
    assert 1 in result
    all_nodes = set(G.nodes())
    assert any(
        all_nodes.issubset(comp) 
        for comp in result[1]
    )


def test_strong_k_components_directed_cycle():
    """
    Directed cycle is strongly connected —
    every node can reach every other node.
    Should appear as a strong k-component.
    """
    G = nx.DiGraph()
    G.add_edges_from([(0,1), (1,2), (2,3), (3,0)])
    result = nx.strong_k_components(G)
    
    assert 1 in result
    all_nodes = set(G.nodes())
    assert any(
        all_nodes.issubset(comp)
        for comp in result[1]
    )


# ============================================================
# SECTION 6: CONSISTENCY TESTS
# ============================================================

def test_weak_k_components_nodes_subset_of_graph():
    """
    All nodes in k-components must be actual
    nodes that exist in the graph.
    No phantom nodes should appear.
    """
    G = strongly_connected_directed_graph()
    result = nx.weak_k_components(G)
    graph_nodes = set(G.nodes())
    
    for k, components in result.items():
        for comp in components:
            assert comp.issubset(graph_nodes), (
                f"Component contains nodes not in graph: "
                f"{comp - graph_nodes}"
            )


def test_strong_k_components_nodes_subset_of_graph():
    """
    Same node validity check for strong k-components.
    """
    G = strongly_connected_directed_graph()
    result = nx.strong_k_components(G)
    graph_nodes = set(G.nodes())
    
    for k, components in result.items():
        for comp in components:
            assert comp.issubset(graph_nodes)


def test_weak_k_components_keys_are_positive():
    """
    All connectivity levels k must be positive integers.
    k=0 means no connectivity — not a valid component.
    """
    G = strongly_connected_directed_graph()
    result = nx.weak_k_components(G)
    
    for k in result.keys():
        assert k >= 1, f"Found invalid connectivity level k={k}"


def test_weak_k_components_connectivity_check():
    """
    Full connectivity verification for weak k-components.
    Uses helper function to verify each component
    has at least k node-independent paths.
    """
    G = strongly_connected_directed_graph()
    result = nx.weak_k_components(G)
    _check_weak_connectivity(G, result)


def test_strong_k_components_connectivity_check():
    """
    Full connectivity verification for strong k-components.
    """
    G = strongly_connected_directed_graph()
    result = nx.strong_k_components(G)
    _check_strong_connectivity(G, result)


# ============================================================
# SECTION 7: RANDOM GRAPH TESTS
# ============================================================

@pytest.mark.parametrize("seed", [42, 123, 456])
def test_weak_k_components_random_directed(seed):
    """
    Test weak_k_components on random directed graphs
    with different random seeds for robustness.
    """
    G = nx.gnp_random_graph(10, 0.4, directed=True, seed=seed)
    result = nx.weak_k_components(G)
    _check_weak_connectivity(G, result)


@pytest.mark.parametrize("seed", [42, 123, 456])
def test_strong_k_components_random_directed(seed):
    """
    Test strong_k_components on random directed graphs.
    """
    G = nx.gnp_random_graph(10, 0.4, directed=True, seed=seed)
    result = nx.strong_k_components(G)
    _check_strong_connectivity(G, result)