#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx

# Example from
# A. Langville and C. Meyer, "A survey of eigenvector methods of web
# information retrieval."  http://citeseer.ist.psu.edu/713792.html


class TestHITS:

    def setUp(self):
        
        G=networkx.DiGraph()

        edges=[(1,3),(1,5),\
           (2,1),\
           (3,5),\
           (5,4),(5,3),\
           (6,5)]
           
        G.add_edges_from(edges,weight=1)
        self.G=G
        self.G.h=[0.000000, 0.000000, 0.211325, 
                  0.211325, 0.211325, 0.366025]

        self.G.a=[0.000000, 0.000000, 0.000000, 
                  0.133975, 0.366025, 0.500000]        


    def test_hits(self):
        G=self.G
        h,a=networkx.hits(G,tol=1.e-08)
        for (x,y) in zip(sorted(h.values()),self.G.h):
            assert_almost_equal(x,y,places=5)
        for (x,y) in zip(sorted(a.values()),self.G.a):
            assert_almost_equal(x,y,places=5)


    def test_numpy_hits(self):
        G=self.G
        try:
            import numpy
        except ImportError:
            raise SkipTest('numpy not available.')
        
        h,a=networkx.hits_numpy(G,tol=1.e-08)
        for (x,y) in zip(sorted(h),self.G.h):
            assert_almost_equal(x,y,places=5)
        for (x,y) in zip(sorted(a),self.G.a):
            assert_almost_equal(x,y,places=5)

    def test_hubs_authority_matrix(self):
        G=self.G
        try:
            import numpy
            import numpy.linalg
        except ImportError:
            raise SkipTest('numpy not available.')

        H=networkx.hub_matrix(G,nodelist=None)
        e,ev=numpy.linalg.eig(H)
        m=e.argsort()[-1] # index of maximum eigenvalue
        h=numpy.array(ev[:,m]).flatten()

        A=networkx.authority_matrix(G,nodelist=None)
        e,ev=numpy.linalg.eig(A)
        m=e.argsort()[-1] # index of maximum eigenvalue
        a=numpy.array(ev[:,m]).flatten()
        h=h/h.sum()
        a=a/a.sum()
        h,a=networkx.hits_scipy(G,tol=1.e-08)
        for (x,y) in zip(sorted(h),self.G.h):
            assert_almost_equal(x,y,places=5)
        for (x,y) in zip(sorted(a),self.G.a):
            assert_almost_equal(x,y,places=5)

    def test_scipy_hits(self):
        G=self.G
        try:
            import scipy
        except ImportError:
            raise SkipTest('scipy not available.')
        h,a=networkx.hits_scipy(G,tol=1.e-08)
        for (x,y) in zip(sorted(h),self.G.h):
            assert_almost_equal(x,y,places=5)
        for (x,y) in zip(sorted(a),self.G.a):
            assert_almost_equal(x,y,places=5)



