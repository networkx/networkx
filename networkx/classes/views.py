"""
Classes to provide node and edge "views" of a graph.

The "views" do not copy any data yet are iterable containers
of the nodes or edges of the graph. They are updated as the 
graph is updated, so updating the graph while iterating through
the view is not permitted.

NodeView V allows `len(V)`, `n in V`, `d=V[n]`, and set operations "V1 & V2".
    Iteration depends on arguments `data` and `default`. If `data` is `False`
    (the default) then iterate over nodes. If `data is True iterate over 
    `(node, datadict)` pairs. Otherwise iterate over 
    `(node, datadict.get(data, default))`.

DegreeView V allows `len(V)`, `deg=V[n]`, and iteration over (n, degree) pairs.
    There are many flavors of DegreeView for In/Out/Directed/Multi.
    No set operations are implemented for degrees, use NodeView.

EdgeView V allows `len(V)`, `e in V`, and iteration over edge tuples.
    Iteration depends on arguments `data` and `default` and for multigraph `keys` 
    If `data is False` (the default) then iterate over 2-tuples `(u,v)`. 
    If `data is True` iterate over 3-tuples `(u, v, datadict)`.
    Otherwise iterate over `(u, v, datadict.get(data, default))`.
    For Multigraphs, if `keys is True`, replace `u,v` with `u,v,key` above. 
    
    Set operations work when `data is False` on the (u, v) or (u, v, k) tuples.
    Use at your own risk when `data is not False` as the tuples are not 
    always hashable in that case.
"""
# Authors: Aric Hagberg (hagberg@lanl.gov),
#          Pieter Swart (swart@lanl.gov),
#          Dan Schult(dschult@colgate.edu)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from collections import KeysView, ItemsView, Set, Iterator

__all__ = ['NodeView', 'EdgeView', 'OutEdgeView', 'InEdgeView',
           'MultiEdgeView', 'OutMultiEdgeView', 'InMultiEdgeView',
           'DegreeView', 'DiDegreeView', 'InDegreeView', 'OutDegreeView',
           'MultiDegreeView', 'DiMultiDegreeView',
           'InMultiDegreeView', 'OutMultiDegreeView']

## NodeViews
class NodeView(ItemsView):
    """A View class for nodes of a NetworkX Graph

    Parameters
    ==========
    graph : NetworkX graph-like class
    data : bool or string (default=False)
    default : object (default=None)
    """
    def __init__(self, graph, data=False, default=None):
        self._mapping = graph.node
        self._data = data
        self._default = default
    def __getitem__(self, n):
        data = self._data
        ddict = self._mapping[n]
        if data is True:
            return ddict
        return ddict[data] if data in ddict else self._default
    def __iter__(self):
        if self._data is False:
            return iter(self._mapping)
        return ((n, self[n]) for n in self._mapping)
    def __contains__(self, n):
        try:
            return n in self._mapping
        except TypeError:
            n, d = n
            return n in self._mapping and self._mapping[n]==d
    def __repr__(self):
        if self._data is False:
            return repr(list(self._mapping.keys()))
        if self._data is True:
            return repr(list(self._mapping.items()))
        return str(dict(self))
    # Needed for Python 3.3 which doesn't have ItemsView define 
    # right set operations __rsub__ _rxor__ __rand__ __ror__
    __rand__ = ItemsView.__and__
    __ror__ = ItemsView.__or__
    __rxor__ = ItemsView.__xor__
    def __rsub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable(e for e in other if e not in self)

## DegreeViews
class DiDegreeView(object):
    """A View class for degree of nodes in a NetworkX Graph

    The functionality is like dict.items() with (node, degree) pairs.
    Additional functionality includes read-only lookup of nodes attribute dict.

    Parameters
    ==========
    graph : NetworkX graph-like class
    weight : bool or string (default=None)
    """
    def __init__(self, graph, weight=None):
        self._succ = graph.succ if hasattr(graph,"succ") else graph.adj
        self._pred = graph.pred if hasattr(graph,"pred") else graph.adj
        self._weight = weight
    def __iter__(self):
        for n in self._succ:
            yield (n, self[n])
    def __getitem__(self, n):
        weight = self._weight
        succs = self._succ[n]
        preds = self._pred[n]
        if weight is None:
            return len(succs) + len(preds)
        return sum(dd.get(weight, 1) for dd in succs.values()) + \
               sum(dd.get(weight, 1) for dd in preds.values())
    def __len__(self):
        return len(self._succ)
    def __repr__(self):
        return '%s(%r)'%(self.__class__.__name__, dict(self))

class DegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return len(nbrs) + (n in nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values()) + \
             (n in nbrs and nbrs[n].get(weight, 1))

class OutDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if self._weight is None:
            return len(nbrs)
        return sum(dd.get(self._weight, 1) for dd in nbrs.values())

class InDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._pred[n]
        if weight is None:
            return len(nbrs)
        return sum(dd.get(weight, 1) for dd in nbrs.values())

class MultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return sum(len(keys) for keys in nbrs.values()) + \
                    (n in nbrs and len(nbrs[n]))
        # edge weighted graph - degree is sum of nbr edge weights
        deg = sum(d.get(weight, 1) for key_dict in nbrs.values()\
                    for d in key_dict.values())
        if n in nbrs:
            deg += sum(d.get(weight, 1) for d in nbrs[n].values())
        return deg

class DiMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        succs = self._succ[n]
        preds = self._pred[n]
        if weight is None:
            return sum(len(keys) for keys in succs.values()) + \
                sum(len(keys) for keys in preds.values())
        # edge weighted graph - degree is sum of nbr edge weights
        deg = sum(d.get(weight, 1) for key_dict in succs.values()\
                    for d in key_dict.values()) + \
              sum(d.get(weight, 1) for key_dict in preds.values()\
                    for d in key_dict.values())
        return deg

class InMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._pred[n]
        if weight is None:
            return sum(len(data) for data in nbrs.values())
        # edge weighted graph - degree is sum of nbr edge weights
        return sum(d.get(weight, 1) for key_dict in nbrs.values()\
                    for d in key_dict.values())

class OutMultiDegreeView(DiDegreeView):
    def __getitem__(self, n):
        weight = self._weight
        nbrs = self._succ[n]
        if weight is None:
            return sum(len(data) for data in nbrs.values())
        # edge weighted graph - degree is sum of nbr edge weights
        return sum(d.get(weight, 1) for key_dict in nbrs.values()\
                    for d in key_dict.values())


## EdgeViews
class OutEdgeView(KeysView):
    """A View class for edges of a NetworkX Graph

    Elements are treated as edge tuples for `e in V` or set operations.
    The form of the tuple is controlled by arguments `data`, `default` and `keys`.
    If the optional `nbunch` argument is provided only edges involving those
    nodes are reported. 

    If `data is False` (the default) then iterate over 2-tuples `(u,v)`. 
    If `data is True` iterate over 3-tuples `(u, v, datadict)`.
    Otherwise iterate over `(u, v, datadict.get(data, default))`.
    For Multigraphs, if `keys is True`, replace `u,v` with `u,v,key` above. 

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

    def __init__(self, graph, nbunch=None, data=False, default=None):
        self._adjdict = ADJ = graph.succ if hasattr(graph, 'succ') else graph.adj
        if nbunch is None:
            self._nodes_nbrs = ADJ.items()
        else:
            # This is in __init__ b/c nbunch may be an iterator and get used up 
            self._nodes_nbrs = [(n, ADJ[n]) for n in graph.nbunch_iter(nbunch)]
        # Set _report based on data and default
        if data is True:
            self._report = lambda n, nbr, dd : (n, nbr, dd)
        elif data is False:
            self._report = lambda n, nbr, dd : (n, nbr)
        else:  # data is attribute name
            self._report = lambda n, nbr, dd : \
                    (n, nbr, dd[data]) if data in dd else (n, nbr, default)

    def __iter__(self):
        return (self._report(n, nbr, dd) for n, nbrs in self._nodes_nbrs \
                for nbr, dd in nbrs.items())

    def __contains__(self, e):
        try:
            u,v = e[:2]
            ddict = self._adjdict[u][v]
        except KeyError:
            return False
        except ValueError:
            raise ValueError("Edge must have at least 2 entries")
        return e == self._report(u, v, ddict)

    def __repr__(self):
        return "{0.__class__.__name__}({1!r})".format(self, list(self))

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs)
    # Needed for Python 3.3 which doesn't have KeysView define 
    # right set operations __rsub__ _rxor__ __rand__ __ror__
    __rand__ = KeysView.__and__
    __ror__ = KeysView.__or__
    __rxor__ = KeysView.__xor__
    def __rsub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable(e for e in other if e not in self)

class EdgeView(OutEdgeView):
    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs:
            for nbr, dd in nbrs.items():
                if nbr not in seen:
                    yield self._report(n, nbr, dd)
            seen[n] = 1
        del seen

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs) // 2

class InEdgeView(OutEdgeView):
    def __init__(self, graph, nbunch=None, data=False, default=None):
        self._adjdict = ADJ = graph.pred
        if nbunch is None:
            self._nodes_nbrs = ADJ.items()
        else:
            # This is in __init__ b/c nbunch may be an iterator and get used up 
            self._nodes_nbrs = [(n, ADJ[n]) for n in graph.nbunch_iter(nbunch)]
        # Set _report based on data and default
        if data is True:
            self._report = lambda n, nbr, dd : (nbr, n, dd)
        elif data is False:
            self._report = lambda n, nbr, dd : (nbr, n)
        else:  # data is attribute name
            self._report = lambda n, nbr, dd : \
                    (nbr, n, dd[data]) if data in dd else (nbr, n, default)

    def __contains__(self, e):
        try:
            u,v = e[:2]
            ddict = self._adjdict[v][u]
        except KeyError:
            return False
        except ValueError:
            raise ValueError("Edge must have at least 2 entries")
        return e == self._report(v, u, ddict)

class OutMultiEdgeView(OutEdgeView):
    def __init__(self, graph, nbunch=None, data=False, keys=False, default=None):
        self._adjdict = ADJ = graph.succ if hasattr(graph, 'succ') else graph.adj
        self.keys = keys
        if nbunch is None:
            self._nodes_nbrs = ADJ.items()
        else:
            # This is in __init__ b/c nbunch may be an iterator and get used up 
            self._nodes_nbrs = [(n, ADJ[n]) for n in graph.nbunch_iter(nbunch)]
        # Set _report based on data and default
        if data is True:
            if keys is True:
                self._report = lambda n, nbr, k, dd : (n, nbr, k, dd)
            else:
                self._report = lambda n, nbr, k, dd : (n, nbr, dd)
        elif data is False:
            if keys is True:
                self._report = lambda n, nbr, k, dd : (n, nbr, k)
            else:
                self._report = lambda n, nbr, k, dd : (n, nbr)
        else:  # data is attribute name
            if keys is True:
                self._report = lambda n, nbr, k, dd : (n, nbr, k, dd[data]) \
                        if data in dd else (n, nbr, k, default)
            else:
                self._report = lambda n, nbr, k, dd : (n, nbr, dd[data]) \
                        if data in dd else (n, nbr, default)

    def __iter__(self):
        return (self._report(n, nbr, k, dd) for n, nbrs in self._nodes_nbrs \
                for nbr, kd in nbrs.items() for k, dd in kd.items())

    def __contains__(self, e):
        u,v = e[:2]
        try:
            kdict = self._adjdict[u][v]
        except KeyError:
            return False
        if self.keys is True:
            k = e[2]
            dd = kdict[k]
            return e == self._report(u, v, k, dd)
        for k,dd in kdict.items():
            if e == self._report(u, v, k, dd):
                return True
        return False

    def __len__(self):
        return sum(len(kdict) for n,nbrs in self._nodes_nbrs \
                              for nbr,kdict in nbrs.items())

class MultiEdgeView(OutMultiEdgeView):
    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs:
            for nbr, kd in nbrs.items():
                if nbr not in seen:
                    for k, dd in kd.items():
                        yield self._report(n, nbr, k, dd)
            seen[n] = 1
        del seen

    def __len__(self):
        return sum(len(kdict) for n,nbrs in self._nodes_nbrs \
                              for nbr,kdict in nbrs.items()) // 2

class InMultiEdgeView(OutMultiEdgeView):
    def __init__(self, graph, nbunch=None, data=False, keys=False, default=None):
        self._adjdict = ADJ = graph.pred
        self.keys = keys
        if nbunch is None:
            self._nodes_nbrs = ADJ.items()
        else:
            # This is in __init__ b/c nbunch may be an iterator and get used up 
            self._nodes_nbrs = [(n, ADJ[n]) for n in graph.nbunch_iter(nbunch)]
        # Set _report based on data and default
        if data is True:
            if keys is True:
                self._report = lambda n, nbr, k, dd : (nbr, n, k, dd)
            else:
                self._report = lambda n, nbr, k, dd : (nbr, n, dd)
        elif data is False:
            if keys is True:
                self._report = lambda n, nbr, k, dd : (nbr, n, k)
            else:
                self._report = lambda n, nbr, k, dd : (nbr, n)
        else:  # data is attribute name
            if keys is True:
                self._report = lambda n, nbr, k, dd : (nbr, n, k, dd[data]) \
                        if data in dd else (n, nbr, k, default)
            else:
                self._report = lambda n, nbr, k, dd : (nbr, n, dd[data]) \
                        if data in dd else (nbr, n, default)

    def __contains__(self, e):
        v,u = e[:2]
        try:
            kdict = self._adjdict[u][v]
        except KeyError:
            return False
        if self.keys is True:
            k = e[2]
            dd = kdict[k]
            return e == self._report(u, v, k, dd)
        for k,dd in kdict.items():
            if e == self._report(u, v, k, dd):
                return True
        return False



