"""Classes for networked control systems."""
import networkx as nx
import numpy as np
from itertools import combinations, product


def create_bipartite_from_directed_graph(G):
    """Create a bipartite representation of a directed graph.

    Creates a bipartite representation of a directed graph by adding two nodes
    $x_i^+$ and $x_i^-$ per each node $x_i$ in the original graph,
    corresponding to the incoming and and outgoing edges, respectively.
    Then, given an edge $(x_i \\to x_j)$ in the original directed graph,
    the edge $(x_i^+, x_j^-)$ is added to the bipartite graph.

    Parameters
    ----------
    G : NetworkX graph
        Directed graph

    Returns
    -------
    bipartite : Graph
        The bipartite representation of the graph

    Notes
    -----
    Definition comes from [1]_. This formulation results in a bipartite graph
    between the two partitions of
    $\{x_1^+, \ldots, x_n^+\} \cup \{x_1^-, \ldots x_n^-\}$.

    References
    ----------
    .. [1] Liu, Y. Y., Slotine, J. J., & Barabási, A. L. (2011).
        Controllability of complex networks.
        Nature, 473(7346), 167-173.
        https://doi.org/10.1038/nature10011
    """
    in_nodes = [node + "-" for node in G.nodes]
    out_nodes = [node + "+" for node in G.nodes]
    edges = []
    for u, v in G.edges:
        edges.append((u + "+", v + "-"))
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


def find_maximum_matchings(G):
    """Find the sets of maximum matchings for a given graph."""
    for t in range(len(G.edges) + 1, 0, -1):
        matchings = find_matchings(G, t)
        if len(matchings) > 0:
            return matchings
    return matchings


def convert_matching_to_nodes(matching, all_nodes, from_bipartite=False):
    """Convert a list of matching edges to matched and unmatched nodes.

    A vertex is matched if it is the end of an edge in the matching.
    """
    if from_bipartite:
        matching = convert_bipartite_edges_to_original(matching)
    matched = set()
    for u, v in matching:
        matched.add(v)
    unmatched = set(all_nodes).difference(matched)
    return matched, unmatched


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

    def __init__(self, A, B, state_prefix="x", input_prefix="u"):
        self.A = A
        self.B = B

        self.G = nx.DiGraph()
        self.state_nodes = [state_prefix + "{}".format(i) for i in range(A.shape[0])]
        self.input_nodes = [input_prefix + "{}".format(i) for i in range(B.shape[1])]
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
            C[:, i * m : (i + 1) * m] = self.A ** i @ self.B
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
            reachable = nx.single_source_shortest_path_length(self.G, input_node).keys()
            total_reachable = total_reachable.union(reachable)
        reachable_states = total_reachable.intersection(self.state_nodes)
        return len(reachable_states) < len(self.state_nodes)

    def contains_dilation(self):
        """Check if the system contains a dilation.

        A dilation is defined as a subset of the state nodes S
        such that the neighborhood set T(S) contains fewer nodes than S itself.
        """
        incoming_neighbors = [
            list(self.G.predecessors(node)) for node in self.state_nodes
        ]
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
        max_matching = find_maximum_matchings(H)[0]
        _, unmatched = convert_matching_to_nodes(
            max_matching, self.state_nodes, from_bipartite=True
        )
        return unmatched

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

    def find_minimum_actuators(self):
        """Find a minimum set of actuators of the system.

        Implementation is based on
        [Pequito et al. 2013](https://doi.org/10.1109/ACC.2013.6580796).
        """
        G = self.G.subgraph(self.state_nodes)
        scc_dag = nx.condensation(G)
        node_to_scc = scc_dag.graph["mapping"]
        scc_to_nodes = {}
        for node, scc in node_to_scc.items():
            if scc not in scc_to_nodes:
                scc_to_nodes[scc] = []
            scc_to_nodes[scc].append(node)
        root_scc = [u for u, in_deg in scc_dag.in_degree() if in_deg == 0]
        beta = len(root_scc)
        H = create_bipartite_from_directed_graph(G)

        max_matchings = find_maximum_matchings(H)
        alpha = 0
        top_assignable_scc = None
        for matching in max_matchings:
            matched, unmatched = convert_matching_to_nodes(
                matching, G.nodes, from_bipartite=True
            )
            assignable = set()
            # Find set of rSCCs that contain driver nodes
            for node in unmatched:
                if node_to_scc[node] in root_scc:
                    assignable.add(node_to_scc[node])
            if len(assignable) > alpha:
                alpha = len(assignable)
                top_assignable_scc = assignable

        root_scc_nodes = set()
        for scc in root_scc:
            for node in scc_to_nodes[scc]:
                root_scc_nodes.add(node)

        max_matching = max_matchings[0]
        matched, unmatched = convert_matching_to_nodes(
            max_matching, G.nodes, from_bipartite=True
        )
        n_driver_nodes = len(unmatched)

        min_num_actuators = n_driver_nodes + beta - alpha

        matched = list(matched)
        thetas = []
        for node in unmatched:
            theta = set()
            other_unmatched = unmatched.difference({node})
            bad_edges = [(u, v) for u, v in H.edges() if v[:-1] in other_unmatched]
            B = H.copy()
            B.remove_edges_from(bad_edges)
            match_lens = []
            for candidate in matched:
                bad_edges = [(u, v) for u, v in B.edges() if v[:-1] == candidate]
                B_new = B.copy()
                B_new.remove_edges_from(bad_edges)
                matching = find_maximum_matchings(B_new)[0]
                new_matches, _ = convert_matching_to_nodes(
                    matching, G.nodes, from_bipartite=True
                )
                match_lens.append(len(new_matches))
            max_len = max(match_lens)
            for i, length in enumerate(match_lens):
                if length == max_len:
                    theta.add(matched[i])
            thetas.append(theta)
        theta = set()
        for scc in root_scc:
            theta = theta.union(set(scc_to_nodes[scc]))
        thetas.append(theta)
        for nodes in product(*thetas):
            nodes = set(nodes)
            if len(nodes) < len(thetas):
                continue
            if len(nodes.intersection(root_scc_nodes)) < len(root_scc_nodes):
                continue
            return nodes
        return None

    def classify_link_importance(self):
        """Classify the importance of each edge using
        structural controllability tests.

        This implementation is generally exponential in the number of edges,
        due to the fact that all maximum matchings need to be enumerated.
        """

        G = self.G.subgraph(self.state_nodes)
        all_edges = set(G.edges())
        H = create_bipartite_from_directed_graph(G)
        max_matchings = find_maximum_matchings(H)
        matchings = []
        for matching in max_matchings:
            matching = convert_bipartite_edges_to_original(matching)
            matchings.append(set(matching))
        critical = set.intersection(*matchings)
        redundant = all_edges.difference(*matchings)
        ordinary = all_edges.difference(critical, redundant)
        return critical, redundant, ordinary

    def classify_node_importance(self):
        """
        Classify the importance of each node using
        minimum driver node tests.
        """

        G = self.G.subgraph(self.state_nodes)
        all_nodes = set(self.state_nodes)
        H = create_bipartite_from_directed_graph(G)
        max_matchings = find_maximum_matchings(H)
        all_driver_nodes = []
        for matching in max_matchings:
            _, driver_nodes = convert_matching_to_nodes(
                matching, G.nodes, from_bipartite=True
            )
            all_driver_nodes.append(driver_nodes)
        critical = set.intersection(*all_driver_nodes)
        redundant = all_nodes.difference(*all_driver_nodes)
        intermittent = all_nodes.difference(critical, redundant)
        return critical, redundant, intermittent

    def classify_node_deletion_importance(self):
        """
        Classify the importance of each node by
        testing the number of minimum driver nodes required
        after the node has been removed from the network.
        """

        all_nodes = set(self.state_nodes)
        G = self.G.subgraph(self.state_nodes)
        H = create_bipartite_from_directed_graph(G)
        matching = find_maximum_matchings(H)[0]
        _, driver_nodes = convert_matching_to_nodes(
            matching, G.nodes, from_bipartite=True
        )
        n_driver_nodes = len(driver_nodes)

        critical, redundant, ordinary = set(), set(), set()
        for node in all_nodes:
            G = self.G.subgraph(all_nodes.difference({node}))
            H = create_bipartite_from_directed_graph(G)
            matchings = find_maximum_matchings(H)
            if len(matchings) > 0:
                _, driver_nodes = convert_matching_to_nodes(
                    matching, G.nodes, from_bipartite=True
                )
            else:
                driver_nodes = G.nodes
            if len(driver_nodes) > n_driver_nodes:
                critical.add(node)
            elif len(driver_nodes) < n_driver_nodes:
                redundant.add(node)
            else:
                ordinary.add(node)
        return critical, redundant, ordinary
