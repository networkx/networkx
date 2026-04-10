import random

import hypothesis

import networkx as nx


def get_component(node, component):
    if component[node] == node:
        return node
    component[node] = get_component(component[node], component)
    return component[node]


def union(u, v, component):
    u_comp = get_component(u, component)
    v_comp = get_component(v, component)
    if u_comp != v_comp:
        component[u_comp] = v_comp


@hypothesis.strategies.composite
def undirected_adjacency_list(draw):
    n = draw(hypothesis.strategies.integers(min_value=3, max_value=100))
    # Build list of all possible directed edges with self-loops
    possible = [(i, j) for i in range(n) for j in range(i, n)]
    # choose a unique subset of these pairs
    pairs = draw(
        hypothesis.strategies.lists(
            hypothesis.strategies.sampled_from(possible),
            unique=True,
            min_size=n,
            max_size=max(1000, len(possible)),
        )
    )
    # attach a random weight to each chosen pair
    edges = []
    for u, v in pairs:
        w = draw(hypothesis.strategies.integers(min_value=1, max_value=100))
        edges.append((u, v, w))
    return edges


@hypothesis.strategies.composite
def undirected_no_self_loop_adjacency_list(draw, must_connected=False):
    n = draw(hypothesis.strategies.integers(min_value=3, max_value=100))
    # Build list of all possible directed edges without self-loops
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    # choose a unique subset of these pairs
    pairs = draw(
        hypothesis.strategies.lists(
            hypothesis.strategies.sampled_from(possible),
            unique=True,
            min_size=n,
            max_size=max(10000, len(possible)),
        )
    )
    if must_connected:
        nodes = set()
        for u, v in pairs:
            nodes.add(u)
            nodes.add(v)
        # Add any isolated nodes to the connected component
        prev_node = nodes.pop()
        while nodes:
            current_node = nodes.pop()
            if current_node < prev_node:
                if (current_node, prev_node) not in pairs:
                    pairs.append((current_node, prev_node))
            else:
                if (prev_node, current_node) not in pairs:
                    pairs.append((prev_node, current_node))
            prev_node = current_node

    # attach a random weight to each chosen pair
    edges = []
    for u, v in pairs:
        w = draw(hypothesis.strategies.integers(min_value=1, max_value=100))
        edges.append((u, v, w))

    return edges


@hypothesis.strategies.composite
def directed_no_self_loop_list(
    draw, must_connected=False, need_source=False, need_target=False
):
    n = draw(hypothesis.strategies.integers(min_value=3, max_value=100))
    # Build list of all possible directed edges without self-loops
    possible = [(i, j) for i in range(n) for j in range(n) if i != j]
    # choose a unique subset of these pairs
    pairs = draw(
        hypothesis.strategies.lists(
            hypothesis.strategies.sampled_from(possible),
            unique=True,
            min_size=n,
            max_size=len(possible),
        )
    )

    # if must_connected flag is set to true, make sure that the graph is connected
    if must_connected:
        nodes = set()
        for u, v in pairs:  # fetch all the nodes from the edges randomly selected
            nodes.add(u)
            nodes.add(v)

        # pick nodes randomly one by one, forming a tree with all the vertices
        prev_node = nodes.pop()
        if need_source:
            source = prev_node
        while nodes:
            current_node = nodes.pop()
            if (
                (prev_node, current_node) not in pairs
            ):  # if edge connecting (prev_node, current_node) is not in pairs,
                pairs.append((prev_node, current_node))  # add it to the pairs
            prev_node = current_node
        if need_target:
            target = prev_node
    # attach a random weight to each chosen pair
    edges = []
    for u, v in pairs:
        w = draw(hypothesis.strategies.integers(min_value=1, max_value=100))
        edges.append((u, v, w))

    if need_source and need_target:
        return edges, source, target
    elif need_source:
        return edges, source
    elif need_target:
        return edges, target
    return edges


@hypothesis.given(undirected_no_self_loop_adjacency_list(must_connected=True))
@hypothesis.settings(max_examples=100)
@hypothesis.example([(0, 1, 1), (0, 2, 1), (1, 3, 3)])
def test_minimum_spanning_tree(graph):
    """
    This method tests that the minimum spanning tree sum.
    The sum of any random spanning tree is less than or equal to the sum of a random spanning tree
    """
    G = nx.Graph()
    G.add_weighted_edges_from(graph)
    T = nx.minimum_spanning_tree(G)
    min_weight = 0
    for edge in T.edges(data=True):
        min_weight += edge[2]["weight"]

    n = G.number_of_nodes()
    random_weight = 0

    component = {i: i for i in G.nodes()}
    count = 0
    while count < n - 1:
        # select a random edge
        random_edge = random.choice(graph)
        u = random_edge[0]
        v = random_edge[1]
        w = random_edge[2]

        parent_u = get_component(u, component)
        parent_v = get_component(v, component)

        if (
            parent_u != parent_v
        ):  # if the vertices of the edge are not in the same component, add the edge
            random_weight += w  # add the weight of the edge
            union(parent_u, parent_v, component)  # merge the components
            count += 1  # increment the edge count

        graph.remove(
            random_edge
        )  # remove edge, as we have already considered this edge

    assert random_weight >= min_weight


@hypothesis.given(
    directed_no_self_loop_list(),
    hypothesis.strategies.integers(min_value=3, max_value=100),
)
@hypothesis.settings(max_examples=100)
@hypothesis.example(
    [
        (0, 1, 1),
        (0, 2, 1),
        (0, 3, 1),
        (1, 0, 1),
        (1, 2, 1),
        (1, 3, 1),
        (2, 0, 1),
        (2, 1, 3),
        (2, 3, 1),
        (3, 2, 1),
    ],
    3,
)
def test_no_tense_edge_in_SSSP(graph, source):
    """
    This method tests that there are no tense edges in the single-source shortest path tree
    """
    # Implementation for testing no tense edges in SSSP
    G = nx.DiGraph()
    G.add_weighted_edges_from(graph)
    if source not in G.nodes():
        return
    distance_vector, _ = nx.single_source_dijkstra(G, source)

    # iterate over all the edges
    for edge in G.edges(data=True):
        u = edge[0]
        v = edge[1]

        if u not in distance_vector:  # if u is not reachable from source, continue
            continue

        assert v in distance_vector
        hypothesis.note(
            f"Edge ({u}, {v}): weight = {edge[2]['weight']}, distance[{u}] = {distance_vector[u]}, distance[{v}] = {distance_vector[v]}"
        )
        assert (
            distance_vector[v] <= distance_vector[u] + edge[2]["weight"]
        )  # Make sure no tense edge is present


@hypothesis.given(undirected_no_self_loop_adjacency_list())
@hypothesis.settings(max_examples=100)
def test_even_degree(graph):
    """
    This method tests the following degree property of a vertex.
    1. The sum of all vertices in the graph have even degree.
    2. And even number of nodes have odd degree
    """
    G = nx.Graph()
    G.add_weighted_edges_from(graph)

    degree_sum = 0
    odd_degree_node_count = 0

    for node in G.nodes():
        degree_sum += G.degree(node)
        if G.degree(node) % 2 == 1:
            odd_degree_node_count += 1

    assert degree_sum % 2 == 0
    assert odd_degree_node_count % 2 == 0


@hypothesis.given(undirected_no_self_loop_adjacency_list(must_connected=True))
@hypothesis.settings(max_examples=100)
def test_closeness_centrality(graph):
    """
    This method tests that the closeness_centrality is between the inclusive range of 2/n and 1
    """
    G = nx.Graph()
    G.add_weighted_edges_from(graph)

    n = len(G.nodes())
    for node in G.nodes():
        closeness = nx.closeness_centrality(G, u=node)
        hypothesis.note(f"Node {node}: closeness = {closeness}")
        assert 2 / n <= closeness <= 1


@hypothesis.given(
    directed_no_self_loop_list(must_connected=True, need_source=True, need_target=True)
)
@hypothesis.settings(max_examples=100)
def test_min_cut(values):
    """
    This method tests that min cut of a connected directed graph is equal to atleast the min weight
    """
    graph, source, target = values
    G = nx.DiGraph()
    G.add_weighted_edges_from(graph, weight="capacity")

    if source not in G.nodes() or target not in G.nodes() or source == target:
        return
    min_capacity = min(edge[2]["capacity"] for edge in G.edges(data=True))

    min_cut_calculated, _ = nx.minimum_cut(G, source, target)
    hypothesis.note(
        f"Minimum cut: {min_cut_calculated}, Minimum capacity: {min_capacity}"
    )
    assert min_cut_calculated >= min_capacity


@hypothesis.given(directed_no_self_loop_list())
@hypothesis.settings(
    max_examples=100, deadline=None
)  # deadline=None because first run can be slow (import warmup)
@hypothesis.example(
    [(0, 1, 1), (1, 2, 1), (2, 0, 1)]
)  # also test this specific small cycle
def test_pagerank_dangling_node_validity(graph):
    """PageRank must produce a valid probability distribution even when
    dangling nodes (sinks with no outgoing edges) exist.
    Property: sum of all ranks == 1 and every rank >= 0."""

    # Build a directed graph from the random edge list
    G = nx.DiGraph()
    G.add_weighted_edges_from(graph)

    # Skip empty graphs (nothing to test)
    if len(G) == 0:
        return

    # Just for logging: find which nodes have no outgoing edges (dangling/sink nodes)
    dangling_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]

    # Run PageRank with default damping factor alpha=0.85
    pr = nx.pagerank(G, alpha=0.85)

    # Log some info (only printed when Hypothesis finds a failing example)
    hypothesis.note(f"Nodes: {len(G)}, Dangling nodes: {len(dangling_nodes)}")

    # CHECK 1: Every node's PageRank must be non-negative
    for n in G.nodes():
        assert pr[n] >= 0, f"Node {n} has negative PageRank {pr[n]}"

    # CHECK 2: All PageRank values must sum to 1.0 (it's a probability distribution)
    assert abs(sum(pr.values()) - 1.0) < 1e-6, f"PageRank sum {sum(pr.values())} != 1.0"


@hypothesis.given(
    hypothesis.strategies.integers(min_value=3, max_value=50)
)  # n = number of nodes, random between 3 and 50
@hypothesis.settings(max_examples=100, deadline=None)
@hypothesis.example(4)  # also test with exactly 4 nodes
def test_pagerank_symmetric_graph_equal_ranks(n):
    """In a complete directed graph every node is structurally identical,
    so all nodes must receive exactly the same PageRank = 1/n.
    Property: PR(v) == 1/n for all v in a complete digraph, for any alpha."""

    # Create a complete directed graph with n nodes
    # (every node has an edge to every other node)
    G = nx.complete_graph(n, create_using=nx.DiGraph)

    # Test with multiple alpha values to make sure symmetry holds across the board
    for alpha in [0.1, 0.5, 0.85, 0.99]:
        pr = nx.pagerank(G, alpha=alpha)

        # Every node should get exactly 1/n of the total rank
        expected = 1.0 / n
        for node, rank in pr.items():
            assert abs(rank - expected) < 1e-6, (
                f"Node {node}: rank {rank} != {expected} on complete graph with alpha={alpha}"
            )


@hypothesis.given(hypothesis.strategies.integers(min_value=3, max_value=50))
@hypothesis.settings(max_examples=100, deadline=None)
@hypothesis.example(5)
def test_pagerank_alpha_zero_gives_uniform(n):
    """When alpha=0 the random surfer never follows links, only teleports.
    Property: every node gets PageRank exactly 1/n regardless of graph structure."""

    # Even though we build a complete graph here, ANY graph structure would work
    # because alpha=0 means links are totally ignored
    G = nx.complete_graph(n, create_using=nx.DiGraph)
    pr = nx.pagerank(G, alpha=0)

    # Every node should have rank = 1/n since teleportation is uniform
    expected = 1.0 / n
    for node, rank in pr.items():
        assert abs(rank - expected) < 1e-6, (
            f"Node {node}: rank {rank} != expected {expected} at alpha=0"
        )


@hypothesis.given(
    directed_no_self_loop_list(),
    hypothesis.strategies.integers(min_value=0, max_value=99),
)
@hypothesis.settings(max_examples=100, deadline=None)
@hypothesis.example(
    [(0, 1, 1), (1, 2, 1), (2, 0, 1), (0, 2, 1)], 0
)  # small cycle with extra edge, target=node 0
def test_pagerank_adding_edges_increases_rank(graph, target_pick):
    """Adding more incoming edges to a node should not decrease its PageRank.
    Property: PR(v) in augmented graph >= PR(v) in original graph."""

    # Build the directed graph
    G = nx.DiGraph()
    G.add_weighted_edges_from(graph)

    # Need at least 3 nodes for a meaningful test
    if len(G) < 3:
        return

    # Pick a target node using modular arithmetic so target_pick maps to a valid node
    nodes = sorted(G.nodes())
    target = nodes[target_pick % len(nodes)]

    # Compute PageRank BEFORE adding new edges
    pr_before = nx.pagerank(G, alpha=0.85)

    # Find all nodes that DON'T currently have an edge pointing to our target
    non_predecessors = [n for n in nodes if n != target and not G.has_edge(n, target)]

    # If every node already points to target, nothing to add, skip
    if not non_predecessors:
        return

    # Make a copy and add edges from ALL non-predecessors to the target
    G2 = G.copy()
    for src in non_predecessors:
        G2.add_edge(src, target, weight=1)

    # Compute PageRank AFTER adding the new edges
    pr_after = nx.pagerank(G2, alpha=0.85)

    # Log for debugging (only shown on failure)
    hypothesis.note(
        f"Target={target}, rank before={pr_before[target]:.6f}, after={pr_after[target]:.6f}"
    )

    # The target's rank should NOT have decreased (with tiny tolerance for float precision)
    assert pr_after[target] >= pr_before[target] - 1e-6, (
        f"Adding incoming edges to {target} decreased its rank"
    )


@hypothesis.given(directed_no_self_loop_list())
@hypothesis.settings(max_examples=100, deadline=None)
@hypothesis.example([(0, 1, 1), (1, 2, 1), (2, 0, 1)])  # simple 3-node cycle
def test_pagerank_personalization_boosts_target(graph):
    """When we heavily personalize towards one node, that node's PageRank
    should increase compared to uniform personalization.
    Property: PR_personalized(v) > PR_uniform(v) for the personalized node."""

    # Build the graph
    G = nx.DiGraph()
    G.add_weighted_edges_from(graph)

    # Need at least 3 nodes
    if len(G) < 3:
        return

    # We'll personalize towards the first node (node 0 usually)
    nodes = sorted(G.nodes())
    target = nodes[0]

    # Step 1: Compute PageRank with DEFAULT (uniform) personalization
    # This is normal PageRank where teleportation goes to every node equally
    pr_uniform = nx.pagerank(G, alpha=0.85)

    # Step 2: Create a personalization vector that heavily favors the target.
    # Every node gets weight 1, but the target gets weight = 10 * number_of_nodes.
    # This means when the surfer teleports, it lands on target ~10x more often.
    personalization = {n: 1 for n in nodes}
    personalization[target] = len(nodes) * 10
    pr_personalized = nx.pagerank(G, alpha=0.85, personalization=personalization)

    # Log for debugging
    hypothesis.note(
        f"Target={target}, uniform={pr_uniform[target]:.6f}, personalized={pr_personalized[target]:.6f}"
    )

    # The target's rank with personalization should be >= its rank without
    assert pr_personalized[target] >= pr_uniform[target] - 1e-6, (
        f"Heavy personalization towards {target} did not boost its rank"
    )
