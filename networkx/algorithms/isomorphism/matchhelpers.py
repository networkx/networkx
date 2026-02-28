"""Functions which help end users define customize node_match and
edge_match functions to use during isomorphism checks.
"""
import itertools
import math
import types

import networkx as nx

__all__ = [
    "node_match_to_label",
    "edge_match_to_label",
    "categorical_node_match",
    "categorical_edge_match",
    "categorical_multiedge_match",
    "numerical_node_match",
    "numerical_edge_match",
    "numerical_multiedge_match",
    "generic_node_match",
    "generic_edge_match",
    "generic_multiedge_match",
]


def node_match_to_label(node_match, Glist, attrname):
    """Use the `node_match` function to set node labels for all graphs in `Glist`

    The `node_match` function takes a pair of node datadicts and returns `True`
    if the nodes are considered matched in the sense of isomorphism. This function
    calls `node_match` to determine which groups of nodes all match each other.
    Those nodes are given an integer label, unique across all graphs in Glist.
    The node attribute `attrname` is created/updated in each graph to store the labels.
    Node labels are equal iff the corresponding nodes match across all graphs in Glist.

    The `node_match` function must be commutative and transitive across all graphs
    (if a node matches with 2 other nodes, then the two other nodes must match).

    The intent of this function is to ease transition from the match-function
    framework of the isomorphism checkers to a match-by-label framework
    implemented in the VF2pp tools.

    This will work for multiedge_match functions as well as edge_match functions.

    The labels used are integers. If other labels are desired, consider manipulating
    the returned dict keyed by labels to cannonical datadicts for that group of nodes
    to determine replacement labels and then get/set a node attribute in each graph.

    Parameters
    ==========
    node_match : callable
        A function that returns True if node n1 in G1 and n2 in G2 should
        be considered equal during the isomorphism test.

        The function will be called like

           node_match(G1.nodes[n1], G2.nodes[n2]).

        That is, the function will receive the node attribute dictionaries
        for n1 and n2 as inputs.

    Glist : NetworkX graph or list of NetworkX graphs
        A single graph or list of graphs for which the labels are computed

    attrname : attribute name
        The name of the node attribute to be set to the node label.

    Returns
    =======
    cannonical_datadicts_by_label : dict
        A dict keyed to a single datadict that represents all nodes with that label.
        The datadict matches all node datadicts with that label in all graphs.

    Examples
    ========
    >>> iso = nx.isomorphism
    >>> def node_match(d1, d2): return d1["tint"] == d2["tint"] and d1["hue"] == d2["hue"]

    >>> G = nx.path_graph(4)
    >>> H = G.copy()
    >>> nx.set_node_attributes(G, {n: "lt" if n > 1 else "dk" for n in G}, "tint")
    >>> nx.set_node_attributes(G, {n: "blue" if n % 2 else "red" for n in G}, "hue")
    >>> nx.set_node_attributes(H, {n: "lt" if n < 2 else "dk" for n in H}, "tint")
    >>> nx.set_node_attributes(H, {n: "blue" if n % 2 else "red" for n in H}, "hue")
    >>> H.add_node(4, tint="lt", hue="purple")

    >>> lbl_dds = iso.node_match_to_label(node_match, [G, H], "label")
    >>> nx.get_node_attributes(G, "label")
    {0: 0, 1: 1, 2: 2, 3: 3}
    >>> nx.get_node_attributes(H, "label")
    {0: 2, 1: 3, 2: 0, 3: 1, 4: 4}

    If you want to relabel the nodes to more meaningful labels, you can use the
    lbl_dds to construct such labels

    >>> relabel = {lbl: f"{dd['tint']} {dd['hue']}" for lbl, dd in lbl_dds.items()}
    >>> Grelabels = {n: relabel[lbl] for n, lbl in G.nodes.data("label")}
    >>> Grelabels
    {0: 'dk red', 1: 'dk blue', 2: 'lt red', 3: 'lt blue'}

    See Also
    ========
    edge_match_to_label
    """
    if hasattr(Glist, "adj"):
        Glist = [Glist]
    new_label = itertools.count()
    labels = {}
    ddict_by_label = {}
    for G in Glist:
        for node in G:
            ddn = G.nodes[node]
            for lbl, dd in ddict_by_label.items():
                if node_match(ddn, dd):
                    break
            else:
                lbl = next(new_label)
                ddict_by_label[lbl] = ddn
            ddn[attrname] = lbl
    return ddict_by_label


def edge_match_to_label(edge_match, Glist, attrname):
    """Use the `edge_match` function to set edge labels for all graphs in `Glist`

    The `edge_match` function takes a pair of edge datadicts and returns `True`
    if the edges are considered matched in the sense of isomorphism. This function
    calls `edge_match` to determine which groups of edges all match each other.
    Those edges are given an integer label, unique across all graphs in Glist.
    The edge attribute `attrname` is created/updated in each graph to store the labels.
    Edge labels are equal iff the corresponding edges match across all graphs in Glist.

    The `edge_match` function takes a pair of edge datadicts and returns `True`
    if the edges are match in the sense of isomorphism. This function calls
    `edge_match` to determine which groups of edges all match each other.
    Those edges are given an integer label, unique across all graphs in Glist.
    The returned list of `label_dicts` correspond to each graph in Glist and
    provide the label for each edge in that graph. Those dicts are precisely
    what is needed for `nx.set_edge_attributes`. If the `attrname` is provided,
    edge attributes with that name are added to each graph with the label as value.
    Edge labels are equal iff the corresponding edges match across all graphs in Glist.

    The `edge_match` function must be commutative and transitive across all graphs
    (if a edge matches with 2 other edges, then the two other edges must match).

    The intent of this function is to ease transition from the match-function
    framework of the isomorphism checkers to a match-by-label framework
    implemented in the VF2pp tools.

    This will work for multiedge_match functions as well as edge_match functions.

    The labels used are integers. If other labels are desired, consider manipulating
    the returned dict keyed by labels to cannonical datadicts for that group of edges
    to determine replacement labels and then get/set a edge attribute in each graph.

    Parameters
    ==========
    edge_match : callable
        A function that returns True if the edge attribute dictionary
        for the pair of nodes (u1, v1) in G1 and (u2, v2) in G2 should
        be considered equal during the isomorphism test.

        The function will be called like

           edge_match(G1[u1][v1], G2[u2][v2]).

        That is, the function will receive the edge attribute dictionaries
        of the edges under consideration.

    Glist : NetworkX graph or list of NetworkX graphs
        A single graph or a list of graphs for which the labels are computed

    attrname : string or None (default: None)
        The name of the edge attribute in each graph to be set.

    Returns
    =======
    cannonical_datadicts_by_label : dict
        A dict keyed to a single datadict that represents all edges with that label.
        The datadict matches all edge datadicts with that label in all graphs.

    Examples
    ========
    >>> iso = nx.isomorphism
    >>> set_ea = nx.set_edge_attributes
    >>> def edge_match(d1, d2): return d1["tint"] == d2["tint"] and d1["hue"] == d2["hue"]

    >>> G = nx.path_graph(5)
    >>> H = G.copy()
    >>> set_ea(G, {e: "lt" if sum(e) > 4 else "dk" for e in G.edges}, "tint")
    >>> set_ea(G, {e: "blue" if sum(e) in (3, 7) else "red" for e in G.edges}, "hue")
    >>> set_ea(H, {e: "lt" if sum(e) < 4 else "dk" for e in H.edges}, "tint")
    >>> set_ea(H, {e: "blue" if sum(e) in (3, 7) else "red" for e in H.edges}, "hue")
    >>> H.add_edge(6, 7, tint="lt", hue="purple")

    >>> lbl_dds = iso.edge_match_to_label(edge_match, [G, H], "label")
    >>> nx.get_edge_attributes(G, "label")
    {(0, 1): 0, (1, 2): 1, (2, 3): 2, (3, 4): 3}
    >>> nx.get_edge_attributes(H, "label")
    {(0, 1): 2, (1, 2): 3, (2, 3): 0, (3, 4): 1, (6, 7): 4}

    If you want to relabel the edges to more meaningful labels, you can use the
    lbl_dds to construct such labels

    >>> relabel = {lbl: f"{dd['tint']} {dd['hue']}" for lbl, dd in lbl_dds.items()}
    >>> Grelabels = {(u, v): relabel[lbl] for u, v, lbl in G.edges.data("label")}
    >>> Grelabels
    {(0, 1): 'dk red', (1, 2): 'dk blue', (2, 3): 'lt red', (3, 4): 'lt blue'}

    See Also
    ========
    node_match_to_label
    """
    if hasattr(Glist, "adj"):
        Glist = [Glist]
    new_label = itertools.count()
    labels = {}
    ddict_by_label = {}
    for G in Glist:
        for edge in G.edges:
            ddn = G.edges[edge]
            for lbl, dd in ddict_by_label.items():
                if edge_match(ddn, dd):
                    break
            else:
                lbl = next(new_label)
                ddict_by_label[lbl] = ddn
            ddn[attrname] = lbl
    return ddict_by_label


def copyfunc(f, name=None):
    """Returns a deepcopy of a function."""
    return types.FunctionType(
        f.__code__, f.__globals__, name or f.__name__, f.__defaults__, f.__closure__
    )


def allclose(x, y, rtol=1.0000000000000001e-05, atol=1e-08):
    """Returns True if x and y are sufficiently close, elementwise.

    Parameters
    ----------
    rtol : float
        The relative error tolerance.
    atol : float
        The absolute error tolerance.

    """
    # assume finite weights, see numpy.allclose() for reference
    return all(math.isclose(xi, yi, rel_tol=rtol, abs_tol=atol) for xi, yi in zip(x, y))


categorical_doc = """
Returns a comparison function for a categorical node attribute.

The value(s) of the attr(s) must be hashable and comparable via the ==
operator since they are placed into a set([]) object.  If the sets from
G1 and G2 are the same, then the constructed function returns True.

Parameters
----------
attr : string | list
    The categorical node attribute to compare, or a list of categorical
    node attributes to compare.
default : value | list
    The default value for the categorical node attribute, or a list of
    default values for the categorical node attributes.

Returns
-------
match : function
    The customized, categorical `node_match` function.

Examples
--------
>>> import networkx.algorithms.isomorphism as iso
>>> nm = iso.categorical_node_match("size", 1)
>>> nm = iso.categorical_node_match(["color", "size"], ["red", 2])

"""


def categorical_node_match(attr, default):
    if isinstance(attr, str):

        def match(data1, data2):
            return data1.get(attr, default) == data2.get(attr, default)

    else:
        attrs = list(zip(attr, default))  # Python 3

        def match(data1, data2):
            return all(data1.get(attr, d) == data2.get(attr, d) for attr, d in attrs)

    return match


categorical_edge_match = copyfunc(categorical_node_match, "categorical_edge_match")


def categorical_multiedge_match(attr, default):
    if isinstance(attr, str):

        def match(datasets1, datasets2):
            values1 = {data.get(attr, default) for data in datasets1.values()}
            values2 = {data.get(attr, default) for data in datasets2.values()}
            return values1 == values2

    else:
        attrs = list(zip(attr, default))  # Python 3

        def match(datasets1, datasets2):
            values1 = set()
            for data1 in datasets1.values():
                x = tuple(data1.get(attr, d) for attr, d in attrs)
                values1.add(x)
            values2 = set()
            for data2 in datasets2.values():
                x = tuple(data2.get(attr, d) for attr, d in attrs)
                values2.add(x)
            return values1 == values2

    return match


# Docstrings for categorical functions.
categorical_node_match.__doc__ = categorical_doc
categorical_edge_match.__doc__ = categorical_doc.replace("node", "edge")
tmpdoc = categorical_doc.replace("node", "edge")
tmpdoc = tmpdoc.replace("categorical_edge_match", "categorical_multiedge_match")
categorical_multiedge_match.__doc__ = tmpdoc


numerical_doc = """
Returns a comparison function for a numerical node attribute.

The value(s) of the attr(s) must be numerical and sortable.  If the
sorted list of values from G1 and G2 are the same within some
tolerance, then the constructed function returns True.

Parameters
----------
attr : string | list
    The numerical node attribute to compare, or a list of numerical
    node attributes to compare.
default : value | list
    The default value for the numerical node attribute, or a list of
    default values for the numerical node attributes.
rtol : float
    The relative error tolerance.
atol : float
    The absolute error tolerance.

Returns
-------
match : function
    The customized, numerical `node_match` function.

Examples
--------
>>> import networkx.algorithms.isomorphism as iso
>>> nm = iso.numerical_node_match("weight", 1.0)
>>> nm = iso.numerical_node_match(["weight", "linewidth"], [0.25, 0.5])

"""


def numerical_node_match(attr, default, rtol=1.0000000000000001e-05, atol=1e-08):
    if isinstance(attr, str):

        def match(data1, data2):
            return math.isclose(
                data1.get(attr, default),
                data2.get(attr, default),
                rel_tol=rtol,
                abs_tol=atol,
            )

    else:
        attrs = list(zip(attr, default))  # Python 3

        def match(data1, data2):
            values1 = [data1.get(attr, d) for attr, d in attrs]
            values2 = [data2.get(attr, d) for attr, d in attrs]
            return allclose(values1, values2, rtol=rtol, atol=atol)

    return match


numerical_edge_match = copyfunc(numerical_node_match, "numerical_edge_match")


def numerical_multiedge_match(attr, default, rtol=1.0000000000000001e-05, atol=1e-08):
    if isinstance(attr, str):

        def match(datasets1, datasets2):
            values1 = sorted(data.get(attr, default) for data in datasets1.values())
            values2 = sorted(data.get(attr, default) for data in datasets2.values())
            return allclose(values1, values2, rtol=rtol, atol=atol)

    else:
        attrs = list(zip(attr, default))  # Python 3

        def match(datasets1, datasets2):
            values1 = []
            for data1 in datasets1.values():
                x = tuple(data1.get(attr, d) for attr, d in attrs)
                values1.append(x)
            values2 = []
            for data2 in datasets2.values():
                x = tuple(data2.get(attr, d) for attr, d in attrs)
                values2.append(x)
            values1.sort()
            values2.sort()
            for xi, yi in zip(values1, values2):
                if not allclose(xi, yi, rtol=rtol, atol=atol):
                    return False
            else:
                return True

    return match


# Docstrings for numerical functions.
numerical_node_match.__doc__ = numerical_doc
numerical_edge_match.__doc__ = numerical_doc.replace("node", "edge")
tmpdoc = numerical_doc.replace("node", "edge")
tmpdoc = tmpdoc.replace("numerical_edge_match", "numerical_multiedge_match")
numerical_multiedge_match.__doc__ = tmpdoc


generic_doc = """
Returns a comparison function for a generic attribute.

The value(s) of the attr(s) are compared using the specified
operators. If all the attributes are equal, then the constructed
function returns True.

Parameters
----------
attr : string | list
    The node attribute to compare, or a list of node attributes
    to compare.
default : value | list
    The default value for the node attribute, or a list of
    default values for the node attributes.
op : callable | list
    The operator to use when comparing attribute values, or a list
    of operators to use when comparing values for each attribute.

Returns
-------
match : function
    The customized, generic `node_match` function.

Examples
--------
>>> from operator import eq
>>> from math import isclose
>>> from networkx.algorithms.isomorphism import generic_node_match
>>> nm = generic_node_match("weight", 1.0, isclose)
>>> nm = generic_node_match("color", "red", eq)
>>> nm = generic_node_match(["weight", "color"], [1.0, "red"], [isclose, eq])

"""


def generic_node_match(attr, default, op):
    if isinstance(attr, str):

        def match(data1, data2):
            return op(data1.get(attr, default), data2.get(attr, default))

    else:
        attrs = list(zip(attr, default, op))  # Python 3

        def match(data1, data2):
            for attr, d, operator in attrs:
                if not operator(data1.get(attr, d), data2.get(attr, d)):
                    return False
            else:
                return True

    return match


generic_edge_match = copyfunc(generic_node_match, "generic_edge_match")


def generic_multiedge_match(attr, default, op):
    """Returns a comparison function for a generic attribute.

    The value(s) of the attr(s) are compared using the specified
    operators. If all the attributes are equal, then the constructed
    function returns True. Potentially, the constructed edge_match
    function can be slow since it must verify that no isomorphism
    exists between the multiedges before it returns False.

    Parameters
    ----------
    attr : string | list
        The edge attribute to compare, or a list of node attributes
        to compare.
    default : value | list
        The default value for the edge attribute, or a list of
        default values for the edgeattributes.
    op : callable | list
        The operator to use when comparing attribute values, or a list
        of operators to use when comparing values for each attribute.

    Returns
    -------
    match : function
        The customized, generic `edge_match` function.

    Examples
    --------
    >>> from operator import eq
    >>> from math import isclose
    >>> from networkx.algorithms.isomorphism import generic_node_match
    >>> nm = generic_node_match("weight", 1.0, isclose)
    >>> nm = generic_node_match("color", "red", eq)
    >>> nm = generic_node_match(["weight", "color"], [1.0, "red"], [isclose, eq])

    """

    # This is slow, but generic.
    # We must test every possible isomorphism between the edges.
    if isinstance(attr, str):
        attr = [attr]
        default = [default]
        op = [op]
    attrs = list(zip(attr, default))  # Python 3

    def match(datasets1, datasets2):
        values1 = []
        for data1 in datasets1.values():
            x = tuple(data1.get(attr, d) for attr, d in attrs)
            values1.append(x)
        values2 = []
        for data2 in datasets2.values():
            x = tuple(data2.get(attr, d) for attr, d in attrs)
            values2.append(x)
        for vals2 in itertools.permutations(values2):
            for xi, yi in zip(values1, vals2):
                if not all(map(lambda x, y, z: z(x, y), xi, yi, op)):
                    # This is not an isomorphism, go to next permutation.
                    break
            else:
                # Then we found an isomorphism.
                return True
        else:
            # Then there are no isomorphisms between the multiedges.
            return False

    return match


# Docstrings for numerical functions.
generic_node_match.__doc__ = generic_doc
generic_edge_match.__doc__ = generic_doc.replace("node", "edge")
