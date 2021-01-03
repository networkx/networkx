r""" This module provides functions and operations for bipartite
graphs.  Bipartite graphs `B = (U, V, E)` have two node sets `U,V` and edges in
`E` that only connect nodes from opposite sets. It is common in the literature
to use an spatial analogy referring to the two node sets as top and bottom nodes.

The bipartite algorithms are not imported into the networkx namespace
at the top level so the easiest way to use them is with:

>>> from networkx.algorithms import bipartite

NetworkX does not have a custom bipartite graph class but the Graph()
or DiGraph() classes can be used to represent bipartite graphs. However,
you have to keep track of which set each node belongs to, and make
sure that there is no edge between nodes of the same set. The convention used
in NetworkX is to use a node attribute named `bipartite` with values 0 or 1 to
identify the sets each node belongs to. This convention is not enforced in
the source code of bipartite functions, it's only a recommendation.

For example:

>>> B = nx.Graph()
>>> # Add nodes with the node attribute "bipartite"
>>> B.add_nodes_from([1, 2, 3, 4], bipartite=0)
>>> B.add_nodes_from(["a", "b", "c"], bipartite=1)
>>> # Add edges only between nodes of opposite node sets
>>> B.add_edges_from([(1, "a"), (1, "b"), (2, "b"), (2, "c"), (3, "c"), (4, "a")])

Many algorithms of the bipartite module of NetworkX require, as an argument, a
container with all the nodes that belong to one set, in addition to the bipartite
graph `B`. The functions in the bipartite package do not check that the node set
is actually correct nor that the input graph is actually bipartite.
If `B` is connected, you can find the two node sets using a two-coloring
algorithm:

>>> nx.is_connected(B)
True
>>> bottom_nodes, top_nodes = bipartite.sets(B)

However, if the input graph is not connected, there are more than one possible
colorations. This is the reason why we require the user to pass a container
with all nodes of one bipartite node set as an argument to most bipartite
functions. In the face of ambiguity, we refuse the temptation to guess and
raise an :exc:`AmbiguousSolution <networkx.AmbiguousSolution>`
Exception if the input graph for
:func:`bipartite.sets <networkx.algorithms.bipartite.basic.sets>`
is disconnected.

Using the `bipartite` node attribute, you can easily get the two node sets:

>>> top_nodes = {n for n, d in B.nodes(data=True) if d["bipartite"] == 0}
>>> bottom_nodes = set(B) - top_nodes

So you can easily use the bipartite algorithms that require, as an argument, a
container with all nodes that belong to one node set:

>>> print(round(bipartite.density(B, bottom_nodes), 2))
0.5
>>> G = bipartite.projected_graph(B, top_nodes)

All bipartite graph generators in NetworkX build bipartite graphs with the
`bipartite` node attribute. Thus, you can use the same approach:

>>> RB = bipartite.random_graph(5, 7, 0.2)
>>> RB_top = {n for n, d in RB.nodes(data=True) if d["bipartite"] == 0}
>>> RB_bottom = set(RB) - RB_top
>>> list(RB_top)
[0, 1, 2, 3, 4]
>>> list(RB_bottom)
[5, 6, 7, 8, 9, 10, 11]

For other bipartite graph generators see
:mod:`Generators <networkx.algorithms.bipartite.generators>`.

"""
__private__ = ["tests"]


def lazy_import(module_name, submodules, submod_attrs):
    import sys
    import importlib
    import importlib.util

    all_funcs = []
    for mod, funcs in submod_attrs.items():
        all_funcs.extend(funcs)
    name_to_submod = {
        func: mod for mod, funcs in submod_attrs.items() for func in funcs
    }

    def require(fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        spec = importlib.util.find_spec(fullname)
        try:
            module = importlib.util.module_from_spec(spec)
        except Exception:
            raise ImportError(
                "Could not lazy import module {fullname}".format(fullname=fullname)
            ) from None
        loader = importlib.util.LazyLoader(spec.loader)
        sys.modules[fullname] = module
        loader.exec_module(module)
        return module

    def __getattr__(name):
        if name in submodules:
            fullname = "{module_name}.{name}".format(module_name=module_name, name=name)
            attr = require(fullname)
        elif name in name_to_submod:
            modname = name_to_submod[name]
            module = importlib.import_module(
                "{module_name}.{modname}".format(
                    module_name=module_name, modname=modname
                )
            )
            attr = getattr(module, name)
        else:
            raise AttributeError(
                "No {module_name} attribute {name}".format(
                    module_name=module_name, name=name
                )
            )
        globals()[name] = attr
        return attr

    return __getattr__


__getattr__ = lazy_import(
    __name__,
    submodules={
        "basic",
        "centrality",
        "cluster",
        "covering",
        "edgelist",
        "generators",
        "matching",
        "matrix",
        "projection",
        "redundancy",
        "spectral",
        "tests",
    },
    submod_attrs={
        "basic": [
            "color",
            "degrees",
            "density",
            "is_bipartite",
            "is_bipartite_node_set",
            "sets",
        ],
        "centrality": [
            "betweenness_centrality",
            "closeness_centrality",
            "degree_centrality",
        ],
        "cluster": [
            "average_clustering",
            "clustering",
            "latapy_clustering",
            "robins_alexander_clustering",
        ],
        "covering": [
            "min_edge_cover",
        ],
        "edgelist": [
            "generate_edgelist",
            "parse_edgelist",
            "read_edgelist",
            "write_edgelist",
        ],
        "generators": [
            "alternating_havel_hakimi_graph",
            "complete_bipartite_graph",
            "configuration_model",
            "gnmk_random_graph",
            "havel_hakimi_graph",
            "preferential_attachment_graph",
            "random_graph",
            "reverse_havel_hakimi_graph",
        ],
        "matching": [
            "eppstein_matching",
            "hopcroft_karp_matching",
            "maximum_matching",
            "minimum_weight_full_matching",
            "to_vertex_cover",
        ],
        "matrix": [
            "biadjacency_matrix",
            "from_biadjacency_matrix",
        ],
        "projection": [
            "collaboration_weighted_projected_graph",
            "generic_weighted_projected_graph",
            "overlap_weighted_projected_graph",
            "project",
            "projected_graph",
            "weighted_projected_graph",
        ],
        "redundancy": [
            "node_redundancy",
        ],
        "spectral": [
            "spectral_bipartivity",
        ],
    },
)


def __dir__():
    return __all__


__all__ = [
    "alternating_havel_hakimi_graph",
    "average_clustering",
    "basic",
    "betweenness_centrality",
    "biadjacency_matrix",
    "centrality",
    "closeness_centrality",
    "cluster",
    "clustering",
    "collaboration_weighted_projected_graph",
    "color",
    "complete_bipartite_graph",
    "configuration_model",
    "covering",
    "degree_centrality",
    "degrees",
    "density",
    "edgelist",
    "eppstein_matching",
    "from_biadjacency_matrix",
    "generate_edgelist",
    "generators",
    "generic_weighted_projected_graph",
    "gnmk_random_graph",
    "havel_hakimi_graph",
    "hopcroft_karp_matching",
    "is_bipartite",
    "is_bipartite_node_set",
    "latapy_clustering",
    "matching",
    "matrix",
    "maximum_matching",
    "min_edge_cover",
    "minimum_weight_full_matching",
    "node_redundancy",
    "overlap_weighted_projected_graph",
    "parse_edgelist",
    "preferential_attachment_graph",
    "project",
    "projected_graph",
    "projection",
    "random_graph",
    "read_edgelist",
    "redundancy",
    "reverse_havel_hakimi_graph",
    "robins_alexander_clustering",
    "sets",
    "spectral",
    "spectral_bipartivity",
    "tests",
    "to_vertex_cover",
    "weighted_projected_graph",
    "write_edgelist",
]
