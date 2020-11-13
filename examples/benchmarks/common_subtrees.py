from networkx.utils import create_py_random_state
import networkx as nx
from networkx.algorithms.minors import maximum_common_ordered_subtree_embedding
from networkx.algorithms.minors.tree_isomorphism import (
    maximum_common_ordered_subtree_isomorphism,
)


def find_shared_structure(tree1, tree2, style, impl="auto", item_type="auto"):
    if style == "embedding":
        s1, s2, value = maximum_common_ordered_subtree_embedding(
            tree1, tree2, impl=impl, item_type=item_type
        )
    elif style == "isomorphism":
        s1, s2, value = maximum_common_ordered_subtree_isomorphism(
            tree1, tree2, impl=impl, item_type=item_type
        )
    else:
        return KeyError(style)
    return s1, s2, value


def benchmark():
    import itertools as it

    def make_grid_from_basis(basis):
        return [dict(zip(basis.keys(), vals)) for vals in it.product(*basis.values())]

    data_basis = {
        "common": [10, 100, 200, 500],
    }
    algo_basis = {
        "style": ["embedding", "isomorphism"],
        "impl": ["iter", "recurse", "iter-cython"],
    }
    data_grid = make_grid_from_basis(data_basis)
    algo_basis = make_grid_from_basis(algo_basis)

    import timerit
    import ubelt as ub

    ti = timerit.Timerit(1, bestof=1, verbose=2)

    results = []
    for datakw in data_grid:
        for algokw in algo_basis:
            runkw = {**datakw, **algokw}
            run_key = ub.repr2(
                runkw,
                sep="",
                itemsep="",
                kvsep="",
                explicit=1,
                nobr=1,
                nl=0,
                precision=1,
            )
            tree1, tree2 = random_shared_structure_trees(**datakw)
            try:
                for timer in ti.reset(run_key):
                    with timer:
                        s1, s2, v = find_shared_structure(tree1, tree2, **algokw)
            except RecursionError as ex:
                print("ex = {!r}".format(ex))
                row = runkw.copy()
                row["time"] = float("nan")
            else:
                row = runkw.copy()
                row["time"] = ti.min()
            results.append(row)

    # Display results
    print(ub.repr2(ub.sorted_vals(ti.measures["min"]), nl=1, align=":", precision=6))


def random_shared_structure_trees(common, p_contract=0.2, p_expand=0.2, seed=None):
    """
    Builds two forests such that they share some degree of common structure.

    Parameters
    ----------

    common : int
        The size of the initial shared structure

    p_contract : float
        Probability of contracting an edge in the common structure in each tree

    seed:
        Random state or seed

    Examples
    --------
    >>> seed = 0
    >>> common = 10
    >>> p_contract = 0.2
    >>> tree1, tree2 = random_shared_structure_trees(common=20, seed=0)
    >>> print(nx.forest_str(tree1))
    >>> print(nx.forest_str(tree2))

    """
    rng = create_py_random_state(seed)
    common_tree = nx.random_graphs.random_ordered_tree(common, seed=rng, directed=True)

    common1 = common_tree.copy()
    common2 = common_tree.copy()

    to_contract1 = [edge for edge in common1.edges if rng.random() < p_contract]
    to_contract2 = [edge for edge in common2.edges if rng.random() < p_contract]

    tree1 = ditree_contract_edges(common1, to_contract1)
    tree2 = ditree_contract_edges(common2, to_contract2)

    inner_expand_size = (1, 5)
    prefix_expand_size = (1, 10)
    suffix_expand_size = (1, 10)

    base = common + 100
    tree1, base = expand_inner(tree1, p_expand, inner_expand_size, rng, base)
    tree2, base = expand_inner(tree2, p_expand, inner_expand_size, rng, base)

    tree1, base = expand_prefix(tree1, prefix_expand_size, rng, base)
    tree2, base = expand_prefix(tree2, prefix_expand_size, rng, base)

    tree1, base = expand_suffix(tree1, suffix_expand_size, rng, base)
    tree2, base = expand_suffix(tree2, suffix_expand_size, rng, base)

    if 0:
        print(nx.forest_str(common_tree))
        print(nx.forest_str(tree1))
        print(nx.forest_str(tree2))

    return tree1, tree2


def _coerce_rv(rv, rng):
    if isinstance(rv, tuple):

        def rv_sample():
            return rng.randint(*rv)

    else:

        def rv_sample():
            return rv

    return rv_sample


def expand_prefix(graph, prefix_expand_size, rng, base):
    sources = [n for n in graph.nodes if graph.in_degree[n] == 0]
    _get_size = _coerce_rv(prefix_expand_size, rng)

    for node in sources:
        insert_size = _get_size()
        to_insert = nx.random_graphs.random_ordered_tree(
            insert_size, seed=rng, directed=True
        )
        to_insert = rebase_nodes(to_insert, base=base)
        graph = ditree_splice_in(graph, (node, node), to_insert)
        base += len(to_insert)
    return graph, base


def expand_suffix(graph, suffix_expand_size, rng, base):
    sinks = [n for n in graph.nodes if graph.out_degree[n] == 0]
    _get_size = _coerce_rv(suffix_expand_size, rng)

    for node in sinks:
        insert_size = _get_size()
        to_insert = nx.random_graphs.random_ordered_tree(
            insert_size, seed=rng, directed=True
        )
        to_insert = rebase_nodes(to_insert, base=base)
        graph = ditree_splice_in(graph, (node, node), to_insert)
        base += len(to_insert)
    return graph, base


def expand_inner(graph, p_expand, inner_expand_size, rng, base):
    _get_size = _coerce_rv(inner_expand_size, rng)

    sources = [n for n in graph.nodes if graph.in_degree[n] == 0]
    ordered_edges = []
    for source in sources:
        ordered_edges += [
            (u, v)
            for u, v, etype in list(nx.dfs_labeled_edges(graph, source=source))
            if etype == "forward" and u != v
        ]

    for edge in ordered_edges[::-1]:
        if rng.random() < p_expand:
            if graph.has_edge(*edge):
                insert_size = _get_size()

                if insert_size > 0:
                    to_insert = nx.random_graphs.random_ordered_tree(
                        insert_size, seed=rng, directed=True
                    )
                    to_insert = rebase_nodes(to_insert, base=base)
                    graph = ditree_splice_in(graph, edge, to_insert)
                    base += len(to_insert)
    return graph, base


def rebase_nodes(graph, base):
    mapping = {n: idx for idx, n in enumerate(graph.nodes, start=base)}
    return nx.relabel_nodes(graph, mapping)


def ditree_splice_in(graph, edge, to_insert):
    sources = [n for n in to_insert.nodes if to_insert.in_degree[n] == 0]
    sinks = [n for n in to_insert.nodes if to_insert.out_degree[n] == 0]
    source = sources[0]
    sink = sinks[0]
    u, v = edge
    if u != v:
        graph.remove_edge(u, v)
        graph.add_edge(u, source)
        graph.add_edge(sink, v)
    else:
        if graph.in_degree[u] == 0:
            graph.add_edge(sink, u)
        elif graph.out_degree[u] == 0:
            graph.add_edge(v, source)
        else:
            raise AssertionError
    graph.add_edges_from(to_insert.edges)
    return graph


def ditree_contract_edges(graph, to_contract):
    # Order edges such that we can iteratively remove them without conflict
    sources = [n for n in graph.nodes if graph.in_degree[n] == 0]
    ordered_edges = []
    for source in sources:
        ordered_edges += [
            (u, v)
            for u, v, etype in list(nx.dfs_labeled_edges(graph, source=source))
            if etype == "forward" and u != v
        ]
    lut = {edge: idx for idx, edge in enumerate(ordered_edges)}
    to_contract = sorted(to_contract, key=lambda edge: lut[edge], reverse=True)

    contracted = graph.copy()
    for u, v in to_contract:
        nx.contracted_nodes(contracted, u, v, copy=False, self_loops=False)
    return contracted
