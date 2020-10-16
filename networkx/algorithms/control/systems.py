"""Classes for networked control systems."""
import networkx as nx
import numpy as np
from itertools import combinations


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

    def construct_controllability_matrix(self):
        """Return the controllability matrix for the given system."""
        n = self.A.shape[0]
        m = self.B.shape[1]

        C = np.zeros((n, n * m))
        for i in range(n):
            C[:, i*m:(i+1)*m] = self.A ** i @ self.B
        return C

    def is_controllable(self):
        """Check if the system is controllable via Kalman's rank test."""
        C = self.construct_controllability_matrix()
        rank = np.linalg.matrix_rank(C)
        return self.A.shape[0] == rank

    def is_inaccessible(self):
        """Check if any states are inaccessible from the inputs."""
        total_reachable = set()
        for input_node in self.input_nodes:
            reachable = nx.single_source_shortest_path_length(self.G,
                                                              input_node).keys()
            total_reachable = total_reachable.union(reachable)
        reachable_states = total_reachable.intersection(self.state_nodes)
        return len(reachable_states) < len(self.state_nodes)

    def contains_dilation(self):
        """Check if the system contains a dilation.

        A dilation is defined as a subset of the state nodes S
        such that the neighborhood set T(S) contains fewer nodes than S itself.
        """
        incoming_neighbors = [list(self.G.predecessors(node))
                              for node in self.state_nodes]
        for i in range(1, len(self.state_nodes) + 1):
            for neighbors in combinations(incoming_neighbors, i):
                neighborhood_set = set().union(*neighbors)
                if len(neighborhood_set) < i:
                    return True
        return False

    def is_structurally_controllable(self):
        """
        Check if the system is structurally controllable based on
        Lin's structural controllability test.

        A system is structurally controllable if and only if
        it contains no inaccessible state nodes or dilations.

        This test ignores the weights and only focuses on the topology
        of the underlying graph of the system.
        """
        return not self.is_inaccessible() and not self.contains_dilation()
