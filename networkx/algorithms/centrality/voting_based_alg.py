"""Algorithms to select influential nodes in a network, or to rank nodes by their
centrality using voting methods from Computational Social Choice.
"""

import itertools
import networkx as nx

__all__ = ["sav_voting", "copeland_voting", "spav_voting"]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def sav_voting(G):
    """Rank nodes using Satisfaction Approval Voting (SAV) [1]_ .

    SAV centrality (introduced in [2]_ and based on the framework in [3]_ ) lets each node vote
    on the centrality of its neighbors. Thereby, each node x contributes 1/|degree(x)| points
    to the total score of each neighbor. In other words: node x distributes a total of 1 point
    equally to all neighbors. One interpretation is that a node is more central according to
    SAV centrality if it has many neighbors which highly rely on the connection to this node
    (they have no, or only a few, other neighbors).

    For a detailed description of the SAV voting system which is the base of this centrality
    method, and a study on its properties, see [1]_ and
    https://en.wikipedia.org/wiki/Satisfaction_approval_voting

    Notes
    -----
    SAV centrality only works with undirected networks (no multigraph). Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    sav_voting : dict
        For each node the dict contains the SAV score.

    See Also
    --------
    copeland_voting, spav_voting

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (1, 5), (5, 6), (6, 7), (7, 8), (7, 9)])
    >>> nx.sav_voting(G)
    {1: 3.5, 2: 0.25, 3: 0.25, 4: 0.25, 5: 0.75, 6: 0.833, 7: 2.5, 8: 0.33, 9: 0.33}

    References
    ----------
    .. [1] Brams, S. J. and Kilgour, D. M. (2014).
        "Satisfaction Approval Voting"
        In: Voting Power and Procedures.
        Publisher: Springer
        Pages 323-346.
        https://link.springer.com/chapter/10.1007/978-3-319-05158-1_18
       [2] Laussmann, C. (2023).
        "Network Centrality Through Voting Rules"
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-Universitaet Duesseldorf
        Pages 27-45.
       [3] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
    """

    # Compute Scores
    scores = {candidate : 0 for candidate in G.nodes}
    for voter in G.nodes:
        neighbors = list(G.neighbors(voter))
        voting_capability = 1/len(neighbors)
        for candidate in neighbors:
            scores[candidate] += voting_capability
    
    return scores



@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def copeland_voting(G):
    """Rank nodes using the Condorcet-consistent voting rule due to Arthur Copeland.

    According to Condorcet, a candidate should win an election whenever it is preferred
    to each other candidate by a majority of voters in direct comparison. Although this
    is a very reasonable criterion, it doesn't tell us what to do when such a candidate
    doesn't exist (which happens most of the time). Arthur Copeland (1951) described a
    method which selects the Condorcet-winner whenever it exists, but chooses a candidate
    which is close to being a Condorcet winner otherwise.

    This centrality index is based on Copeland's method. Each node is compared with every
    other node in direct comparison. Say nodes A and B are compared. If there are more
    nodes strictly closer to A than to B, A receives one point (wins the pairwise
    comparison), and B loses one point. The same holds vice versa when B wins the pairwise
    comparison. If A and B are tied (neither A nor B wins), both receive no points. The
    Copeland centrality index is achieved by summing up all the points from all comparisons.
    
    The Copeland centrality index was introduced in [1]_ . Although the Copeland voting
    method is mostly known under Copeland's name, it dates back at least to Llull (1299).
    See also https://en.wikipedia.org/wiki/Copeland%27s_method

    Notes
    -----
    Copeland centrality only works with undirected networks (no multigraph).
    Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    copeland_voting : dict
        For each node the dict contains the copeland score.

    See Also
    --------
    sav_voting, spav_voting
    
    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (1, 5), (5, 6), (6, 7), (7, 8), (7, 9)])
    >>> nx.copeland_voting(G)
    {1: 5, 2: -1, 3: -1, 4: -1, 5: 8, 6: 5, 7: -1, 8: -7, 9: -7}

    References
    ----------
    .. [1] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
    """

    shortest_paths_len = dict()
    for start, distances in nx.shortest_path_length(G, source=None, target=None):
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


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def spav_voting(G, number_of_nodes=None, voting_ability_fn=None):
    """Select a set of influential nodes using Sequential Proportional Approval Voting (SPAV).

    SPAV centrality (introduced in [2]_ and based on the framework in [3]_ ) lets each node vote
    on the centrality of its neighbors in multiple rounds. In each round, the node with the highest
    voting score is elected where each node contributes the same points to each of its neighbors.
    Thereby, whenever a node is elected, all neighbors' voting ability is reduced so that in the
    next round they contribute less points to their neighbors (similar to VoteRank [4]_). By how far
    the voting ability is reduced depends on the voting_ability_fn, which maps an integer (how many
    nodes from the neighborhood of a "voter" are already selected) to a real number (voting ability).
    By default, voting_ability_fn(0) = 1, voting_ability_fn(1) = 1/2, voting_ability_fn(2) = 1/3,
    etc., is used.
    
    The original voting method SPAV was first proposed by Thorvald Thiele around 1900. For an
    introduction, and astudy on SPAV's properties, see e.g. [1]_ as well as
    https://en.wikipedia.org/wiki/Sequential_proportional_approval_voting

    Notes
    -----
    SPAV centrality only works with undirected networks (no multigraph).
    Weights are ignored.

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

    See Also
    --------
    copeland_voting, sav_voting
    
    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (1, 5), (5, 6), (6, 7), (7, 8), (7, 9)])
    >>> nx.spav_voting(G, number_of_nodes=2)
    [1, 7]

    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (7, 6), (7, 8), (7, 9), (10, 6), (10, 1),])
    >>> nx.spav_voting(G, number_of_nodes=2, voting_ability_fn=lambda x : 1 if x==0 else 0)
    [6, 7]

    References
    ----------
    .. [1] Aziz, H. et al. (2017).
        "Justified Representation in Approval-based Committee Voting"
        In: Social Choice and Welfare 48
        Pages 461-485.
       [2] Laussmann, C. (2023).
        "Network Centrality Through Voting Rules"
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-Universitaet Duesseldorf
        Pages 27-45.
       [3] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
       [4] Zhang, J.-X. et al. (2016).
        "Identifying a set of influential spreaders in complex networks."
        In: Sci. Rep. 6, 27823.
        https://doi.org/10.1038/srep27823
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
        best = max(candidates, key=scores.get)
        selected_nodes.append(best)
        candidates.remove(best)
        for voter in G.neighbors(best):
            neighbors_already_selected[voter] += 1
    return selected_nodes
