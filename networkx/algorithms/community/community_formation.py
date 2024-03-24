"""
Implementation of the Social Aware Assignment of Passengers in Ridesharing
The social aware assignment problem belongs to the field of community formation, which is an important research branch 
within multiagent systems. It analyses the outcome that results when a set of agents is partitioned into communities.
Actually, Match_And_Merge model is a special case of simple Additively Separable Hedonic Games (ASHGs).

Which was described in the article:
Levinger C., Hazon N., Azaria A. Social Aware Assignment of Passengers in Ridesharing. - 2022, https://github.com/VictoKu1/ResearchAlgorithmsCourse1/raw/main/Article/2022%2C%20Chaya%20Amos%20Noam%2C%20Socially%20aware%20assignment%20of%20passengers%20in%20ride%20sharing.pdf
Implementation of match_and_merge
algorithm is based on the pseudocode from the article
which is written by Victor Kushnir.

Also, an online web page was built for running the algorithm:
https://victoku1.pythonanywhere.com/
"""
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["match_and_merge"]


@not_implemented_for("directed")
def match_and_merge(Graph: nx.Graph, k: int) -> list:
    """
    An approximation algorithm for any k ≥ 3, provides a solution for the social aware assignment problem with a ratio of 1/(k-1).

    Social aware assignment definition:

    Given a number k and an undirected friendship graph G = (V, E) where (v_i , v_j) ∈ E if v_i and v_j are connected.
    The goal is to find an assignment P, which is a partition of the set V , such that ∀S ∈ P, |S|≤ k, and the value of P,
    V_P = |{(v_i , v_j) ∈ E: ∃S ∈ P where v_i ∈ S and v_j ∈ S}| is maximized.

    As described in the article under the section "Algorithm 1: Match and Merge".

    The article:

    Levinger C., Hazon N., Azaria A. Social Aware Assignment of Passengers in Ridesharing. - 2022, https://github.com/VictoKu1/ResearchAlgorithmsCourse1/raw/main/Article/2022%2C%20Chaya%20Amos%20Noam%2C%20Socially%20aware%20assignment%20of%20passengers%20in%20ride%20sharing.pdf.

    Function receives a graph G and a number k, and returns a partition P of G of all matched sets, so for ∀S ∈ P, |S|≤ k, and the value of P, V_P = |{(v_i , v_j) ∈ E: ∃S ∈ P where v_i ∈ S and v_j ∈ S}| is maximized.

    The algorithm consists of k - 1 rounds. Each round is composed of a matching phase followed by a merging phase.

    Specifically, in round l MnM computes a maximum matching, M_l ⊆ E_l , for G_l (where G_1 = G). In the merging phase, MnM creates a graph
    G_(l+1) that includes a unified node for each pair of matched nodes. G_(l+1) also includes all unmatched nodes, along with their
    edges to the unified nodes. Clearly, each node in V_l is composed of up-to l nodes
    from V_1. Finally, MnM returns the partition, P, of all the matched sets in a way that ∀S ∈ P, |S|≤ k, and the value of P, V_P = |{(v_i , v_j) ∈ E: ∃S ∈ P where v_i ∈ S and v_j ∈ S}| is maximized.

    :param G: Graph
    :param k: Number of passengers
    :return: A partition P of G of all matched sets so ∀S ∈ P, |S|≤ k, and the value of P, V_P = |{(v_i , v_j) ∈ E: ∃S ∈ P where v_i ∈ S and v_j ∈ S}| is maximized.

    Examples:

    Example where G={(v1,v2),(v2,v3),(v3,v4),(v4,v5),(v4,v6)} and k=1:
    >>> G = nx.Graph()
    >>> list_of_edges = [(4, 6), (4, 5), (3, 4), (2, 3), (1, 2)]
    >>> G.add_edges_from(list_of_edges)
    >>> k = 1
    >>> print(match_and_merge(G, k))
    [[1], [2], [3], [4], [5], [6]]

    Example where G={(v1,v2),(v2,v3),(v3,v4),(v4,v5),(v4,v6)} and k=2:
    >>> G = nx.Graph()
    >>> list_of_edges = [(4, 6), (4, 5), (3, 4), (2, 3), (1, 2)]
    >>> G.add_edges_from(list_of_edges)
    >>> k = 2
    >>> print(match_and_merge(G, k))
    [[1, 2], [3, 4], [5], [6]]

    Example where G={(v1,v2),(v2,v3),(v3,v4),(v4,v5),(v4,v6)} and k=3:
    >>> G = nx.Graph()
    >>> list_of_edges = [(4, 6), (4, 5), (3, 4), (2, 3), (1, 2)]
    >>> G.add_edges_from(list_of_edges)
    >>> k = 3
    >>> print(match_and_merge(G, k))
    [[1, 2], [3, 4, 6], [5]]

    Example where G={(v1,v2),(v2,v3),(v3,v4),(v4,v5),(v4,v6)} and k=4:
    >>> G = nx.Graph()
    >>> list_of_edges = [(4, 6), (4, 5), (3, 4), (2, 3), (1, 2)]
    >>> G.add_edges_from(list_of_edges)
    >>> k = 4
    >>> print(match_and_merge(G, k))
    [[1, 2], [3, 4, 5, 6]]
    """
    # Check if k is correct
    if Graph.number_of_nodes() < k:
        raise nx.NetworkXError(
            "k cannot be greater than the number of nodes in the Graph"
        )
    elif k < 0:
        raise nx.NetworkXError("k should be 0≤k≤|V(Graph)|")
    elif k == 0:
        return []
    # If k is 1, return a partition of the Graph, where each node is a list
    elif k == 1:
        return sorted([[node] for node in Graph.nodes()])
    else:
        # The nodes and the edges of G_1 are sorted in descending order so the maximal matching will be as close to the matching in the article as possible
        G_1 = nx.Graph()
        G_1.add_nodes_from(sorted((Graph.nodes()), reverse=True))
        G_1.add_edges_from(sorted((Graph.edges()), reverse=True))
        # Implement G_l=(V_l,E_l) using a dictionary which contains a tuple of V_l and E_l
        G: dict[int, nx.Graph] = {1: G_1}
        # Should contain the maximal matching of G_l
        M: dict[int, list] = {}
        # Loop to find the lth maximal matching and put it in G_(l+1)
        for l in range(1, k):
            # Initialization of the unified nodes list
            unified_nodes: list = []
            # Find the maximum matching of G_l
            M[l] = list(nx.max_weight_matching(G[l], weight=1))
            # Make sure that G_(l+1) is a empty graph (It was one of the steps of the algorithm in the article)
            if l + 1 not in G:
                G[l + 1] = nx.Graph()
            # Put the nodes of G_l in G_(l+1)
            G[l + 1].add_nodes_from(tuple(G[l].nodes()))
            # For every match in M_l, add a unified node to G_(l+1) so it will be used to find it when needed
            for match in M[l]:
                # Add the match to the unified nodes dictionary, so it will be easier to find the unified nodes in each round
                unified_nodes.append(match)
                # Add a unified node to G_(l+1), which is a tuple of the nodes in the match
                G[l + 1].add_node(match)
                # Remove the nodes in the match from G_(l+1)
                G[l + 1].remove_nodes_from(list(match))
            # For every unified node in G_(l+1), add every v_q in G_(l+1) that is connected to it in G_l, add an edge between them in G_(l+1)
            for unified_node in unified_nodes:
                for v_q in G[l + 1].nodes():
                    if (
                        G[l].has_edge(unified_node, v_q)
                        or G[l].has_edge(unified_node[0], v_q)
                        or G[l].has_edge(unified_node[1], v_q)
                    ):
                        G[l + 1].add_edge(unified_node, v_q)
        # Initialization of the partition P and for every unified node (which is a tuple of nodes) in G_k, add it to P
        P = [[unified_node] for unified_node in G[k].nodes()]
        P = tuplesflattener(P)
    # Return P
    return P


def tuplesflattener(P: list) -> list:
    """
    This function receives a list of partitions, which may contain nested tuples, and returns a list of lists which doesn't contain any tuples.

    :param P: A list of partitions, which may contain nested tuples
    :return: A list of lists which doesn't contain any tuples

    Examples:

    >>> P = [[(1, (2, (3, (4, 5))))]]
    >>> print(tuplesflattener(P))
    [[1, 2, 3, 4, 5]]
    """
    # Loop through every partition in P
    for partition in P:
        # While there are tuples in the partition, remove them and add their elements to the partition
        while any(isinstance(node, tuple) for node in partition):
            for node in partition:
                # If the node is a tuple, remove it and add its elements to the partition
                if isinstance(node, tuple):
                    partition.remove(node)
                    partition.extend(list(node))
        # Sort the partitions
        partition.sort()
    # Sort P
    P.sort()
    return P
