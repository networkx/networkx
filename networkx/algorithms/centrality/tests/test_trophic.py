"""Unit tests for trophic measures
"""
import networkx as nx
import numpy as np
from networkx.testing import almost_equal
from nose.tools import raises


class TestTrophicMeasures:
    def test_trophic_levels(self):
        # trivial example
        G = nx.DiGraph()
        G.add_edge("a", "b")
        G.add_edge("b", "c")

        d = nx.trophic_levels(G)
        assert d == {"a": 1, "b": 2, "c": 3}

        # example from Stephen Levine (1980) J. theor. Biol. 83, 195-207
        # figure 5
        S = nx.DiGraph()
        S.add_edge(1, 2, weight=1.0)
        S.add_edge(1, 3, weight=0.2)
        S.add_edge(1, 4, weight=0.8)
        S.add_edge(2, 3, weight=0.2)
        S.add_edge(2, 5, weight=0.3)
        S.add_edge(4, 3, weight=0.6)
        S.add_edge(4, 5, weight=0.7)
        S.add_edge(5, 4, weight=0.2)

        # save copy for later, test intermediate implementation details first
        S2 = S.copy()

        # drop nodes of in-degree zero
        z = [nid for nid, d in S.in_degree if d == 0]
        for nid in z:
            S.remove_node(nid)

        # find adjacency matrix
        q = nx.linalg.graphmatrix.adjacency_matrix(S).T

        expected_q = np.array([
            [0. , 0. , 0. , 0. ],
            [0.2, 0. , 0.6, 0. ],
            [0. , 0. , 0. , 0.2],
            [0.3, 0. , 0.7, 0. ]
        ])
        assert np.array_equal(q.todense(), expected_q)

        # must be square, size of number of nodes
        assert len(q.shape) == 2
        assert q.shape[0] == q.shape[1]
        assert q.shape[0] == len(S)

        nn = q.shape[0]

        i = np.eye(nn)
        n = np.linalg.inv(i - q)
        y = np.dot(np.asarray(n), np.ones(nn))

        expected_y = np.array([1., 2.07906977, 1.46511628, 2.3255814])
        assert np.allclose(y, expected_y)

        expected_d = {
            1: 1,
            2: 2,
            3: 3.07906977,
            4: 2.46511628,
            5: 3.3255814
        }

        d = nx.trophic_levels(S2)

        for nid, level in d.items():
            expected_level = expected_d[nid]
            assert almost_equal(expected_level, level)

    def test_trophic_levels_simple(self):

        matrix_a = np.array([[0,0],[1,0]])
        G = nx.from_numpy_matrix(matrix_a, create_using=nx.DiGraph)
        d = nx.trophic_levels(G)
        assert almost_equal(d[0], 2)
        assert almost_equal(d[1], 1)
        
    def test_trophic_levels_more_complex(self):

        matrix = np.array([[0,1,0,0],
            [0,0,1,0],
            [0,0,0,1],
            [0,0,0,0]])
        G = nx.from_numpy_matrix(matrix, create_using=nx.DiGraph)
        d = nx.trophic_levels(G)
        expected_result = [1,2,3,4]
        for ind in range(4):
            assert almost_equal(d[ind], expected_result[ind])


        matrix = np.array([[0,1,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [0,0,0,0]])
        G = nx.from_numpy_matrix(matrix, create_using=nx.DiGraph)
        d = nx.trophic_levels(G)

        expected_result = [1,2,2.5,3.25]
        print("Calculated result: ", d)
        print("Expected Result: ", expected_result)
        
        for ind in range(4):
            assert almost_equal(d[ind], expected_result[ind])

    def test_trophic_levels_even_more_complex(self):


        # Another, bigger matrix
        matrix = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]])

        # Generated this linear system using pen and paper:
        K = np.matrix([
        [1, 0,  -1,0,   0],
        [0, .5, 0,  -.5,    0],
        [0, 0,  1,  0,      0],
        [0, -.5,0,  1,      -.5],
        [0, 0,  0,  0,      1],
        ])
        result_1 = np.ravel(np.matmul(np.linalg.inv(K), np.ones(5)))
        G = nx.from_numpy_matrix(matrix, create_using=nx.DiGraph)
        result_2 = nx.trophic_levels(G)

        for ind in range(5):
            assert almost_equal(result_1[ind], result_2[ind])        

    # Check it raises the correct error with graphs with only non-basal nodes
    @raises(np.linalg.LinAlgError)
    def test_singular_matrix(self):

        matrix = np.identity(4)
        G = nx.from_numpy_matrix(matrix, create_using=nx.DiGraph)
        result = nx.trophic_levels(G)        