#    Copyright (C) 2004-2017 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Aric Hagberg (hagberg@lanl.gov),
#          Pieter Swart (swart@lanl.gov),
#          Dan Schult(dschult@colgate.edu)
"""
View Classes provide node, edge and degree "views" of a graph.

Views for nodes, edges and degree are provided for all base graph classes.
A view means a read-only object that is quick to create, automatically
updated when the graph changes, and provides basic access like `n in V`,
`for n in V`, `V[n]` and set operations.

The views are read-only iterable containers that are updated as the
graph is updated. Thus the graph should not be updated while iterating
through the view. Views can be iterated over multiple times.
Edge and Node views also allow data attribute lookup.
The resulting attribute dict is writable as `G.edges[3, 4]['color']='red'`
Degree views allow lookup of degree values for single nodes.
Weighted degree is supported with the `weight` argument.

NodeView
========

    `V = G.nodes` (or `V = G.nodes()`) allows `len(V)`, `n in V`, set
    operations e.g. "V1 & V2", and `ddict = V[n]`, where `ddict` is
    the node data dict. Iteration is over the nodes by default.

NodeDataView
============

    To iterate over (node, data) pairs, use arguments to `G.nodes()`
    to create a DataView e.g. `DV = G.nodes(data='color', default='red')`.
    The DataView iterates as `for n, color in DV` and allows
    `(n, 'red') in VD`. For `DV = G.nodes(data=True)`, the DataViews
    use the full datadict in writeable form also allowing
    `(n, {'color': 'red'}) in VD`. DataViews do not provide set operations.
    For hashable data attributes use `set(G.nodes(data='color'))`.

DegreeView
==========

    `V = G.degree()` allows `len(V)`, `deg=V[n]`, and iteration
    over (n, degree) pairs. There are many flavors of DegreeView
    for In/Out/Directed/Multi. For Directed Graphs, `G.degree()`
    counts both in and out going edges. `G.out_degree()` and
    `G.in_degree()` count only specific directions.
    Weighted degree using edge data attributes is provide via
    `V = G.degree(weight='attr_name')` where any string with the
    attribute name can be used. `weight=None` is the default.
    No set operations are implemented for degrees, use NodeView.

    The argument `nbunch` restricts iteration to nodes in nbunch.
    The DegreeView can still lookup any node even if nbunch is specified.

EdgeView
========

    `V = G.edges` or `V = G.edges()` allows `len(V)`, `e in V`, and set
    operations. Iteration is over 2-tuples `(u, v)`. For multigraph
    edges default iteration is 3-tuples `(u, v, k)` but 2-tuples can
    be obtained from `V = G.edges(keys=False)`.
    Set operations for directed graphs treat the edges as a set of 2-tuples.
    For undirected graphs, 2-tuples are not unique representations of edges.
    So long as the set being compared to contains unique representations
    of its edges, the set operations will act as expected. If the other
    set contains both `(0, 1)` and `(1, 0)` however, the result of set
    operations may contain both representations of the same edge.

EdgeDataView
============

    `V = G.edges(data='weight', default=1)` allows `len(V)`, `e in V`,
    and iteration over edge tuples.
    Iteration depends on `data` and `default` and for multigraph `keys`
    If `data is False` (the default) then iterate over 2-tuples `(u, v)`.
    If `data is True` iterate over 3-tuples `(u, v, datadict)`.
    Otherwise iterate over `(u, v, datadict.get(data, default))`.
    For Multigraphs, if `keys is True`, replace `u, v` with `u, v, key`
    to create 3-tuples and 4-tuples.


Examples
========

NodeView:  options: data, default  (data makes `iter` and `contains`
                                    act on (node, data) 2-tuples)
    NV=G.nodes()
    assert(2 in NV)
    for n in NV: print(n)
    datadict = NV[2]
    NV & {1, 2, 3}

    NVdata=G.nodes(data=True)
    assert( (2, NV[2]) in NVdata)
    for n, dd in NVdata: print(dd['color'])
    assert(NVdata[2] == NV[2])

    NVdata=G.nodes(data='color')
    assert( (2, NV[2]) in NVdata)
    for n, dd in NVdata: print(dd['color'])
    assert(NVdata[2] != NV[2])

EdgeView: options: nbunch; data, default; keys

    EV=G.edges()
    assert((2, 3) in EV)
    for u, v in EV: print((u, v))
    EV & {(1, 2), (3, 4)}

    EVdata=G.edges(data='color')
    assert((2, 3, 'blue') in EVdata)
    for u, v, c in EVdata: print("({}, {}) has color:{}".format(u, v, c))

    EVnbunch=G.edges(nbunch=2)
    assert((2, 3) in EVbunch)
    assert((5, 6) in EVbunch)   #  at the moment, nbunch ignored in contains
    for u, v in EVbunch: assert(u == 2 or v == 2)

    EVmulti=MG.edges(keys=True)
    assert((2, 3, 0) in EVmulti) #  keys==True enforces 3-tuples for contains
    for u, v, k in EVmulti: print(u, v, k)

DegreeView:  options:  nbunch, weight (default=None)

    DV=G.degree()
    assert(DV[2] == 4)
    s = sum(deg for n, deg in DV)

    DVweight = G.degree(weight="span")
    assert(DVweight[2] == 6)   #  default value for edges without "span" is 1
    s = sum(span for n, span in DVweight

    DVnbunch = G.degree(nbunch=(2, 3))
    assert(len(list(DVnbunch)) == 2)     # iteration only passes over nbunch

Note: DegreeView can still lookup any node even if nbunch is specified.
nbunch only affects iteration. DiDegreeView looks both directions,
InDegreeView and OutDegreeView look in a directed way.
DegreeViews do not provide set operations.
"""
from collections import Mapping, KeysView, ItemsView, Set, Iterator
import networkx as nx

__all__ = ['DictView', 'AtlasView', 'MultiAtlasView',
           'NodeView', 'NodeDataView',
           'EdgeView', 'OutEdgeView', 'InEdgeView',
           'EdgeDataView', 'OutEdgeDataView', 'InEdgeDataView',
           'MultiEdgeView', 'OutMultiEdgeView', 'InMultiEdgeView',
           'MultiEdgeDataView', 'OutMultiEdgeDataView', 'InMultiEdgeDataView',
           'DegreeView', 'DiDegreeView', 'InDegreeView', 'OutDegreeView',
           'MultiDegreeView', 'DiMultiDegreeView',
           'InMultiDegreeView', 'OutMultiDegreeView']


# NodeViews
class NodeView(KeysView):
    """A Viewer class to act as G.nodes for a NetworkX Graph

    Set operations act on the nodes without considering data.
    Iteration is over nodes. Node data can be looked up.
    Use NodeDataView to iterate over data or to specify data attribute
    for lookup. NodeDataView is created by calling the NodeView.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> NV = G.nodes()
    >>> 2 in NV
    True
    >>> for n in NV: print(n)
    0
    1
    2
    >>> assert(NV & {1, 2, 3} == {1, 2})

    >>> G.add_node(2, color='blue')
    >>> NV[2]
    {'color': 'blue'}
    >>> G.add_node(8, color='red')
    >>> NDV = G.nodes(data=True)
    >>> (2, NV[2]) in NDV
    True
    >>> for n, dd in NDV: print((n, dd.get('color', 'aqua')))
    (0, 'aqua')
    (1, 'aqua')
    (2, 'blue')
    (8, 'red')
    >>> NDV[2] == NV[2]
    True

    >>> NVdata = G.nodes(data='color', default='aqua')
    >>> (2, NVdata[2]) in NVdata
    True
    >>> for n, dd in NVdata: print((n, dd))
    (0, 'aqua')
    (1, 'aqua')
    (2, 'blue')
    (8, 'red')
    >>> NVdata[2] == NV[2]  # NVdata gets 'color', NV gets datadict
    False

    Parameters
    ----------
    graph : NetworkX graph-like class
    """
    __slots__ = '_mapping',

    # Python 2 needs getstate and setstate for pickle to work with __slots__
#    def __getstate__(self):
#        return {'_mapping': self._mapping}
#        #return {slot: getattr(self, slot) for slot in self.__slots__}
#
#    def __setstate__(self, d):
#        self._mapping = d['_mapping']
#        #for slot in d:
#        #    setattr(self, slot, d[slot])

    def __init__(self, graph):
        self._mapping = graph._node

    def __call__(self, data=False, default=None):
        if data is False:
            return self
        return NodeDataView(self._mapping, data, default)

    def __getitem__(self, n):
        return self._mapping[n]

    def __str__(self):
        return 'NodeView(%r)' % tuple(self)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, tuple(self))

    # Needed for Python 3.3 which doesn't have Set define the
    # right-side set operations __rsub__ __xor__ __rand__ __ror__
    __rand__ = Set.__and__
    __ror__ = Set.__or__
    __rxor__ = Set.__xor__

    def __rsub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable(e for e in other if e not in self)


#class NodeDataView(object):
class NodeDataView(KeysView):
    """A View class for nodes of a NetworkX Graph

    Set operations can be done with NodeView, but not NodeDataView
    Node data can be iterated over for NodeDataView but not NodeView

    Parameters
    ==========
    graph : NetworkX graph-like class
    data : bool or string (default=False)
    default : object (default=None)
    """
    def __init__(self, mapping, data=False, default=None):
        self._mapping = mapping
        self._data = data
        self._default = default

    def __call__(self, data=False, default=None):
        if data == self._data and default == self._default:
            return self
        return NodeDataView(self._mapping, data, default)

    def __getitem__(self, n):
        ddict = self._mapping[n]
        data = self._data
        if data is False or data is True:
            return ddict
        return ddict[data] if data in ddict else self._default

    def __iter__(self):
        data = self._data
        if data is False:
            return iter(self._mapping)
        if data is True:
            return iter(self._mapping.items())
        return ((n, dd.get(data, self._default)) for n, dd in self._mapping.items())
        #return ((n, dd[data] if data in ddict else self._default) for n, dd in self._mapping.items())

    def __contains__(self, n):
        try:
            node_in = n in self._mapping
        except TypeError:
            n, d = n
            return n in self._mapping and self[n] == d
        if node_in is True:
            return node_in
        try:
            n, d = n
        except (TypeError, ValueError):
            return False
        return n in self._mapping and self[n] == d

    def __repr__(self):
        if self._data is False:
            return '%s(%r)' % (self.__class__.__name__, tuple(self))
        if self._data is True:
            return '%s(%r)' % (self.__class__.__name__, dict(self))
        return '%s(%r, data=%r)' % \
               (self.__class__.__name__, dict(self), self._data)


# DegreeViews
class DiDegreeView(object):
    """A View class for degree of nodes in a NetworkX Graph

    The functionality is like dict.items() with (node, degree) pairs.
    Additional functionality includes read-only lookup of node degree,
    and calling with optional features nbunch (for only a subset of nodes)
    and weight (use edge weights to compute degree).

    Parameters
    ==========
    graph : NetworkX graph-like class
    nbunch : node, container of nodes, or None meaning all nodes (default=None)
    weight : bool or string (default=None)

    Notes
    -----
    DegreeView can still lookup any node even if nbunch is specified.

    Examples
    --------
    >>> G = nx.path_graph(3)
    >>> DV = G.degree()
    >>> assert(DV[2] == 1)
    >>> assert(sum(deg for n, deg in DV) == 4)

    >>> DVweight = G.degree(weight="span")
    >>> G.add_edge(1, 2, span=34)
    >>> DVweight[2]
    34
    >>> DVweight[0]  #  default edge weight is 1
    1
    >>> sum(span for n, span in DVweight)  # sum weighted degrees
    70

    >>> DVnbunch = G.degree(nbunch=(1, 2))
    >>> assert(len(list(DVnbunch)) == 2)  # iteration over nbunch only
    """
    def __init__(self, G, nbunch=None, weight=None):
        self.nbunch_iter = G.nbunch_iter
        self._succ = G._succ if hasattr(G, "_succ") else G._adj
        self._pred = G._pred if hasattr(G, "_pred") else G._adj
        self._nodes = self._succ if nbunch is None \
            else list(self.nbunch_iter(nbunch))
        self._weight = weight

    def __call__(self, nbunch=None, weight=None):
        if nbunch is None:
            return self.__class__(self, None, weight)
        try:
            if nbunch in self._nodes:
                return self.__class__(self, None, weight)[nbunch]
        except TypeError:
            pass
        return self.__class__(self, nbunch, weight)

    def __getitem__(self, n):
        weight = self._weight
        succs = self._succ[n]
        preds = self._pred[n]
        if weight is None:
            return len(succs) + len(preds)
        return sum(dd.get(weight, 1) for dd in succs.values()) + \
            sum(dd.get(weight, 1) for dd in preds.values())

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                succs = self._succ[n]
                preds = self._pred[n]
                yield (n, len(succs) + len(preds))
        else:
            for n in self._nodes:
                succs = self._succ[n]
                preds = self._pred[n]
                deg = sum(dd.get(weight, 1) for dd in succs.values()) \
                      + sum(dd.get(weight, 1) for dd in preds.values())
                yield (n, deg)

    def __len__(self):
        return len(self._succ)

    def __str__(self):
        return 'DegreeView(%r)' % dict(self)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self))


class DegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return len(nbrs) + (n in nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values()) + \
            (n in nbrs and nbrs[n].get(weight, 1))
    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                nbrs = self._succ[n]
                yield (n, len(nbrs) + (n in nbrs))
        else:
            for n in self._nodes:
                nbrs = self._succ[n]
                deg = sum(dd.get(weight, 1) for dd in nbrs.values()) + \
                    (n in nbrs and nbrs[n].get(weight, 1))
                yield (n, deg)


class OutDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if self._weight is None:
            return len(nbrs)
        return sum(dd.get(self._weight, 1) for dd in nbrs.values())

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                succs = self._succ[n]
                yield (n, len(succs))
        else:
            for n in self._nodes:
                succs = self._succ[n]
                deg = sum(dd.get(weight, 1) for dd in succs.values())
                yield (n, deg)


class InDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._pred[n]
        if weight is None:
            return len(nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values())

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                preds = self._pred[n]
                yield (n, len(preds))
        else:
            for n in self._nodes:
                preds = self._pred[n]
                deg = sum(dd.get(weight, 1) for dd in preds.values())
                yield (n, deg)


class MultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return sum(len(keys) for keys in nbrs.values()) + \
                    (n in nbrs and len(nbrs[n]))
        # edge weighted graph - degree is sum of nbr edge weights
        deg = sum(d.get(weight, 1) for key_dict in nbrs.values()
                  for d in key_dict.values())
        if n in nbrs:
            deg += sum(d.get(weight, 1) for d in nbrs[n].values())
        return deg

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                nbrs = self._succ[n]
                deg = sum(len(keys) for keys in nbrs.values()) + \
                    (n in nbrs and len(nbrs[n]))
                yield (n, deg)
        else:
            for n in self._nodes:
                nbrs = self._succ[n]
                deg = sum(d.get(weight, 1) for key_dict in nbrs.values()
                          for d in key_dict.values())
                if n in nbrs:
                    deg += sum(d.get(weight, 1) for d in nbrs[n].values())
                yield (n, deg)


class DiMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        succs = self._succ[n]
        preds = self._pred[n]
        if weight is None:
            return sum(len(keys) for keys in succs.values()) + \
                sum(len(keys) for keys in preds.values())
        # edge weighted graph - degree is sum of nbr edge weights
        deg = sum(d.get(weight, 1) for key_dict in succs.values()
                  for d in key_dict.values()) + \
            sum(d.get(weight, 1) for key_dict in preds.values()
                for d in key_dict.values())
        return deg

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                succs = self._succ[n]
                preds = self._pred[n]
                deg = sum(len(keys) for keys in succs.values()) + \
                    sum(len(keys) for keys in preds.values())
                yield (n, deg)
        else:
            for n in self._nodes:
                succs = self._succ[n]
                preds = self._pred[n]
                deg = sum(d.get(weight, 1) for key_dict in succs.values()
                          for d in key_dict.values()) + \
                    sum(d.get(weight, 1) for key_dict in preds.values()
                        for d in key_dict.values())
                yield (n, deg)


class InMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._pred[n]
        if weight is None:
            return sum(len(data) for data in nbrs.values())
        # edge weighted graph - degree is sum of nbr edge weights
        return sum(d.get(weight, 1) for key_dict in nbrs.values()
                   for d in key_dict.values())

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                nbrs = self._pred[n]
                deg = sum(len(data) for data in nbrs.values())
                yield (n, deg)
        else:
            for n in self._nodes:
                nbrs = self._pred[n]
                deg = sum(d.get(weight, 1) for key_dict in nbrs.values()
                           for d in key_dict.values())
                yield (n, deg)


class OutMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return sum(len(data) for data in nbrs.values())
        # edge weighted graph - degree is sum of nbr edge weights
        return sum(d.get(weight, 1) for key_dict in nbrs.values()
                   for d in key_dict.values())

    def __iter__(self):
        weight = self._weight
        if weight is None:
            for n in self._nodes:
                nbrs = self._succ[n]
                deg = sum(len(data) for data in nbrs.values())
                yield (n, deg)
        else:
            for n in self._nodes:
                nbrs = self._succ[n]
                deg = sum(d.get(weight, 1) for key_dict in nbrs.values()
                           for d in key_dict.values())
                yield (n, deg)


# EdgeDataViews
class OutEdgeDataView(object):
    def __init__(self, graph, nbunch=None, data=False, default=None):
        self.graph = graph
        self._adjdict = graph._succ if hasattr(graph, '_succ') else graph._adj
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(graph.nbunch_iter(nbunch))
            self._nodes_nbrs = lambda: [(n, self._adjdict[n]) for n in nbunch]
        # Set _report based on data and default
        if data is True:
            self._report = lambda n, nbr, dd: (n, nbr, dd)
        elif data is False:
            self._report = lambda n, nbr, dd: (n, nbr)
        else:  # data is attribute name
            self._report = lambda n, nbr, dd: \
                    (n, nbr, dd[data]) if data in dd else (n, nbr, default)

    def __iter__(self):
        return (self._report(n, nbr, dd) for n, nbrs in self._nodes_nbrs()
                for nbr, dd in nbrs.items())

    def __contains__(self, e):
        try:
            u, v = e[:2]
            ddict = self._adjdict[u][v]
        except KeyError:
            return False
        return e == self._report(u, v, ddict)

    def __str__(self):
        return "EdgeView({!r})".format(list(self))

    def __repr__(self):
        return "{0.__class__.__name__}({1!r})".format(self, list(self))

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())


class EdgeDataView(OutEdgeDataView):
    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, dd in nbrs.items():
                if nbr not in seen:
                    yield self._report(n, nbr, dd)
            seen[n] = 1
        del seen

    def __contains__(self, e):
        try:
            u, v = e[:2]
            ddict = self._adjdict[u][v]
        except KeyError:
            try:
                ddict = self._adjdict[v][u]
            except KeyError:
                return False
        return e == self._report(u, v, ddict)

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs()) // 2


class InEdgeDataView(OutEdgeDataView):
    def __init__(self, graph, nbunch=None, data=False, default=None):
        self.graph = graph
        self._adjdict = graph._pred
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(graph.nbunch_iter(nbunch))
            self._nodes_nbrs = lambda: [(n, self._adjdict[n]) for n in nbunch]
        # Set _report based on data and default
        if data is True:
            self._report = lambda n, nbr, dd: (nbr, n, dd)
        elif data is False:
            self._report = lambda n, nbr, dd: (nbr, n)
        else:  # data is attribute name
            self._report = lambda n, nbr, dd: \
                    (nbr, n, dd[data]) if data in dd else (nbr, n, default)

    def __contains__(self, e):
        try:
            u, v = e[:2]
            ddict = self._adjdict[v][u]
        except KeyError:
            return False
        return e == self._report(v, u, ddict)


class OutMultiEdgeDataView(OutEdgeDataView):
    def __init__(self, graph, nbunch=None,
                 data=False, keys=False, default=None):
        self.graph = graph
        self._adjdict = graph._succ if hasattr(graph, '_succ') else graph._adj
        self.keys = keys
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(graph.nbunch_iter(nbunch))
            self._nodes_nbrs = lambda: [(n, self._adjdict[n]) for n in nbunch]
        # Set _report based on data and default
        if data is True:
            if keys is True:
                self._report = lambda n, nbr, k, dd: (n, nbr, k, dd)
            else:
                self._report = lambda n, nbr, k, dd: (n, nbr, dd)
        elif data is False:
            if keys is True:
                self._report = lambda n, nbr, k, dd: (n, nbr, k)
            else:
                self._report = lambda n, nbr, k, dd: (n, nbr)
        else:  # data is attribute name
            if keys is True:
                self._report = lambda n, nbr, k, dd: (n, nbr, k, dd[data]) \
                        if data in dd else (n, nbr, k, default)
            else:
                self._report = lambda n, nbr, k, dd: (n, nbr, dd[data]) \
                        if data in dd else (n, nbr, default)

    def __iter__(self):
        return (self._report(n, nbr, k, dd) for n, nbrs in self._nodes_nbrs()
                for nbr, kd in nbrs.items() for k, dd in kd.items())

    def __contains__(self, e):
        u, v = e[:2]
        try:
            kdict = self._adjdict[u][v]
        except KeyError:
            return False
        if self.keys is True:
            k = e[2]
            try:
                dd = kdict[k]
            except KeyError:
                return False
            return e == self._report(u, v, k, dd)
        for k, dd in kdict.items():
            if e == self._report(u, v, k, dd):
                return True
        return False

    def __len__(self):
        return sum(len(kdict) for n, nbrs in self._nodes_nbrs()
                   for nbr, kdict in nbrs.items())


class MultiEdgeDataView(OutMultiEdgeDataView):
    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, kd in nbrs.items():
                if nbr not in seen:
                    for k, dd in kd.items():
                        yield self._report(n, nbr, k, dd)
            seen[n] = 1
        del seen

    def __contains__(self, e):
        u, v = e[:2]
        try:
            kdict = self._adjdict[u][v]
        except KeyError:
            try:
                kdict = self._adjdict[v][u]
            except KeyError:
                return False
        if self.keys is True:
            k = e[2]
            try:
                dd = kdict[k]
            except KeyError:
                return False
            return e == self._report(u, v, k, dd)
        for k, dd in kdict.items():
            if e == self._report(u, v, k, dd):
                return True
        return False

    def __len__(self):
        return sum(len(kdict) for n, nbrs in self._nodes_nbrs()
                   for nbr, kdict in nbrs.items()) // 2


class InMultiEdgeDataView(OutMultiEdgeDataView):
    def __init__(self, graph, nbunch=None,
                 data=False, keys=False, default=None):
        self.graph = graph
        self._adjdict = graph._pred
        self.keys = keys
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(graph.nbunch_iter(nbunch))
            self._nodes_nbrs = lambda: [(n, self._adjdict[n]) for n in nbunch]
        # Set _report based on data and default
        if data is True:
            if keys is True:
                self._report = lambda n, nbr, k, dd: (nbr, n, k, dd)
            else:
                self._report = lambda n, nbr, k, dd: (nbr, n, dd)
        elif data is False:
            if keys is True:
                self._report = lambda n, nbr, k, dd: (nbr, n, k)
            else:
                self._report = lambda n, nbr, k, dd: (nbr, n)
        else:  # data is attribute name
            if keys is True:
                self._report = lambda n, nbr, k, dd: (nbr, n, k, dd[data]) \
                        if data in dd else (n, nbr, k, default)
            else:
                self._report = lambda n, nbr, k, dd: (nbr, n, dd[data]) \
                        if data in dd else (nbr, n, default)

    def __contains__(self, e):
        v, u = e[:2]
        try:
            kdict = self._adjdict[u][v]
        except KeyError:
            return False
        if self.keys is True:
            k = e[2]
            dd = kdict[k]
            return e == self._report(u, v, k, dd)
        for k, dd in kdict.items():
            if e == self._report(u, v, k, dd):
                return True
        return False


# EdgeViews    have set operations and no data reported
class OutEdgeView(Set):
    """A View class for edges of a NetworkX Graph

    Elements are treated as edge tuples for `e in V` or set operations.
    The form of the tuple is controlled by `data`, `default` and `keys`.
    If the optional `nbunch` argument is provided only edges involving those
    nodes are reported.

    If `data is False` (the default) then iterate over 2-tuples `(u, v)`.
    If `data is True` iterate over 3-tuples `(u, v, datadict)`.
    Otherwise iterate over `(u, v, datadict.get(data, default))`.
    For Multigraphs, if `keys is True`, replace `u, v` with `u, v, key` above.

    Parameters
    ==========
    graph : NetworkX graph-like class
    nbunch : (default= all nodes in graph) only report edges with these nodes
    keys : (only for MultiGraph. default=False) report edge key in tuple
    data : bool or string (default=False) see above
    default : object (default=None)

    Examples
    ========
    >>> G = nx.path_graph(4)
    >>> EV = G.edges()
    >>> (2, 3) in EV
    True
    >>> for u, v in EV: print((u, v))
    (0, 1)
    (1, 2)
    (2, 3)
    >>> assert(EV & {(1, 2), (3, 4)} == {(1, 2)})

    >>> EVdata = G.edges(data='color', default='aqua')
    >>> G.add_edge(2, 3, color='blue')
    >>> assert((2, 3, 'blue') in EVdata)
    >>> for u, v, c in EVdata: print("({}, {}) has color: {}".format(u, v, c))
    (0, 1) has color: aqua
    (1, 2) has color: aqua
    (2, 3) has color: blue

    >>> EVnbunch = G.edges(nbunch=2)
    >>> assert((2, 3) in EVnbunch)
    >>> assert((0, 1) in EVnbunch)   #  nbunch is ignored in __contains__
    >>> for u, v in EVnbunch: assert(u == 2 or v == 2)

    >>> MG = nx.path_graph(4, create_using=nx.MultiGraph())
    >>> EVmulti = MG.edges(keys=True)
    >>> (2, 3, 0) in EVmulti
    True
    >>> (2, 3) in EVmulti   # 2-tuples work even when keys is True
    True
    >>> key = MG.add_edge(2, 3)
    >>> for u, v, k in EVmulti: print((u, v, k))
    (0, 1, 0)
    (1, 2, 0)
    (2, 3, 0)
    (2, 3, 1)
    """
    @classmethod
    def _from_iterable(self, it):
        return set(it)

    view = OutEdgeDataView

    def __init__(self, G):
        self.graph = G
        self._adjdict = G._succ if hasattr(G, "_succ") else G._adj
        self._nodes_nbrs = self._adjdict.items
        self.nbunch = None
        self.data = False
        self.default = None
        self._report = lambda n, nbr, dd: (n, nbr)
#        self.nbunch_iter = G.nbunch_iter
#        self._pred = G._pred if hasattr(G, "_pred") else G._adj

    def __call__(self, nbunch=None, data=False, default=None):
#        if nbunch == self.nbunch and data == self.data \
#                and default == self.default:
#            return self
#        if nbunch is None:
#            self._nodes_nbrs = self._adjdict.items
#        else:
#            nbunch = list(self.graph.nbunch_iter(nbunch))
#            self._nodes_nbrs = lambda: [(n, self._adjdict[n]) for n in nbunch]
#        self.data = data
#        self.default = default
#        if data is True:
#            self._report = lambda n, nbr, dd: (n, nbr, dd)
#        elif data is False:
#            self._report = lambda n, nbr, dd: (n, nbr)
#        else:  # data is attribute name
#            self._report = lambda n, nbr, dd: \
#                    (n, nbr, dd[data]) if data in dd else (n, nbr, default)
#        return self

        if nbunch is None and data is False:
            return self
        return self.view(self.graph, nbunch, data, default)
        #return ((n, nbr) for n, nbrs in self._nodes_nbrs()
        #        for nbr, dd in nbrs.items())

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr, dd in nbrs.items():
                yield self._report(n, nbr, dd)
    #        for nbr in nbrs.items():
    #            yield (n, nbr)

    def __contains__(self, e):
        try:
            u, v = e[:2]
            ddict = self._adjdict[u][v]
        except KeyError:
            return False
        return e == self._report(u, v, ddict)
    #def __contains__(self, e):
    #    try:
    #        u, v = e
    #        return v in self._adjdict[u]
    #    except KeyError:
    #        return False

    def __getitem__(self, e):
        u, v = e
        return self._adjdict[u][v]

    def __repr__(self):
        return "{0.__class__.__name__}({1!r})".format(self, list(self))
    # Needed for Python 3.3 which doesn't have set define the
    # right-side set operations __rsub__ __xor__ __rand__ __ror__
    __rand__ = Set.__and__
    __ror__ = Set.__or__
    __rxor__ = Set.__xor__

    def __rsub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable(e for e in other if e not in self)


class EdgeView(OutEdgeView):

    view = EdgeDataView

    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, dd in nbrs.items():
                if nbr not in seen:
                    yield self._report(n, nbr, dd)
#            for nbr in nbrs:
#                if nbr not in seen:
#                    yield (n, nbr)
            seen[n] = 1
        del seen

    def __contains__(self, e):
        try:
            u, v = e[:2]
            ddict = self._adjdict[u][v]
        except KeyError:
            try:
                ddict = self._adjdict[v][u]
            except KeyError:
                return False
        return e == self._report(u, v, ddict)

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs()) // 2


class InEdgeView(OutEdgeView):

    view = InEdgeDataView

    def __init__(self, G):
        self.graph = G
        self._adjdict = G._pred if hasattr(G, "_pred") else G._adj
        self._nodes_nbrs = self._adjdict.items
#        self.nbunch_iter = G.nbunch_iter
#        self._succ = G._succ if hasattr(G, "_succ") else G._adj
#        self._pred = G._pred if hasattr(G, "_pred") else G._adj
#        self.nbunch_iter = G.nbunch_iter
#        self._adjdict = self._pred
#        self._nodes_nbrs = self._pred.items

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr in nbrs:
                yield (nbr, n)

    def __contains__(self, e):
        try:
            u, v = e
            return u in self._adjdict[v]
        except KeyError:
            return False


class OutMultiEdgeView(OutEdgeView):

    view = OutMultiEdgeDataView

    def __call__(self, nbunch=None, data=False, keys=False, default=None):
        if nbunch is None and data is False and keys is True:
            return self
        return self.view(self.graph, nbunch, data, keys, default)

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr, kdict in nbrs.items():
                for key in kdict:
                    yield (n, nbr, key)

    def __contains__(self, e):
        N = len(e)
        if N == 3:
            u, v, k = e
        elif N == 2:
            u, v = e
            k = 0
        else:
            raise ValueError("MultiEdge must have length 2 or 3")
        try:
            return k in self._adjdict[u][v]
        except KeyError:
            return False

    def __getitem__(self, e):
        u, v, k = e
        return self._adjdict[u][v][k]

    def __len__(self):
        return sum(len(kdict) for n, nbrs in self._nodes_nbrs()
                   for nbr, kdict in nbrs.items())


class MultiEdgeView(OutMultiEdgeView):

    view = MultiEdgeDataView

    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, kd in nbrs.items():
                if nbr not in seen:
                    for k, dd in kd.items():
                        yield (n, nbr, k)
            seen[n] = 1
        del seen

    def __len__(self):
        return sum(len(kdict) for n, nbrs in self._nodes_nbrs()
                   for nbr, kdict in nbrs.items()) // 2


class InMultiEdgeView(OutMultiEdgeView):

    view = InMultiEdgeDataView

    def __init__(self, G):
        self.graph = G
        self._adjdict = G._pred if hasattr(G, "_pred") else G._adj
        self._nodes_nbrs = self._adjdict.items
#        self.nbunch_iter = G.nbunch_iter
#        self._succ = G._succ if hasattr(G, "_succ") else G._adj
#        self._pred = G._pred if hasattr(G, "_pred") else G._adj
#        self.nbunch_iter = G.nbunch_iter
#        self._adjdict = self._pred
#        self._nodes_nbrs = self._pred.items

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr, kdict in nbrs.items():
                for key in kdict:
                    yield (nbr, n, key)

    def __contains__(self, e):
        N = len(e)
        if N == 3:
            u, v, k = e
        elif N == 2:
            u, v = e
            k = 0
        else:
            raise ValueError("MultiEdge must have length 2 or 3")
        try:
            return k in self._adjdict[v][u]
        except KeyError:
            return False

class DictView(Mapping):
    __slots__ = ('_dict',)
    def __init__(self, d):
        self._dict = d
    def __len__(self):
        return len(self._dict)
    def __iter__(self):
        return iter(self._dict)
    def __getitem__(self, key):
        return self._dict[key]

class AtlasView(Mapping):
    __slots__ = ('_atlas',)
    def __init__(self, atlas):
        self._atlas = atlas
    def __len__(self):
        return len(self._atlas)
    def __iter__(self):
        return iter(self._atlas)
    def __getitem__(self, name):
        return DictView(self._atlas[name])

class MultiAtlasView(AtlasView):
    __slots__ = ()   # Still uses AtlasView slots names _atlas
    def __getitem__(self, name):
        return AtlasView(self._atlas[name])
