
import os, tempfile
from nose import SkipTest
from nose.tools import assert_raises, assert_true, assert_false

import networkx as nx
from networkx.generators.classic import barbell_graph,cycle_graph,path_graph

class TestConvertNumpy(object):
    @classmethod
    def setupClass(cls):
        global np, sp, sparse
        try:
            import numpy as np
            import scipy as sp
            import scipy.sparse as sparse
        except ImportError:
            raise SkipTest('SciPy sparse library not available.')

    def __init__(self):
        self.G1 = barbell_graph(10, 3)
        self.G2 = cycle_graph(10, create_using=nx.DiGraph())

        self.G3 = self.create_weighted(nx.Graph())
        self.G4 = self.create_weighted(nx.DiGraph())

    def create_weighted(self, G):
        g = cycle_graph(4)
        e = g.edges()
        source = [u for u,v in e]
        dest = [v for u,v in e]
        weight = [s+10 for s in source]
        ex = zip(source, dest, weight)
        G.add_weighted_edges_from(ex)
        return G

    def assert_equal(self, G1, G2):
        assert_true( sorted(G1.nodes())==sorted(G2.nodes()) )
        assert_true( sorted(G1.edges())==sorted(G2.edges()) )

    def identity_conversion(self, G, A, create_using):
        GG = nx.from_scipy_sparse_matrix(A, create_using=create_using)
        self.assert_equal(G, GG)

        GW = nx.from_whatever(A, create_using=create_using)
        self.assert_equal(G, GW)

        GI = create_using.__class__(A)
        self.assert_equal(G, GI)

        ACSR = A.tocsr()
        GI = create_using.__class__(ACSR)
        self.assert_equal(G, GI)

        ACOO = A.tocoo()
        GI = create_using.__class__(ACOO)
        self.assert_equal(G, GI)

        ACSC = A.tocsc()
        GI = create_using.__class__(ACSC)
        self.assert_equal(G, GI)

        AD = A.todense()
        GI = create_using.__class__(AD)
        self.assert_equal(G, GI)

        AA = A.toarray()
        GI = create_using.__class__(AA)
        self.assert_equal(G, GI)

    def test_shape(self):
        "Conversion from non-square sparse array."
        A = sp.sparse.lil_matrix([[1,2,3],[4,5,6]])
        assert_raises(nx.NetworkXError, nx.from_scipy_sparse_matrix, A)

    def test_identity_graph_matrix(self):
        "Conversion from graph to sparse matrix to graph."
        A = nx.to_scipy_sparse_matrix(self.G1)
        self.identity_conversion(self.G1, A, nx.Graph())

    def test_identity_digraph_matrix(self):
        "Conversion from digraph to sparse matrix to digraph."
        A = nx.to_scipy_sparse_matrix(self.G2)
        self.identity_conversion(self.G2, A, nx.DiGraph())

    def test_identity_weighted_graph_matrix(self):
        """Conversion from weighted graph to sparse matrix to weighted graph."""
        A = nx.to_scipy_sparse_matrix(self.G3)
        self.identity_conversion(self.G3, A, nx.Graph())

    def test_identity_weighted_digraph_matrix(self):
        """Conversion from weighted digraph to sparse matrix to weighted digraph."""
        A = nx.to_scipy_sparse_matrix(self.G4)
        self.identity_conversion(self.G4, A, nx.DiGraph())

    def test_nodelist(self):
        """Conversion from graph to sparse matrix to graph with nodelist."""
        P4 = path_graph(4)
        P3 = path_graph(3)
        nodelist = P3.nodes()
        A = nx.to_scipy_sparse_matrix(P4, nodelist=nodelist)
        GA = nx.Graph(A)    
        self.assert_equal(GA, P3)

        # Make nodelist ambiguous by containing duplicates.
        nodelist += [nodelist[0]]
        assert_raises(nx.NetworkXError, nx.to_numpy_matrix, P3, nodelist=nodelist)



