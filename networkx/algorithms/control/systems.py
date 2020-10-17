"""Classes for networked control systems."""
import networkx as nx
import numpy as np
from itertools import combinations


def create_bipartite_from_directed_graph(G):
    """Create a bipartite graph from a directed graph.

    Adds in and out nodes for each node of the graph.
    """
    in_nodes = [node + '-' for node in G.nodes]
    out_nodes = [node + '+' for node in G.nodes]
    edges = []
    for u, v in G.edges:
        edges.append((u + '+', v + '-'))
    H = nx.Graph()
    H.add_nodes_from(out_nodes, bipartite=0)
    H.add_nodes_from(in_nodes, bipartite=1)
    H.add_edges_from(edges)
    return H


def convert_bipartite_edges_to_original(edges):
    """
    Convert bipartite edges to original edges by removing
    the in (-) and out (+) specification in the string name.
    """
    return [(u[:-1], v[:-1]) for u, v in edges]


def find_matchings(G, t, selfloops=True):
    """Find matchings in a given graph.

    A matching is defined as a set of edges such that no edges share
    any vertices. t specifies the sizes of such matchings to search for.
    """
    matchings = []
    if selfloops:
        all_edges = G.edges
    else:
        all_edges = [(u, v) for (u, v) in G.edges if u[:-1] != v[:-1]]
    for edges in combinations(all_edges, t):
        if nx.is_matching(G, edges):
            matchings.append(edges)
    return matchings


def has_t_constrained_matching(G, t, selfloops=True):
    """Check if a graph contains a t-constrained matching.

    A t-matching is contrained if it is the only such matching of size t.
    """
    matchings = find_matchings(G, t, selfloops=selfloops)
    if len(matchings) == 0 or len(matchings) > 1:
        return False
    return True


def add_self_loops(G):
    """Add self loops to all nodes of G."""
    G = G.copy()
    for node in G.nodes:
        G.add_edge(node, node)
    return G


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

    def is_strongly_structurally_controllable(self):
        """
        Check if the system is strongly structurally controllable based on
        bipartite matchings.

        A system is strongly structurally controllably if and only if
        the bipartite representation of the system has a constrained
        (n - m) matching, and the bipartite representation of the system
        with self-loops added has a constrained self-loop-less (n - m) matching.
        """
        n = len(self.state_nodes)
        m = len(self.input_nodes)
        G_no_inputs = self.G.subgraph(self.state_nodes)
        H = create_bipartite_from_directed_graph(G_no_inputs)
        if not has_t_constrained_matching(H, n - m, selfloops=True):
            return False
        G_x = add_self_loops(G_no_inputs)
        H_x = create_bipartite_from_directed_graph(G_x)
        return has_t_constrained_matching(H_x, n - m, selfloops=False)

    def find_minimum_driver_nodes(self):
        """Find a minimum set of driver nodes for the system.

        Driver nodes are a set of nodes that when driven by different signals,
        can control the entire network.
        """
        G_no_inputs = self.G.subgraph(self.state_nodes)
        H = create_bipartite_from_directed_graph(G_no_inputs)
        max_matching = nx.maximal_matching(H)
        max_matching = convert_bipartite_edges_to_original(max_matching)
        matched_nodes = [v for u, v in max_matching]
        unmatched_nodes = set(self.state_nodes).difference(matched_nodes)
        return unmatched_nodes

    def is_controllable_pbh(self):
        """
        Check if system is controllable via the
        Popov-Belevitch-Hautus (PBH) test.
        """
        n = self.A.shape[0]
        m = self.B.shape[1]
        D = np.zeros((n, n + m))
        D[:, n:] = self.B
        evals, evecs = np.linalg.eig(self.A)
        for val in evals:
            D[:, :n] = val * np.eye(n) - self.A
            rank = np.linalg.matrix_rank(D)
            if rank != n:
                return False
        return True
