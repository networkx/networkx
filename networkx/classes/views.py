#    Copyright (C) 2004-2016 by
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
Classes to provide node edge and degree "views" of a graph.

The "views" do not copy any data yet are iterable containers
of the nodes or edges of the graph. They are updated as the
graph is updated, so updating the graph while iterating through
the view is not permitted.

NodeViewer V allows `len(V)`, `n in V`, `d=V[n]`, and set operations "V1 & V2".
    where d is the node data dict. Iteration is over the nodes only.

NodeView V allows `len(V), `n in V`, `(n, d) in V`, and `d=V[n]`
    Iteration depends on arguments `data` and `default`.
    If `data` is `False` (the default) then iterate over nodes.
    If `data is True iterate over `(node, datadict)` pairs.
    Otherwise iterate over `(node, datadict.get(data, default))`.

DegreeView V allows `len(V)`, `deg=V[n]`, and iteration over (n, degree) pairs.
    There are many flavors of DegreeView for In/Out/Directed/Multi.
    No set operations are implemented for degrees, use NodeView.

EdgeViewer V allows `len(V)`, `e in V`, iteration and set operations.
    Iteration is over 3-tuples `(u, v, k)` for multigraph, and 2-tuples
    `(u, v)` for not multigraph.
    Set operations

EdgeView V allows `len(V)`, `e in V`, and iteration over edge tuples.
    Iteration depends on `data` and `default` and for multigraph `keys`
    If `data is False` (the default) then iterate over 2-tuples `(u, v)`.
    If `data is True` iterate over 3-tuples `(u, v, datadict)`.
    Otherwise iterate over `(u, v, datadict.get(data, default))`.
    For Multigraphs, if `keys is True`, replace `u, v` with `u, v, key` above.

Summary:
Views for nodes, edges and degree for all base graph classes.
A view means a read-only object that is quick to create, automatically
updated when graph changes, and provides basic access like `n in V`,
`for n in V`, `V[n]` and set operations.

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
    EVdata & {(1, 2, "blue"), (2, 3, "red")}

    EVnbunch=G.edges(nbunch=2)
    assert((2, 3) in EVbunch)
    assert((5, 6) in EVbunch)   #  at the moment, nbunch ignored in contains
    for u, v in EVbunch: assert(u == 2 or v == 2)

    EVmulti=MG.edges(keys=True)
    assert((2, 3, 0) in EVmulti) #  keys==True enforces 3-tuples for contains
    assert_raises((2, 3) in EVmulti, ValueError)
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
from collections import KeysView, ItemsView, Set, Iterator

__all__ = ['NodeViewer', 'NodeView',
           'EdgeViewer', 'OutEdgeViewer', 'InEdgeViewer',
           'EdgeView', 'OutEdgeView', 'InEdgeView',
           'MultiEdgeViewer', 'OutMultiEdgeViewer', 'InMultiEdgeViewer',
           'MultiEdgeView', 'OutMultiEdgeView', 'InMultiEdgeView',
           'DegreeView', 'DiDegreeView', 'InDegreeView', 'OutDegreeView',
           'MultiDegreeView', 'DiMultiDegreeView',
           'InMultiDegreeView', 'OutMultiDegreeView']


# NodeViews
class NodeViewer(KeysView):
    """A Viewer class to act as G.nodes for a NetworkX Graph

    Set operations act on the nodes without considering data.
    Iteration is over nodes. Node data can be looked up.
    Use NodeView to iterate over data or to specify data attribute
    for lookup. NodeView is created by calling the NodeViewer.

    Parameters
    ==========
    graph : NetworkX graph-like class
    """
    __slots__ = '_mapping',

    def __getstate__(self):
        return {'_mapping': self._mapping}
#        return {slot: getattr(self, slot) for slot in self.__slots__}

    def __setstate__(self, d):
        self._mapping = d['_mapping']
#        for slot in d:
#            setattr(self, slot, d[slot])

    def __init__(self, graph):
        self._mapping = graph.node

    def __call__(self, data=False, default=None):
        if data is False:
            return self
        return NodeView(self._mapping, data, default)

    def __getitem__(self, n):
        return self._mapping[n]

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


class NodeView(object):
    """A View class for nodes of a NetworkX Graph

    Set operations can be done with NodeViewer, but not NodeView
    Node data can be iterated over for NodeView but not NodeViewer

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
        return NodeView(self._mapping, data, default)

    def __getitem__(self, n):
        ddict = self._mapping[n]
        data = self._data
        if data is False or data is True:
            return ddict
        if data in ddict:
            return ddict[data]
        return self._default

    def __iter__(self):
        if self._data is False:
            return iter(self._mapping)
        return ((n, self[n]) for n in self._mapping)

    def __contains__(self, n):
        try:
            return n in self._mapping
        except TypeError:
            n, d = n
            return n in self._mapping and self._mapping[n] == d

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
    """
    def __init__(self, G, nbunch=None, weight=None):
        self.nbunch_iter = G.nbunch_iter
        self.succ = G.succ if hasattr(G, "succ") else G.adj
        self.pred = G.pred if hasattr(G, "pred") else G.adj
        self._nodes = self.succ if nbunch is None \
            else list(self.nbunch_iter(nbunch))
        self._weight = weight

    def __call__(self, nbunch=None, weight=None):
        try:
            if nbunch in self._nodes:
                return self.__class__(self, nbunch, weight)[nbunch]
        except TypeError:
            pass
        return self.__class__(self, nbunch, weight)

    def __getitem__(self, n):
        weight = self._weight
        succs = self.succ[n]
        preds = self.pred[n]
        if weight is None:
            return len(succs) + len(preds)
        return sum(dd.get(weight, 1) for dd in succs.values()) + \
            sum(dd.get(weight, 1) for dd in preds.values())

    def __iter__(self):
        for n in self._nodes:
            yield (n, self[n])

    def __len__(self):
        return len(self.succ)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self))


class DegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self.succ[n]
        if weight is None:
            return len(nbrs) + (n in nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values()) + \
            (n in nbrs and nbrs[n].get(weight, 1))


class OutDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self.succ[n]
        if self._weight is None:
            return len(nbrs)
        return sum(dd.get(self._weight, 1) for dd in nbrs.values())


class InDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self.pred[n]
        if weight is None:
            return len(nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values())


class MultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self.succ[n]
        if weight is None:
            return sum(len(keys) for keys in nbrs.values()) + \
                    (n in nbrs and len(nbrs[n]))
        # edge weighted graph - degree is sum of nbr edge weights
        deg = sum(d.get(weight, 1) for key_dict in nbrs.values()
                  for d in key_dict.values())
        if n in nbrs:
            deg += sum(d.get(weight, 1) for d in nbrs[n].values())
        return deg


class DiMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        succs = self.succ[n]
        preds = self.pred[n]
        if weight is None:
            return sum(len(keys) for keys in succs.values()) + \
                sum(len(keys) for keys in preds.values())
        # edge weighted graph - degree is sum of nbr edge weights
        deg = sum(d.get(weight, 1) for key_dict in succs.values()
                  for d in key_dict.values()) + \
            sum(d.get(weight, 1) for key_dict in preds.values()
                for d in key_dict.values())
        return deg


class InMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self.pred[n]
        if weight is None:
            return sum(len(data) for data in nbrs.values())
        # edge weighted graph - degree is sum of nbr edge weights
        return sum(d.get(weight, 1) for key_dict in nbrs.values()
                   for d in key_dict.values())


class OutMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self.succ[n]
        if weight is None:
            return sum(len(data) for data in nbrs.values())
        # edge weighted graph - degree is sum of nbr edge weights
        return sum(d.get(weight, 1) for key_dict in nbrs.values()
                   for d in key_dict.values())


# EdgeViews
class OutEdgeView(object):
    def __init__(self, viewer, nbunch=None, data=False, default=None):
        self.nbunch_iter = viewer.nbunch_iter
        self._adjdict = viewer._adjdict
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(viewer.nbunch_iter(nbunch))
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
        except ValueError:
            raise ValueError("Edge must have at least 2 entries")
        return e == self._report(u, v, ddict)

    def __repr__(self):
        return "{0.__class__.__name__}({1!r})".format(self, list(self))

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())


class EdgeView(OutEdgeView):
    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, dd in nbrs.items():
                if nbr not in seen:
                    yield self._report(n, nbr, dd)
            seen[n] = 1
        del seen

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs()) // 2


class InEdgeView(OutEdgeView):
    def __init__(self, viewer, nbunch=None, data=False, default=None):
        self.nbunch_iter = viewer.nbunch_iter
        self._adjdict = viewer._adjdict
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(viewer.nbunch_iter(nbunch))
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
        except ValueError:
            raise ValueError("Edge must have at least 2 entries")
        return e == self._report(v, u, ddict)


class OutMultiEdgeView(OutEdgeView):
    def __init__(self, viewer, nbunch=None,
                 data=False, keys=False, default=None):
        self.nbunch_iter = viewer.nbunch_iter
        self._adjdict = viewer._adjdict
        self.keys = keys
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(viewer.nbunch_iter(nbunch))
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


class MultiEdgeView(OutMultiEdgeView):
    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, kd in nbrs.items():
                if nbr not in seen:
                    for k, dd in kd.items():
                        yield self._report(n, nbr, k, dd)
            seen[n] = 1
        del seen

    def __len__(self):
        return sum(len(kdict) for n, nbrs in self._nodes_nbrs()
                   for nbr, kdict in nbrs.items()) // 2


class InMultiEdgeView(OutMultiEdgeView):
    def __init__(self, viewer, nbunch=None,
                 data=False, keys=False, default=None):
        self.nbunch_iter = viewer.nbunch_iter
        self._adjdict = viewer._adjdict
        self.keys = keys
        if nbunch is None:
            self._nodes_nbrs = self._adjdict.items
        else:
            nbunch = list(viewer.nbunch_iter(nbunch))
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


# EdgeViewers    have set operations and no data reported
class OutEdgeViewer(Set):
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
    """
    @classmethod
    def _from_iterable(self, it):
        return set(it)

    view = OutEdgeView

    def __init__(self, G):
        self.succ = G.succ if hasattr(G, "succ") else G.adj
        self.pred = G.pred if hasattr(G, "pred") else G.adj
        self.nbunch_iter = G.nbunch_iter
        self._adjdict = self.succ
        self._nodes_nbrs = self.succ.items

    def __call__(self, nbunch=None, data=False, default=None):
        return self.view(self, nbunch, data, default)

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr in nbrs:
                yield (n, nbr)

    def __contains__(self, e):
        try:
            u, v = e
            return v in self.succ[u]
        except KeyError:
            return False
        except ValueError:
            ValueError("Edge must have 2 entries")

    def __getitem__(self, e):
        u, v = e
        return self.succ[u][v]

    def __repr__(self):
        return "{0.__class__.__name__}({1!r})".format(self, list(self))
    # Needed for Python 3.3 which doesn't have set define the
    # right-side set operations __rsub__ __xor__ __rand__ __ror__
    __rand__ = set.__and__
    __ror__ = set.__or__
    __rxor__ = set.__xor__

    def __rsub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable(e for e in other if e not in self)


class EdgeViewer(OutEdgeViewer):

    view = EdgeView

    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr in nbrs:
                if nbr not in seen:
                    yield (n, nbr)
            seen[n] = 1
        del seen

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs()) // 2


class InEdgeViewer(OutEdgeViewer):

    view = InEdgeView

    def __init__(self, G):
        self.succ = G.succ if hasattr(G, "succ") else G.adj
        self.pred = G.pred if hasattr(G, "pred") else G.adj
        self.nbunch_iter = G.nbunch_iter
        self._adjdict = self.pred
        self._nodes_nbrs = self.pred.items

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr in nbrs:
                yield (nbr, n)

    def __contains__(self, e):
        try:
            u, v = e
            return u in self.pred[v]
        except KeyError:
            return False
        except ValueError:
            ValueError("Edge must have 2 entries")


class OutMultiEdgeViewer(OutEdgeViewer):

    view = OutMultiEdgeView

    def __call__(self, nbunch=None, data=False, keys=False, default=None):
        return self.view(self, nbunch, data, keys, default)

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
            return k in self.succ[u][v]
        except KeyError:
            return False

    def __getitem__(self, e):
        u, v, k = e
        return self.succ[u][v][k]

    def __len__(self):
        return sum(len(kdict) for n, nbrs in self._nodes_nbrs()
                   for nbr, kdict in nbrs.items())


class MultiEdgeViewer(OutMultiEdgeViewer):

    view = MultiEdgeView

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


class InMultiEdgeViewer(OutMultiEdgeViewer):

    view = InMultiEdgeView

    def __init__(self, G):
        self.succ = G.succ if hasattr(G, "succ") else G.adj
        self.pred = G.pred if hasattr(G, "pred") else G.adj
        self.nbunch_iter = G.nbunch_iter
        self._adjdict = self.pred
        self._nodes_nbrs = self.pred.items

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
            return k in self.succ[u][v]
        except KeyError:
            return False
