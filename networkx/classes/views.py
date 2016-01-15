"""
Classes to provide node and edge "views" of a graph.

The "views" do not copy any data yet are iterable containers
of the nodes or edges of the graph. They are updated as the 
graph is updated, so updating the graph while iterating through
the view is not permitted.

Views V allow "len(V)", "e in V", "str(V)" and set operations "V1 & V2".
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

__all__ = ['NodeView', 'EdgeView', 'DiEdgeView', 'InDiEdgeView',
           'MultiEdgeView', 'MultiDiEdgeView', 'InMultiDiEdgeView']

class NodeView(object):
    """A View class for nodes of a NetworkX Graph

    Parameters
    ==========
    nodedict : dict
        The node dict for the graph. Typically G.node
    data : bool or string (default=False)
    default : object (default=None)
    """
    def __init__(self, graph, data=False, default=None):
        self.G = graph
        self.node = graph.node
        self.data = data
        self.default = default
    def __iter__(self):
        data=self.data
        if data is True:
            return iter(self.node.items())
        if data is False:
            return iter(self.node)
        default = self.default
        return ((n, dd.get(data, default)) for n, dd in self.node.items())
    def __str__(self):
        if self.data is False:
            return str(list(self.node.keys()))
        if self.data is True:
            return str(list(self.node.items()))
        return str(dict(self))
    def __contains__(self, n):
        try:
            return n in self.node
        except TypeError:
            n, d = n
            return n in self.node and self.node[n]==d
    def __len__(self):
        return len(self.node)
    def __and__(self, other):
        return set(self.node) & set(other)
    def __or__(self, other):
        return set(self.node) | set(other)
    def __xor__(self, other):
        return set(self.node) ^ set(other)
    def __sub__(self, other):
        return set(self.node) - set(other)


class EdgeView(object):
    def __init__(self, graph, nbunch=None, data=False, default=None):
        self.G = G = graph
        self.adjdict = G.adj
        self.nbunch = nbunch
        self.data = data
        self.default = default
        if nbunch is None:
            self.nodes_nbrs = G.adj.items()
        else:
            self.nodes_nbrs = [(n, G.adj[n]) for n in G.nbunch_iter(nbunch)]
    def __iter__(self):
        seen = {}
        data = self.data
        if data is True:
            for n, nbrs in self.nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    if nbr not in seen:
                        yield (n, nbr, ddict)
                seen[n] = 1
        elif data is not False:
            default = self.default
            for n, nbrs in self.nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    if nbr not in seen:
                        d = ddict[data] if data in ddict else default
                        yield (n, nbr, d)
                seen[n] = 1
        else:  # data is False
            for n, nbrs in self.nodes_nbrs:
                for nbr in nbrs:
                    if nbr not in seen:
                        yield (n, nbr)
                seen[n] = 1
        del seen
    def __str__(self):
        return str(list(self))
    def __contains__(self, e):
        n = len(e)
        if n == 2:
            u,v = e
            try:
                return v in self.adjdict[u]
            except KeyError:
                return False
        if n == 3:
            u,v,d = e
            try:
                return d == self.adjdict[u][v]
            except KeyError:
                return False
        raise TypeError("edge must be a 2-tuple or a 3-tuple")
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self.nodes_nbrs) // 2
    def __and__(self, other):
        return set(self) & set(other)
    def __or__(self, other):
        return set(self) | set(other)
    def __xor__(self, other):
        return set(self) ^ set(other)
    def __sub__(self, other):
        return set(self) - set(other)

class DiEdgeView(EdgeView):
    def __iter__(self):
        data = self.data
        if data is True:
            for n, nbrs in self.nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    yield (n, nbr, ddict)
        elif data is not False:
            default = self.default
            for n, nbrs in self.nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    d = ddict[data] if data in ddict else default
                    yield (n, nbr, d)
        else:  # data is False
            for n, nbrs in self.nodes_nbrs:
                for nbr in nbrs:
                    yield (n, nbr)
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self.nodes_nbrs)

class InDiEdgeView(DiEdgeView):
    def __init__(self, graph, nbunch=None, data=False, default=None):
        self.G = G = graph
        self.adjdict = G.pred
        self.nbunch = nbunch
        self.data = data
        self.default = default
        if nbunch is None:
            self.nodes_nbrs = G.pred.items()
        else:
            self.nodes_nbrs = [(n, G.pred[n]) for n in G.nbunch_iter(nbunch)]
    def __iter__(self):
        data = self.data
        if data is True:
            for n, nbrs in self.nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    yield (nbr, n, ddict)
        elif data is not False:
            default = self.default
            for n, nbrs in self.nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    d = ddict[data] if data in ddict else default
                    yield (nbr, n, d)
        else:  # data is False
            for n, nbrs in self.nodes_nbrs:
                for nbr in nbrs:
                    yield (nbr, n)
    

class MultiEdgeView(EdgeView):
    def __init__(self, graph, nbunch=None, keys=False,
                 data=False, default=None):
        super(MultiEdgeView, self).__init__(graph, nbunch, data, default)
        self.keys = keys
    def __iter__(self):
        seen = {}
        data = self.data
        keys = self.keys
        if data is True:
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key, ddict in keydict.items():
                            if keys:
                                yield (n, nbr, key, ddict)
                            else:
                                yield (n, nbr, ddict)
                seen[n] = 1
        elif data is not False:
            default = self.default
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key, ddict in keydict.items():
                            d = ddict[data] if data in ddict else default
                            yield (n, nbr, key, d) if keys else (n, nbr, d)
                seen[n] = 1
        else:
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key in keydict:
                            yield (n, nbr, key) if keys else (n, nbr)
                seen[n] = 1
        del seen

class MultiDiEdgeView(MultiEdgeView):
    def __iter__(self):
        data = self.data
        keys = self.keys
        if data is True:
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, ddict in keydict.items():
                        yield (n, nbr, key, ddict) if keys else (n, nbr, ddict)
        elif data is not False:
            default = self.default
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, ddict in keydict.items():
                        d = ddict[data] if data in ddict else default
                        yield (n, nbr, key, d) if keys else (n, nbr, d)
        else:
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key in keydict:
                        yield (n, nbr, key) if keys else (n, nbr)

class InMultiDiEdgeView(InDiEdgeView):
    def __init__(self, graph, nbunch=None, keys=False, data=False, default=None):
        self.G = G = graph
        self.adjdict = G.pred
        self.nbunch = nbunch
        self.keys = keys
        self.data = data
        self.default = default
        if nbunch is None:
            self.nodes_nbrs = G.pred.items()
        else:
            self.nodes_nbrs = [(n, G.pred[n]) for n in G.nbunch_iter(nbunch)]
    def __iter__(self):
        # Same as for MultiDiEdgeView but order switched due to pred adjdict
        data = self.data
        keys = self.keys
        if data is True:
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, ddict in keydict.items():
                        yield (nbr, n, key, ddict) if keys else (nbr, n, ddict)
        elif data is not False:
            default = self.default
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, ddict in keydict.items():
                        d = ddict[data] if data in ddict else default
                        yield (nbr, n, key, d) if keys else (nbr, n, d)
        else:
            for n, nbrs in self.nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key in keydict:
                        yield (nbr, n, key) if keys else (nbr, n)
