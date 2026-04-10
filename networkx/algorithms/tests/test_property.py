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
