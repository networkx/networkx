"""
Algorithms to select influential nodes in a network, or to rank nodes by their
centrality using voting methods from Computational Social Choice.
"""

import itertools

__all__ = ["sav_voting", "copeland_voting"]


@not_implemented_for("directed")
def sav_voting(G, number_of_nodes):
    """Select a set of influential nodes using Satisfaction Approval Voting (SAV).

    SAV [1]_ [2]_ lets each node vote on the centrality of its neighbors. Thereby, each node x
    contributes 1/|degree(x)| points to the total score of each neighbor. In other words: node
    x distributes a total of 1 point equally to all neighbors.

    Eventually, the nodes with the highest total score are selected.

    SAV only works with undirected networks. Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    number_of_nodes : integer
        Number of nodes to select.

    Returns
    -------
    sav_voting : set
        The number_of_nodes nodes with highest SAV score.

    Examples
    --------
    TODO

    References
    ----------
    .. [1] Brams, S. and Kilgour, D. (2014).
        Satisfaction Approval Voting.
        In: Voting Power and Procedures.
        Publisher: Springer
        Pages 323-346.
       [2] Laussmann, C. (2023).
        Network Centrality Through Voting Rules.
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-Universitaet Duesseldorf
        Pages 27-45.
    """

    # Compute Scores
    scores = {candidate : 0 for candidate in G.nodes}
    for voter in G.nodes:
        neighbors = G.neighbors(voter)
        voting_capability = 1/len(neighbors)
        for candidate in neighbors:
            scores[candidate] += voting_capability
    
    # Select best nodes
    selected nodes = set()
    for i in range(number_of_nodes):
        best = max(G.nodes, key=scores.get)
        selected_nodes.add(best)
        scores[best] = -1
    return selected_nodes



@not_implemented_for("directed")
def copeland_voting(G):
    """Rank nodes using the Condorcet-consistent voting rule due to Copeland.

    According to Condorcet, a candidate should win an election whenever it is preferred
    to each other candidate by a majority of voters in direct comparison. Although this
    is a very reasonable criterion, it doesn't tell us what to do when such a candidate
    doesn't exist (which happens most of the time). Arthur Copeland described a method
    which selects the Condorcet-winner whenever it exists, but chooses a winner which
    is close to being a Condorcet winner otherwise.

    This centrality index is based on Copelands method. Each node is compared with every
    other node in direct comparison. Say nodes A and B are compared. If there are more
    nodes strictly closer to A than to B, A receives one point (wins the pairwise
    comparison), and B loses one point. The same holds vice versa when B wins the pairwise
    comparison. If A and B are tied (neither A nor B wins), both receive no points. The
    Copeland centrality index is achieved by summing up all the points from all comparisons.
    
    The Copeland centrality index was introduced in [1]_ .

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    copeland_voting : dict
        For each node the dict contains the copeland score.

    Examples
    --------
    TODO

    References
    ----------
    .. [1] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        Voting for Centrality (Extended Abstract).
        Proceedings of the 21st International Conference on Autonomous Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
    """

    shortest_paths_len = dict()
    for start, distances in nx.shortest_path_length(graph, source=None, target=None):
        shortest_paths_len[start] = distances

    def pairwise_comparison(A, B):
        other_nodes = G.nodes - {A,B}
        prefers_A = [n for n in other_nodes if shortest_paths_len[n][A] < shortest_paths_len[n][B]]
        prefers_B = [n for n in other_nodes if shortest_paths_len[n][A] > shortest_paths_len[n][B]]
        if len(prefers_A) > len(prefers_B):
            return 1
        elif len(prefers_A) < len(prefers_B):
            return -1
        return 0

    # Compute Scores
    scores = {candidate : 0 for candidate in G.nodes}
    for X,Y in itertools.combinations(G.nodes, 2):
        comparison = pairwise_comparison(X,Y)
        scores[X] += comparison
        scores[Y] -= comparison

    return scores