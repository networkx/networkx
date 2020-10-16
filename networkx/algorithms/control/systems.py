"""Classes for networked control systems."""
import networkx as nx


class LTISystem:
    """
    Linear time-invariant system whose dynamics
    are defined by matrices A and B.

    Constructs an underlying (weighted) directed graph of the system
    based on the given matrices.
    """
    def __init__(self, A, B,
                 state_prefix='x', input_prefix='u'):
        self.A = A
        self.B = B

        self.G = nx.DiGraph()
        self.state_nodes = [state_prefix + '{}'.format(i) for i in range(A.shape[0])]
        self.input_nodes = [input_prefix + '{}'.format(i) for i in range(B.shape[1])]
        self.G.add_nodes_from(self.state_nodes)
        self.G.add_nodes_from(self.input_nodes)

        # Edges are defined from col to row
        edges = []
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if A[i, j] != 0:
                    edge = (self.state_nodes[j], self.state_nodes[i], A[i, j])
                    edges.append(edge)
        for i in range(B.shape[0]):
            for j in range(B.shape[1]):
                if B[i, j] != 0:
                    edge = (self.input_nodes[j], self.state_nodes[i], B[i, j])
                    edges.append(edge)
        self.G.add_weighted_edges_from(edges)
