"""
Algorithms to select influential nodes in a network using voting methods from Computational
Social Choice.
"""

__all__ = ["sav_voting"]


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