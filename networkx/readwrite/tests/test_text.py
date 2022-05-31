import itertools as it
from textwrap import dedent

import pytest

import networkx as nx


def test_directed_tree_str():
    # Create a directed forest with labels
    graph = nx.balanced_tree(r=2, h=2, create_using=nx.DiGraph)
    for node in graph.nodes:
        graph.nodes[node]["label"] = "node_" + chr(ord("a") + node)

    node_target = dedent(
        """
        ╙── 0
            ├─╼ 1
            │   ├─╼ 3
            │   └─╼ 4
            └─╼ 2
                ├─╼ 5
                └─╼ 6
        """
    ).strip()

    label_target = dedent(
        """
        ╙── node_a
            ├─╼ node_b
            │   ├─╼ node_d
            │   └─╼ node_e
            └─╼ node_c
                ├─╼ node_f
                └─╼ node_g
        """
    ).strip()

    # Basic node case
    ret = nx.forest_str(graph, with_labels=False)
    print(ret)
    assert ret == node_target

    # Basic label case
    ret = nx.forest_str(graph, with_labels=True)
    print(ret)
    assert ret == label_target

    # Custom write function case
    lines = []
    ret = nx.forest_str(graph, write=lines.append, with_labels=False)
    assert ret is None
    assert lines == node_target.split("\n")

    # Smoke test to ensure passing the print function works. To properly test
    # this case we would need to capture stdout. (for potential reference
    # implementation see :class:`ubelt.util_stream.CaptureStdout`)
    ret = nx.forest_str(graph, write=print)
    assert ret is None


def test_empty_graph():
    assert nx.graph_str(nx.DiGraph()) == "╙"
    assert nx.graph_str(nx.Graph()) == "╙"
    assert nx.graph_str(nx.DiGraph(), ascii_only=True) == "+"
    assert nx.graph_str(nx.Graph(), ascii_only=True) == "+"


def test_within_forest_glyph():
    g = nx.DiGraph()
    g.add_nodes_from([1, 2, 3, 4])
    g.add_edge(2, 4)
    lines = []
    write = lines.append
    nx.graph_str(g, write=write)
    nx.graph_str(g, write=write, ascii_only=True)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╟── 1
        ╟── 2
        ╎   └─╼ 4
        ╙── 3
        +-- 1
        +-- 2
        :   L-> 4
        +-- 3
        """
    ).strip()
    assert text == target


def test_directed_multi_tree_forest():
    tree1 = nx.balanced_tree(r=2, h=2, create_using=nx.DiGraph)
    tree2 = nx.balanced_tree(r=2, h=2, create_using=nx.DiGraph)
    forest = nx.disjoint_union_all([tree1, tree2])
    ret = nx.forest_str(forest)
    print(ret)

    target = dedent(
        """
        ╟── 0
        ╎   ├─╼ 1
        ╎   │   ├─╼ 3
        ╎   │   └─╼ 4
        ╎   └─╼ 2
        ╎       ├─╼ 5
        ╎       └─╼ 6
        ╙── 7
            ├─╼ 8
            │   ├─╼ 10
            │   └─╼ 11
            └─╼ 9
                ├─╼ 12
                └─╼ 13
        """
    ).strip()
    assert ret == target

    tree3 = nx.balanced_tree(r=2, h=2, create_using=nx.DiGraph)
    forest = nx.disjoint_union_all([tree1, tree2, tree3])
    ret = nx.forest_str(forest, sources=[0, 14, 7])
    print(ret)

    target = dedent(
        """
        ╟── 0
        ╎   ├─╼ 1
        ╎   │   ├─╼ 3
        ╎   │   └─╼ 4
        ╎   └─╼ 2
        ╎       ├─╼ 5
        ╎       └─╼ 6
        ╟── 14
        ╎   ├─╼ 15
        ╎   │   ├─╼ 17
        ╎   │   └─╼ 18
        ╎   └─╼ 16
        ╎       ├─╼ 19
        ╎       └─╼ 20
        ╙── 7
            ├─╼ 8
            │   ├─╼ 10
            │   └─╼ 11
            └─╼ 9
                ├─╼ 12
                └─╼ 13
        """
    ).strip()
    assert ret == target

    ret = nx.forest_str(forest, sources=[0, 14, 7], ascii_only=True)
    print(ret)

    target = dedent(
        """
        +-- 0
        :   |-> 1
        :   |   |-> 3
        :   |   L-> 4
        :   L-> 2
        :       |-> 5
        :       L-> 6
        +-- 14
        :   |-> 15
        :   |   |-> 17
        :   |   L-> 18
        :   L-> 16
        :       |-> 19
        :       L-> 20
        +-- 7
            |-> 8
            |   |-> 10
            |   L-> 11
            L-> 9
                |-> 12
                L-> 13
        """
    ).strip()
    assert ret == target


def test_undirected_multi_tree_forest():
    tree1 = nx.balanced_tree(r=2, h=2, create_using=nx.Graph)
    tree2 = nx.balanced_tree(r=2, h=2, create_using=nx.Graph)
    tree2 = nx.relabel_nodes(tree2, {n: n + len(tree1) for n in tree2.nodes})
    forest = nx.union(tree1, tree2)
    ret = nx.forest_str(forest, sources=[0, 7])
    print(ret)

    target = dedent(
        """
        ╟── 0
        ╎   ├── 1
        ╎   │   ├── 3
        ╎   │   └── 4
        ╎   └── 2
        ╎       ├── 5
        ╎       └── 6
        ╙── 7
            ├── 8
            │   ├── 10
            │   └── 11
            └── 9
                ├── 12
                └── 13
        """
    ).strip()
    assert ret == target

    ret = nx.forest_str(forest, sources=[0, 7], ascii_only=True)
    print(ret)

    target = dedent(
        """
        +-- 0
        :   |-- 1
        :   |   |-- 3
        :   |   L-- 4
        :   L-- 2
        :       |-- 5
        :       L-- 6
        +-- 7
            |-- 8
            |   |-- 10
            |   L-- 11
            L-- 9
                |-- 12
                L-- 13
        """
    ).strip()
    assert ret == target


def test_undirected_tree_str():
    # Create a directed forest
    graph = nx.balanced_tree(r=2, h=2, create_using=nx.Graph)

    # arbitrary starting point
    nx.forest_str(graph)

    node_target0 = dedent(
        """
        ╙── 0
            ├── 1
            │   ├── 3
            │   └── 4
            └── 2
                ├── 5
                └── 6
        """
    ).strip()

    # defined starting point
    ret = nx.forest_str(graph, sources=[0])
    print(ret)
    assert ret == node_target0

    # defined starting point
    node_target2 = dedent(
        """
        ╙── 2
            ├── 0
            │   └── 1
            │       ├── 3
            │       └── 4
            ├── 5
            └── 6
        """
    ).strip()
    ret = nx.forest_str(graph, sources=[2])
    print(ret)
    assert ret == node_target2


def test_forest_str_errors():
    ugraph = nx.complete_graph(3, create_using=nx.Graph)

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.forest_str(ugraph)

    dgraph = nx.complete_graph(3, create_using=nx.DiGraph)

    with pytest.raises(nx.NetworkXNotImplemented):
        nx.forest_str(dgraph)


def test_overspecified_sources():
    """
    When sources are directly specified, we wont be able to determine when we
    are in the last component, so there will always be a trailing, leftmost
    pipe.
    """
    graph = nx.disjoint_union_all(
        [
            nx.balanced_tree(r=2, h=1, create_using=nx.DiGraph),
            nx.balanced_tree(r=1, h=2, create_using=nx.DiGraph),
            nx.balanced_tree(r=2, h=1, create_using=nx.DiGraph),
        ]
    )

    # defined starting point
    target1 = dedent(
        """
        ╟── 0
        ╎   ├─╼ 1
        ╎   └─╼ 2
        ╟── 3
        ╎   └─╼ 4
        ╎       └─╼ 5
        ╟── 6
        ╎   ├─╼ 7
        ╎   └─╼ 8
        """
    ).strip()

    target2 = dedent(
        """
        ╟── 0
        ╎   ├─╼ 1
        ╎   └─╼ 2
        ╟── 3
        ╎   └─╼ 4
        ╎       └─╼ 5
        ╙── 6
            ├─╼ 7
            └─╼ 8
        """
    ).strip()

    lines = []
    nx.forest_str(graph, write=lines.append, sources=graph.nodes)
    got1 = "\n".join(lines)
    print("got1: ")
    print(got1)

    lines = []
    nx.forest_str(graph, write=lines.append)
    got2 = "\n".join(lines)
    print("got2: ")
    print(got2)

    assert got1 == target1
    assert got2 == target2


def test_graph_str_iterative_add_directed_edges():
    """
    Walk through the cases going from a diconnected to fully connected graph
    """
    graph = nx.DiGraph()
    graph.add_nodes_from([1, 2, 3, 4])
    lines = []
    write = lines.append
    write("--- initial state ---")
    nx.graph_str(graph, write=write)
    for i, j in it.product(graph.nodes, graph.nodes):
        write(f"--- add_edge({i}, {j}) ---")
        graph.add_edge(i, j)
        nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    # defined starting point
    target = dedent(
        """
        --- initial state ---
        ╟── 1
        ╟── 2
        ╟── 3
        ╙── 4
        --- add_edge(1, 1) ---
        ╟── 1 ╾ 1
        ╎   └─╼  ...
        ╟── 2
        ╟── 3
        ╙── 4
        --- add_edge(1, 2) ---
        ╟── 1 ╾ 1
        ╎   ├─╼ 2
        ╎   └─╼  ...
        ╟── 3
        ╙── 4
        --- add_edge(1, 3) ---
        ╟── 1 ╾ 1
        ╎   ├─╼ 2
        ╎   ├─╼ 3
        ╎   └─╼  ...
        ╙── 4
        --- add_edge(1, 4) ---
        ╙── 1 ╾ 1
            ├─╼ 2
            ├─╼ 3
            ├─╼ 4
            └─╼  ...
        --- add_edge(2, 1) ---
        ╙── 2 ╾ 1
            └─╼ 1 ╾ 1
                ├─╼ 3
                ├─╼ 4
                └─╼  ...
        --- add_edge(2, 2) ---
        ╙── 1 ╾ 1, 2
            ├─╼ 2 ╾ 2
            │   └─╼  ...
            ├─╼ 3
            ├─╼ 4
            └─╼  ...
        --- add_edge(2, 3) ---
        ╙── 1 ╾ 1, 2
            ├─╼ 2 ╾ 2
            │   ├─╼ 3 ╾ 1
            │   └─╼  ...
            ├─╼ 4
            └─╼  ...
        --- add_edge(2, 4) ---
        ╙── 1 ╾ 1, 2
            ├─╼ 2 ╾ 2
            │   ├─╼ 3 ╾ 1
            │   ├─╼ 4 ╾ 1
            │   └─╼  ...
            └─╼  ...
        --- add_edge(3, 1) ---
        ╙── 2 ╾ 1, 2
            ├─╼ 1 ╾ 1, 3
            │   ├─╼ 3 ╾ 2
            │   │   └─╼  ...
            │   ├─╼ 4 ╾ 2
            │   └─╼  ...
            └─╼  ...
        --- add_edge(3, 2) ---
        ╙── 3 ╾ 1, 2
            ├─╼ 1 ╾ 1, 2
            │   ├─╼ 2 ╾ 2, 3
            │   │   ├─╼ 4 ╾ 1
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- add_edge(3, 3) ---
        ╙── 1 ╾ 1, 2, 3
            ├─╼ 2 ╾ 2, 3
            │   ├─╼ 3 ╾ 1, 3
            │   │   └─╼  ...
            │   ├─╼ 4 ╾ 1
            │   └─╼  ...
            └─╼  ...
        --- add_edge(3, 4) ---
        ╙── 1 ╾ 1, 2, 3
            ├─╼ 2 ╾ 2, 3
            │   ├─╼ 3 ╾ 1, 3
            │   │   ├─╼ 4 ╾ 1, 2
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- add_edge(4, 1) ---
        ╙── 2 ╾ 1, 2, 3
            ├─╼ 1 ╾ 1, 3, 4
            │   ├─╼ 3 ╾ 2, 3
            │   │   ├─╼ 4 ╾ 1, 2
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- add_edge(4, 2) ---
        ╙── 3 ╾ 1, 2, 3
            ├─╼ 1 ╾ 1, 2, 4
            │   ├─╼ 2 ╾ 2, 3, 4
            │   │   ├─╼ 4 ╾ 1, 3
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- add_edge(4, 3) ---
        ╙── 4 ╾ 1, 2, 3
            ├─╼ 1 ╾ 1, 2, 3
            │   ├─╼ 2 ╾ 2, 3, 4
            │   │   ├─╼ 3 ╾ 1, 3, 4
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- add_edge(4, 4) ---
        ╙── 1 ╾ 1, 2, 3, 4
            ├─╼ 2 ╾ 2, 3, 4
            │   ├─╼ 3 ╾ 1, 3, 4
            │   │   ├─╼ 4 ╾ 1, 2, 4
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        """
    ).strip()
    assert target == text


def test_graph_str_iterative_add_undirected_edges():
    """
    Walk through the cases going from a diconnected to fully connected graph
    """
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4])
    lines = []
    write = lines.append
    write("--- initial state ---")
    nx.graph_str(graph, write=write)
    for i, j in it.product(graph.nodes, graph.nodes):
        if i == j:
            continue
        write(f"--- add_edge({i}, {j}) ---")
        graph.add_edge(i, j)
        nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        --- initial state ---
        ╟── 1
        ╟── 2
        ╟── 3
        ╙── 4
        --- add_edge(1, 2) ---
        ╟── 3
        ╟── 4
        ╙── 1
            └── 2
        --- add_edge(1, 3) ---
        ╟── 4
        ╙── 2
            └── 1
                └── 3
        --- add_edge(1, 4) ---
        ╙── 2
            └── 1
                ├── 3
                └── 4
        --- add_edge(2, 1) ---
        ╙── 2
            └── 1
                ├── 3
                └── 4
        --- add_edge(2, 3) ---
        ╙── 4
            └── 1
                ├── 2
                │   └── 3 ─ 1
                └──  ...
        --- add_edge(2, 4) ---
        ╙── 3
            ├── 1
            │   ├── 2 ─ 3
            │   │   └── 4 ─ 1
            │   └──  ...
            └──  ...
        --- add_edge(3, 1) ---
        ╙── 3
            ├── 1
            │   ├── 2 ─ 3
            │   │   └── 4 ─ 1
            │   └──  ...
            └──  ...
        --- add_edge(3, 2) ---
        ╙── 3
            ├── 1
            │   ├── 2 ─ 3
            │   │   └── 4 ─ 1
            │   └──  ...
            └──  ...
        --- add_edge(3, 4) ---
        ╙── 1
            ├── 2
            │   ├── 3 ─ 1
            │   │   └── 4 ─ 1, 2
            │   └──  ...
            └──  ...
        --- add_edge(4, 1) ---
        ╙── 1
            ├── 2
            │   ├── 3 ─ 1
            │   │   └── 4 ─ 1, 2
            │   └──  ...
            └──  ...
        --- add_edge(4, 2) ---
        ╙── 1
            ├── 2
            │   ├── 3 ─ 1
            │   │   └── 4 ─ 1, 2
            │   └──  ...
            └──  ...
        --- add_edge(4, 3) ---
        ╙── 1
            ├── 2
            │   ├── 3 ─ 1
            │   │   └── 4 ─ 1, 2
            │   └──  ...
            └──  ...
        """
    ).strip()
    assert target == text


def test_graph_str_iterative_add_random_directed_edges():
    """
    Walk through the cases going from a diconnected to fully connected graph
    """
    import random

    rng = random.Random(724466096)
    graph = nx.DiGraph()
    graph.add_nodes_from([1, 2, 3, 4, 5])
    possible_edges = list(it.product(graph.nodes, graph.nodes))
    rng.shuffle(possible_edges)
    graph.add_edges_from(possible_edges[0:8])
    lines = []
    write = lines.append
    write("--- initial state ---")
    nx.graph_str(graph, write=write)
    for i, j in possible_edges[8:12]:
        write(f"--- add_edge({i}, {j}) ---")
        graph.add_edge(i, j)
        nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        --- initial state ---
        ╙── 3 ╾ 5
            └─╼ 2 ╾ 2
                ├─╼ 4 ╾ 4
                │   ├─╼ 5
                │   │   ├─╼ 1 ╾ 1
                │   │   │   └─╼  ...
                │   │   └─╼  ...
                │   └─╼  ...
                └─╼  ...
        --- add_edge(4, 1) ---
        ╙── 3 ╾ 5
            └─╼ 2 ╾ 2
                ├─╼ 4 ╾ 4
                │   ├─╼ 5
                │   │   ├─╼ 1 ╾ 1, 4
                │   │   │   └─╼  ...
                │   │   └─╼  ...
                │   └─╼  ...
                └─╼  ...
        --- add_edge(2, 1) ---
        ╙── 3 ╾ 5
            └─╼ 2 ╾ 2
                ├─╼ 4 ╾ 4
                │   ├─╼ 5
                │   │   ├─╼ 1 ╾ 1, 4, 2
                │   │   │   └─╼  ...
                │   │   └─╼  ...
                │   └─╼  ...
                └─╼  ...
        --- add_edge(5, 2) ---
        ╙── 3 ╾ 5
            └─╼ 2 ╾ 2, 5
                ├─╼ 4 ╾ 4
                │   ├─╼ 5
                │   │   ├─╼ 1 ╾ 1, 4, 2
                │   │   │   └─╼  ...
                │   │   └─╼  ...
                │   └─╼  ...
                └─╼  ...
        --- add_edge(1, 5) ---
        ╙── 3 ╾ 5
            └─╼ 2 ╾ 2, 5
                ├─╼ 4 ╾ 4
                │   ├─╼ 5 ╾ 1
                │   │   ├─╼ 1 ╾ 1, 4, 2
                │   │   │   └─╼  ...
                │   │   └─╼  ...
                │   └─╼  ...
                └─╼  ...

        """
    ).strip()
    assert target == text


def test_graph_str_nearly_forest():
    g = nx.DiGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 5)
    g.add_edge(2, 3)
    g.add_edge(3, 4)
    g.add_edge(5, 6)
    g.add_edge(6, 7)
    g.add_edge(6, 8)
    orig = g.copy()
    g.add_edge(1, 8)  # forward edge
    g.add_edge(4, 2)  # back edge
    g.add_edge(6, 3)  # cross edge
    lines = []
    write = lines.append
    write("--- directed case ---")
    nx.graph_str(orig, write=write)
    write("--- add (1, 8), (4, 2), (6, 3) ---")
    nx.graph_str(g, write=write)
    write("--- undirected case ---")
    nx.graph_str(orig.to_undirected(), write=write, sources=[1])
    write("--- add (1, 8), (4, 2), (6, 3) ---")
    nx.graph_str(g.to_undirected(), write=write, sources=[1])
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        --- directed case ---
        ╙── 1
            ├─╼ 2
            │   └─╼ 3
            │       └─╼ 4
            └─╼ 5
                └─╼ 6
                    ├─╼ 7
                    └─╼ 8
        --- add (1, 8), (4, 2), (6, 3) ---
        ╙── 1
            ├─╼ 2 ╾ 4
            │   └─╼ 3 ╾ 6
            │       └─╼ 4
            │           └─╼  ...
            ├─╼ 5
            │   └─╼ 6
            │       ├─╼ 7
            │       ├─╼ 8 ╾ 1
            │       └─╼  ...
            └─╼  ...
        --- undirected case ---
        ╙── 1
            ├── 2
            │   └── 3
            │       └── 4
            └── 5
                └── 6
                    ├── 7
                    └── 8
        --- add (1, 8), (4, 2), (6, 3) ---
        ╙── 1
            ├── 2
            │   ├── 3
            │   │   ├── 4 ─ 2
            │   │   └── 6
            │   │       ├── 5 ─ 1
            │   │       ├── 7
            │   │       └── 8 ─ 1
            │   └──  ...
            └──  ...
        """
    ).strip()
    assert target == text


def test_graph_str_complete_graph_ascii_only():
    graph = nx.generators.complete_graph(5, create_using=nx.DiGraph)
    lines = []
    write = lines.append
    write("--- directed case ---")
    nx.graph_str(graph, write=write, ascii_only=True)
    write("--- undirected case ---")
    nx.graph_str(graph.to_undirected(), write=write, ascii_only=True)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        --- directed case ---
        +-- 0 <- 1, 2, 3, 4
            |-> 1 <- 2, 3, 4
            |   |-> 2 <- 0, 3, 4
            |   |   |-> 3 <- 0, 1, 4
            |   |   |   |-> 4 <- 0, 1, 2
            |   |   |   |   L->  ...
            |   |   |   L->  ...
            |   |   L->  ...
            |   L->  ...
            L->  ...
        --- undirected case ---
        +-- 0
            |-- 1
            |   |-- 2 - 0
            |   |   |-- 3 - 0, 1
            |   |   |   L-- 4 - 0, 1, 2
            |   |   L--  ...
            |   L--  ...
            L--  ...
        """
    ).strip()
    assert target == text


def test_graph_str_with_labels():
    graph = nx.generators.complete_graph(5, create_using=nx.DiGraph)
    for n in graph.nodes:
        graph.nodes[n]["label"] = f"Node(n={n})"
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write, with_labels=True, ascii_only=False)
    text = "\n".join(lines)
    print(text)
    # Non trees with labels can get somewhat out of hand with graph_str
    # because we need to immediately show every non-tree edge to the right
    target = dedent(
        """
        ╙── Node(n=0) ╾ Node(n=1), Node(n=2), Node(n=3), Node(n=4)
            ├─╼ Node(n=1) ╾ Node(n=2), Node(n=3), Node(n=4)
            │   ├─╼ Node(n=2) ╾ Node(n=0), Node(n=3), Node(n=4)
            │   │   ├─╼ Node(n=3) ╾ Node(n=0), Node(n=1), Node(n=4)
            │   │   │   ├─╼ Node(n=4) ╾ Node(n=0), Node(n=1), Node(n=2)
            │   │   │   │   └─╼  ...
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        """
    ).strip()
    assert target == text


def test_graph_str_complete_graphs():
    lines = []
    write = lines.append
    for k in [0, 1, 2, 3, 4, 5]:
        g = nx.generators.complete_graph(k)
        write(f"--- undirected k={k} ---")
        nx.graph_str(g, write=write)

    for k in [0, 1, 2, 3, 4, 5]:
        g = nx.generators.complete_graph(k, nx.DiGraph)
        write(f"--- directed k={k} ---")
        nx.graph_str(g, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        --- undirected k=0 ---
        ╙
        --- undirected k=1 ---
        ╙── 0
        --- undirected k=2 ---
        ╙── 0
            └── 1
        --- undirected k=3 ---
        ╙── 0
            ├── 1
            │   └── 2 ─ 0
            └──  ...
        --- undirected k=4 ---
        ╙── 0
            ├── 1
            │   ├── 2 ─ 0
            │   │   └── 3 ─ 0, 1
            │   └──  ...
            └──  ...
        --- undirected k=5 ---
        ╙── 0
            ├── 1
            │   ├── 2 ─ 0
            │   │   ├── 3 ─ 0, 1
            │   │   │   └── 4 ─ 0, 1, 2
            │   │   └──  ...
            │   └──  ...
            └──  ...
        --- directed k=0 ---
        ╙
        --- directed k=1 ---
        ╙── 0
        --- directed k=2 ---
        ╙── 0 ╾ 1
            └─╼ 1
                └─╼  ...
        --- directed k=3 ---
        ╙── 0 ╾ 1, 2
            ├─╼ 1 ╾ 2
            │   ├─╼ 2 ╾ 0
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- directed k=4 ---
        ╙── 0 ╾ 1, 2, 3
            ├─╼ 1 ╾ 2, 3
            │   ├─╼ 2 ╾ 0, 3
            │   │   ├─╼ 3 ╾ 0, 1
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        --- directed k=5 ---
        ╙── 0 ╾ 1, 2, 3, 4
            ├─╼ 1 ╾ 2, 3, 4
            │   ├─╼ 2 ╾ 0, 3, 4
            │   │   ├─╼ 3 ╾ 0, 1, 4
            │   │   │   ├─╼ 4 ╾ 0, 1, 2
            │   │   │   │   └─╼  ...
            │   │   │   └─╼  ...
            │   │   └─╼  ...
            │   └─╼  ...
            └─╼  ...
        """
    ).strip()
    assert target == text


def test_graph_str_multiple_sources():
    g = nx.DiGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 5)
    g.add_edge(3, 6)
    g.add_edge(5, 4)
    g.add_edge(4, 1)
    g.add_edge(1, 5)
    lines = []
    write = lines.append
    # Use each node as the starting point to demonstrate how the representation
    # changes.
    nodes = sorted(g.nodes())
    for n in nodes:
        write(f"--- source node: {n} ---")
        nx.graph_str(g, write=write, sources=[n])
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        --- source node: 1 ---
        ╙── 1 ╾ 4
            ├─╼ 2
            │   └─╼ 4 ╾ 5
            │       └─╼  ...
            ├─╼ 3
            │   ├─╼ 5 ╾ 1
            │   │   └─╼  ...
            │   └─╼ 6
            └─╼  ...
        --- source node: 2 ---
        ╙── 2 ╾ 1
            └─╼ 4 ╾ 5
                └─╼ 1
                    ├─╼ 3
                    │   ├─╼ 5 ╾ 1
                    │   │   └─╼  ...
                    │   └─╼ 6
                    └─╼  ...
        --- source node: 3 ---
        ╙── 3 ╾ 1
            ├─╼ 5 ╾ 1
            │   └─╼ 4 ╾ 2
            │       └─╼ 1
            │           ├─╼ 2
            │           │   └─╼  ...
            │           └─╼  ...
            └─╼ 6
        --- source node: 4 ---
        ╙── 4 ╾ 2, 5
            └─╼ 1
                ├─╼ 2
                │   └─╼  ...
                ├─╼ 3
                │   ├─╼ 5 ╾ 1
                │   │   └─╼  ...
                │   └─╼ 6
                └─╼  ...
        --- source node: 5 ---
        ╙── 5 ╾ 3, 1
            └─╼ 4 ╾ 2
                └─╼ 1
                    ├─╼ 2
                    │   └─╼  ...
                    ├─╼ 3
                    │   ├─╼ 6
                    │   └─╼  ...
                    └─╼  ...
        --- source node: 6 ---
        ╙── 6 ╾ 3
        """
    ).strip()
    assert target == text


def test_graph_str_star_graph():
    graph = nx.star_graph(5, create_using=nx.Graph)
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╙── 1
            └── 0
                ├── 2
                ├── 3
                ├── 4
                └── 5
        """
    ).strip()
    assert target == text


def test_graph_str_path_graph():
    graph = nx.path_graph(3, create_using=nx.Graph)
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╙── 0
            └── 1
                └── 2
        """
    ).strip()
    assert target == text


def test_graph_str_lollipop_graph():
    graph = nx.lollipop_graph(4, 2, create_using=nx.Graph)
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╙── 5
            └── 4
                └── 3
                    ├── 0
                    │   ├── 1 ─ 3
                    │   │   └── 2 ─ 0, 3
                    │   └──  ...
                    └──  ...
        """
    ).strip()
    assert target == text


def test_graph_str_wheel_graph():
    graph = nx.wheel_graph(7, create_using=nx.Graph)
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╙── 1
            ├── 0
            │   ├── 2 ─ 1
            │   │   └── 3 ─ 0
            │   │       └── 4 ─ 0
            │   │           └── 5 ─ 0
            │   │               └── 6 ─ 0, 1
            │   └──  ...
            └──  ...
        """
    ).strip()
    assert target == text


def test_graph_str_circular_ladder_graph():
    graph = nx.circular_ladder_graph(4, create_using=nx.Graph)
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╙── 0
            ├── 1
            │   ├── 2
            │   │   ├── 3 ─ 0
            │   │   │   └── 7
            │   │   │       ├── 6 ─ 2
            │   │   │       │   └── 5 ─ 1
            │   │   │       │       └── 4 ─ 0, 7
            │   │   │       └──  ...
            │   │   └──  ...
            │   └──  ...
            └──  ...
        """
    ).strip()
    assert target == text


def test_graph_str_dorogovtsev_goltsev_mendes_graph():
    graph = nx.dorogovtsev_goltsev_mendes_graph(4, create_using=nx.Graph)
    lines = []
    write = lines.append
    nx.graph_str(graph, write=write)
    text = "\n".join(lines)
    print(text)
    target = dedent(
        """
        ╙── 15
            ├── 0
            │   ├── 1 ─ 15
            │   │   ├── 2 ─ 0
            │   │   │   ├── 4 ─ 0
            │   │   │   │   ├── 9 ─ 0
            │   │   │   │   │   ├── 22 ─ 0
            │   │   │   │   │   └── 38 ─ 4
            │   │   │   │   ├── 13 ─ 2
            │   │   │   │   │   ├── 34 ─ 2
            │   │   │   │   │   └── 39 ─ 4
            │   │   │   │   ├── 18 ─ 0
            │   │   │   │   ├── 30 ─ 2
            │   │   │   │   └──  ...
            │   │   │   ├── 5 ─ 1
            │   │   │   │   ├── 12 ─ 1
            │   │   │   │   │   ├── 29 ─ 1
            │   │   │   │   │   └── 40 ─ 5
            │   │   │   │   ├── 14 ─ 2
            │   │   │   │   │   ├── 35 ─ 2
            │   │   │   │   │   └── 41 ─ 5
            │   │   │   │   ├── 25 ─ 1
            │   │   │   │   ├── 31 ─ 2
            │   │   │   │   └──  ...
            │   │   │   ├── 7 ─ 0
            │   │   │   │   ├── 20 ─ 0
            │   │   │   │   └── 32 ─ 2
            │   │   │   ├── 10 ─ 1
            │   │   │   │   ├── 27 ─ 1
            │   │   │   │   └── 33 ─ 2
            │   │   │   ├── 16 ─ 0
            │   │   │   ├── 23 ─ 1
            │   │   │   └──  ...
            │   │   ├── 3 ─ 0
            │   │   │   ├── 8 ─ 0
            │   │   │   │   ├── 21 ─ 0
            │   │   │   │   └── 36 ─ 3
            │   │   │   ├── 11 ─ 1
            │   │   │   │   ├── 28 ─ 1
            │   │   │   │   └── 37 ─ 3
            │   │   │   ├── 17 ─ 0
            │   │   │   ├── 24 ─ 1
            │   │   │   └──  ...
            │   │   ├── 6 ─ 0
            │   │   │   ├── 19 ─ 0
            │   │   │   └── 26 ─ 1
            │   │   └──  ...
            │   └──  ...
            └──  ...
        """
    ).strip()
    assert target == text
