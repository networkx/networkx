"""
Algorithms to select influential nodes in a network, or to rank nodes by their
centrality using voting methods from Computational Social Choice.
"""

import itertools

__all__ = ["sav_voting", "copeland_voting", "spav_voting"]


@not_implemented_for("directed")
def sav_voting(G):
    """
    Rank nodes using Satisfaction Approval Voting (SAV).

    SAV [1]_ [2]_ lets each node vote on the centrality of its neighbors. Thereby, each node x
    contributes 1/|degree(x)| points to the total score of each neighbor. In other words: node
    x distributes a total of 1 point equally to all neighbors.
    
    One interpretation is that a node is more central according to SAV if it has many neighbors
    which highly rely on the connection to this node (they have no, or only a few, other neighbors).

    SAV only works with undirected networks. Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    sav_voting : dict
        For each node the dict contains the SAV score.

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
    
    return scores



@not_implemented_for("directed")
def copeland_voting(G):
    """
    Rank nodes using the Condorcet-consistent voting rule due to Copeland.

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


@not_implemented_for("directed")
def spav_voting(G, number_of_nodes=None, voting_ability_fn=None):
    """
    Select a set of influential nodes using Sequential Proportional Approval Voting (SPAV).

    SPAV [1]_ [2]_ lets each node vote on the centrality of its neighbors in multiple rounds. In each
    round, the node with the highest voting score is elected where each node contributes the same
    points to each of its neighbors. Thereby, whenever a node is elected, all neighbors' voting ability
    is reduced so that in the next round they contribute less points to their neighbors (similar to VoteRank).
    By how far the voting ability is reduced depends on the voting_ability_fn, which maps an integer
    (how many nodes from the neighborhood of a "voter" are already selected) to a real number (voting ability).
    By default, voting_ability_fn(0) = 1, voting_ability_fn(1) = 1/2, voting_ability_fn(2) = 1/3, etc., is
    used, as it war originally proposed by Thiele in 1895.


    Parameters
    ----------
    G : graph
        A NetworkX graph.
    
    number_of_nodes : integer (Optional)
        The number of nodes to select. If None, all nodes are selected.

    voting_ability_fn : function: non-negative integer -> non-negative float (Optional)
        A function f(x) returning the voting ability of a node when x neighbors are elected already.
        If None, the default function f(x) = 1/(x+1) will be used.

    Returns
    -------
    spav_voting : list
        The sequence in which the number_of_nodes nodes are elected.

    Examples
    --------
    TODO

    References
    ----------
    .. [1] Aziz, H. et al. (2017).
        Justified representation in approval-based committee voting.
        In: Social Choice and Welfare 48
        Pages 461-485.
       [2] Laussmann, C. (2023).
        Network Centrality Through Voting Rules.
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-Universitaet Duesseldorf
        Pages 27-45.
    """

    # Set default values
    if number_of_nodes == None or number_of_nodes > len(G.nodes):
        number_of_nodes = len(G.nodes)
    if voting_ability_fn == None:
        voting_ability_fn = lambda x : 1/(x+1)
    
    # Select nodes sequentially
    selected_nodes = list()
    neighbors_already_selected = {voter : 0 for voter in G.nodes}
    candidates = set(G.nodes)
    for _ in range(number_of_nodes):
        scores = dict()
        for candidate in candidates:
            candidate_score = 0
            for voter in G.neighbors(candidate):
                candidate_score += voting_ability_fn(neighbors_already_selected[voter])
            scores[candidate] = candidate_score
        best = max(G.nodes, key=scores.get)
        selected_nodes.append(best)
        candidates.remove(best)
        for voter in G.neighbors(best):
            neighbors_already_selected[voter] += 1
    return selected_nodes