import networkx as nx
import numpy as np


def test_lti_system():
    A = np.array([[0, 0, 0, 0, 0],
                  [1, 0, 0, 0, 0],
                  [2, 0, 0, 0, 0],
                  [-1, 0, 3, 0, 0],
                  [0, 0, 0, 0, 4]])
    B = np.array([[5, 0],
                  [0, -2],
                  [0, 0],
                  [0, 0],
                  [0, 6]])
    sys = nx.algorithms.control.systems.LTISystem(A, B,
                                                  state_prefix='x',
                                                  input_prefix='u')

    states = ['x{}'.format(i) for i in range(A.shape[0])]
    inputs = ['u{}'.format(i) for i in range(B.shape[1])]
    edges = [('x0', 'x1'), ('x0', 'x2'), ('x0', 'x3'), ('x2', 'x3'),
             ('x4', 'x4'), ('u0', 'x0'), ('u1', 'x1'), ('u1', 'x4')]
    edge_data = [('x0', 'x1', 1), ('x0', 'x2', 2), ('x0', 'x3', -1),
                 ('x2', 'x3', 3), ('x4', 'x4', 4), ('u0', 'x0', 5),
                 ('u1', 'x1', -2), ('u1', 'x4', 6)]

    assert sys.state_nodes == states
    assert sys.input_nodes == inputs
    assert list(sys.G.nodes) == states + inputs
    assert [e for e in sys.G.edges] == edges
    assert list(sys.G.edges.data('weight')) == edge_data

    G_A = nx.adjacency_matrix(sys.G, nodelist=states).todense().T
    G_B = nx.adjacency_matrix(sys.G).todense().T[:len(states), -len(inputs):]
    assert (G_A == A).all()
    assert (G_B == B).all()


if __name__ == '__main__':
    test_lti_system()
