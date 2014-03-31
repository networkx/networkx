# -*- coding: utf-8 -*-


"""
===========
SparseGraph
===========

:Author:
    Moritz E. Beber <moritz.beber@gmail.com>
:Date:
    2014-03-19
:Copyright:
    See LICENSE.rst and the LICENSES folder for detailed information.
    Copyright |c| 2014, Moritz E. Beber, all rights reserved.
:File:
    graph.py

.. |c| unicode:: U+A9
"""


__all__ = ["SparseGraph"]


import warnings

import networkx as nx
import scipy
import scipy.sparse as sp

from itertools import (izip, count)

from .. import SCIPY_FORMATS

# TODO: think about using an pandas.index or ndarray
# impacts many iterators
class SparseGraph(object):
    """
    Base class for undirected sparse matrix graphs.

    A SparseGraph may store nodes and edges with optional data, or attributes.

    SparseGraphs hold undirected edges.  Self loops are allowed but multiple
    (parallel) edges are not.

    Nodes can be arbitrary (hashable) Python objects with optional
    key/value attributes if a node list is desired. Otherwise they simply reduce
    to indexes of the sparse matrix.

    The sparse matrix represents the edges in the graph. The convention followed
    here is that if there is an edge between `i` and `j` there is an entry in
    the adjacency matrix `A_{ij} = 1`.

    Edges can have additional key/value attributes although this is memory
    intensive and discouraged for large graphs.

    Note
    ----
    If you are interested in storing edge weights in the matrix, refer to
    SparseMultiGraph.

    Parameters
    ----------
    data : input graph
        Data to initialize the graph.  If data=None (default) an empty
        graph is created.  The data can be an edge list, any
        NetworkX graph object, a numpy matrix, numpy 2d ndarray or any of the
        SciPy sparse matrices.
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to the graph attributes as key=value pairs.

    See Also
    --------
    SparseDiGraph
    SparseMultiGraph
    SparseMultiDiGraph
    """
    def __init__(self, data=None, nodelist=None, dtype=None, format="csr",
            copy=True, **attr):
        """Initialize a sparse graph with edges, name and graph attributes.

        Parameters
        ----------
        data : input graph
            Data to initialize the graph.  If data=None (default) an empty
            graph is created.  The data can be an edge list, any
            NetworkX graph object, a numpy matrix, numpy 2d ndarray or any of the
            SciPy sparse matrices.
        nodelist : int or nodes (optional)
            When data is supplied, this will attempt to use nodes in the order
            of the list from that structure only. If no data is specified, the
            list is used as an index to the matrix which is constructed with
            dimensions len(nodelist) x len(nodelist). If nodelist is an int, the
            matrix will have dimensions nodelist x nodelist.
        dtype : (optional)
            Force the data type of the constructed matrix. The default is either
            deduced from the input or scipy.int32 is used.
        copy : bool (optional)
            If data is given, either copy the structure (default) or use the
            data directly (in case of a sparse matrix).
        attr : (optional)
            Keyword arguments (default no attributes) to add to the graph
            attributes as key=value pairs.
        """
        super(SparseGraph, self).__init__()
        self.graph = attr
        self.node = dict()
        self.matrix = None
        self.edge = self.adj # maybe defer that
        if data is not None:
            self.to_sparse_graph(data, nodelist, dtype, format, copy)
        else:
            if nodelist:
                self.matrix = SCIPY_FORMATS[format]
            else:
                self.matrix = SCIPY_FORMATS[format]

    @property
    def name(self):
        return self.graph.get("name", "")
    @name.setter
    def name(self, s):
        self.graph["name"] = s

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.node)

    @property
    def adj(self):
#        return dict((n,Adjacency(n, self.matrix)) for n in self.node)
        return

    def _add_node_attr(self, n, attr_dict=None, **attr):
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise nx.NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        if n not in self.node:
            self.node[n] = attr_dict
        else:
            self.node[n].update(attr_dict)

    def add_node(self, n, attr_dict=None, **attr):
        if not isinstance(n, (int, scipy.integer)):
            raise NotImplementedError("Non-integer nodes are not possible at"\
                    " the moment.")
        if n > 0 and n < self.matrix.shape[0]:
            self._add_node_attr(n, attr_dict, **attr)
            return # index within known bounds, nothing to add
        if isinstance(self.matrix, (sp.csr_matrix, sp.csc_matrix, sp.dia_matrix,
                sp.bsr_matrix)):
            raise nx.NetworkXError("Please convert to a different storage"\
                    " system while changing the adjacency.")
        dim = self.matrix.shape
        if isinstance(self.matrix, sp.dok_matrix):
            self.matrix.resize((dim[0] + 1, dim[1] + 1))
            self._add_node_attr(n, attr_dict, **attr)
        if isinstance(self.matrix, sp.lil_matrix):
            self.matrix.reshape((dim[0] + 1, dim[1] + 1))
            self._add_node_attr(n, attr_dict, **attr)
        if isinstance(self.matrix, sp.coo_matrix):
            self.matrix = sp.coo_matrix((self.matrix.data, (self.matrix.row,
                self.matrix.col)), (dim[0] + 1, dim[1] + 1))
            self._add_node_attr(n, attr_dict, **attr)

    def to_sparse_graph(self, data, nodelist, dtype, format, copy):
        """Create a SparseGraph from a known data structure.

        The preferred way to call this is automatically
        from the class constructor.

        >>> g = nx.Graph({0: {1: {'weight':1}}}) # dict-of-dicts single edge (0,1)
        >>> sg = nx.SparseGraph(g)

        Parameters
        ----------
        data : a object to be converted
           Current known types are:
             any NetworkX graph
             dict-of-dicts
             dist-of-lists
             list of edges
             numpy.matrix
             numpy.ndarray
             scipy sparse matrix
        Also see SparseGraph init parameters.

        """
        # nx graph
        if isinstance(data, nx.Graph):
            self.__class__.from_nx_graph(data, nodelist, dtype, format,
                    create_using=self)
            return
        # dict interfaces
        import collections
        if isinstance(data, collections.Mapping):
            val = next(data.itervalues())
            if isinstance(val, collections.Mapping):
                self.__class__.from_dict_of_dicts(data, nodelist, dtype, format,
                        create_using=self)
                return
            elif isinstance(val, collections.Iterable):
                self.__class__.from_dict_of_lists(data, nodelist, dtype, format,
                        create_using=self)
                return
            else:
                raise nx.NetworkXError("Unknown dict structure")
        if isinstance(data, collections.Iterable):
            self.__class__.from_edgelist(data, nodelist, dtype, format,
                    create_using=self)
            return
        import numpy
        from numpy.ma import MaskedArray
        if isinstance(data, (numpy.ndarray, MaskedArray, numpy.matrix)):
            self.__class__.from_numpy_matrix(data, nodelist, dtype, format,
                    create_using=self)
            return
        if sp.isspmatrix(data):
            self.__class__.from_scipy_matrix(data, nodelist, dtype, format,
                    create_using=self)
            return
        raise nx.NetworkXError("Input is not a known data type for conversion.")

    @classmethod
    def from_nx_graph(cls, data, nodelist, dtype, format, create_using=None):
        """Create a SparseGraph from a networkx graph.

        The preferred way to call this is automatically
        from the class constructor

        >>> g = nx.Graph({0: {1: {'weight':1}}}) # dict-of-dicts single edge (0,1)
        >>> sg = nx.SparseGraph(g)

        instead of the equivalent

        >>> G = nx.SparseGraph.from_nx_graph(g)

        Parameters
        ----------
        See SparseGraph init parameters.

        """
        if data.is_directed():
            warnings.warn("Attempting to instantiate a SparseGraph"\
                    " with a directed graph.")
        if data.is_multigraph():
            warnings.warn("Attempting to instantiate a SparseGraph"\
                    " with a multi graph.")
        num_nodes = data.number_of_nodes()
        if isinstance(nodelist, int):
            if num_nodes > nodelist:
                warnings.warn("Shortened graph due to dimension specification.")
            dim = (nodelist, nodelist)
            nodelist = sorted(data.nodes_iter())[:nodelist]
        elif nodelist is not None:
            if len(nodelist) != len(set(nodelist)):
                raise nx.NetworkXError("Ambiguous ordering: 'nodelist'"\
                        " contains duplicates.")
            if len(nodelist) > num_nodes:
                warnings.warn("'nodelist' contains more nodes than the graph;"\
                        " some nodes will be ignored")
            num_nodes = min(num_nodes, len(nodelist))
            dim = (num_nodes, num_nodes)
        else:
            nodelist = sorted(data.nodes_iter())
            dim = (num_nodes, num_nodes)
        index = dict(izip(nodelist, count()))
        (row, col, data, edge) = zip(*[(index[u], index[v], 1, d)\
                for (u, v, d) in data.edges_iter(nodelist, data=True)\
                if u in index and v in index])
        if create_using is not None:
            sparse = create_using
        else:
            sparse = cls()
        if any(edge):
            sparse.edge = edge
        dtype = scipy.int32 if dtype is None else dtype
        matrix = sp.coo_matrix((data + data, (row + col, col + row)),
                shape=dim, dtype=dtype)
        try:
            sparse.matrix = SCIPY_FORMATS[format](matrix)
        except KeyError:
            raise nx.NetworkXError("Unknown sparse matrix format '%s'."\
                    % (format,))

