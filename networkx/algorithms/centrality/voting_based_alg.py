"""Algorithms to select influential nodes in a network, or to rank nodes by
their centrality using voting methods from Computational Social Choice.
"""

import itertools

import networkx as nx

__all__ = [
    "satisfaction_approval_centrality",
    "pairwise_centrality",
    "borda_centrality",
    "single_transferable_vote",
    "sequential_proportional_voting",
]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def satisfaction_approval_centrality(G):
    """Rank nodes using Satisfaction Approval Voting (SAV).

    Satisfaction approval centrality (introduced in [2]_ and based on the
    framework in [3]_ ) lets each node vote on the centrality of its neighbors.
    Thereby, each node x contributes 1/degree(x) points to the total score of
    each neighbor. In other words: node x distributes a total of 1 point equally
    to all neighbors. One interpretation is that a node is more central
    according to this centrality if it has many neighbors which highly rely on
    the connection to this node (they have no, or only a few, other neighbors).

    For a detailed description of the SAV voting system which is the base of
    this centrality index, and a study on its properties, see [1]_ and
    https://en.wikipedia.org/wiki/Satisfaction_approval_voting

    Notes
    -----
    Satisfaction approval centrality only works with undirected networks (no
    multigraph). Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    satisfaction_approval_centrality : dict
        For each node the dict contains the SAV score.

    See Also
    --------
    pairwise_centrality, sequential_proportional_voting, borda_centrality,
    single_transferable_vote

    Examples
    --------
    >>> G = nx.Graph([(1,2), (1,3), (1,4), (1,5), (2,3)])
    >>> nx.satisfaction_approval_centrality(G)
    {1: 3.0, 2: 0.75, 3: 0.75, 4: 0.25, 5: 0.25}

    References
    ----------
    .. [1] Brams, S. J. and Kilgour, D. M. (2014).
        "Satisfaction Approval Voting"
        In: Voting Power and Procedures.
        Publisher: Springer
        Pages 323-346.
        https://link.springer.com/chapter/10.1007/978-3-319-05158-1_18
    .. [2] Laussmann, C. (2023).
        "Network Centrality Through Voting Rules"
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-
        Universitaet Duesseldorf
        Pages 27-45.
    .. [3] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous
        Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
    """

    scores = {candidate: 0 for candidate in G.nodes}
    for voter in G.nodes:
        neighbors = list(G.neighbors(voter))
        voting_capability = 1 / len(neighbors)
        for candidate in neighbors:
            scores[candidate] += voting_capability
    return scores


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def pairwise_centrality(G):
    """Rank nodes using the Condorcet-consistent voting rule due to A. Copeland.

    According to Condorcet, a candidate should win an election whenever it is
    preferred to each other candidate by a majority of voters in direct
    comparison. Although this is a very reasonable criterion, it doesn't tell us
    what to do when such a candidate doesn't exist (which happens most of the
    time). Arthur Copeland (1951) described a method which selects the Condorcet
    -winner whenever it exists, but chooses a candidate which is close to being
    a Condorcet winner otherwise.

    This centrality index is based on Copeland's method. Each node is compared
    with every other node in direct comparison. Say nodes A and B are compared.
    If there are more nodes strictly closer to A than to B, A receives one point
    (wins the pairwise comparison), and B loses one point. The same holds vice
    versa when B wins the pairwise comparison. If A and B are tied (neither A
    nor B wins), both receive no points. The Copeland centrality index is
    achieved by summing up all the points from all comparisons.

    The pairwise centrality index was introduced in [1]_ . Although the Copeland
    voting method is mostly known under Copeland's name, it dates back at least
    to Llull (1299). See also https://en.wikipedia.org/wiki/Copeland%27s_method

    Notes
    -----
    Pairwise centrality only works with undirected networks (no multigraph).
    Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    pairwise_centrality : dict
        For each node the dict contains the copeland score.

    See Also
    --------
    satisfaction_approval_centrality, sequential_proportional_voting,
    borda_centrality, single_transferable_vote

    Examples
    --------
    >>> G = nx.Graph([(1,2), (2,3), (3,4), (3,5), (2,6)])
    >>> nx.pairwise_centrality(G)
    {1: -2, 2: 4, 3: 4, 4: -2, 5: -2, 6: -2}

    References
    ----------
    .. [1] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous
        Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
    """

    shortest_paths_len = {}
    for start, distances in nx.shortest_path_length(G, source=None, target=None):
        shortest_paths_len[start] = distances

    # Function for computing who wins pairwise comparison
    def pairwise_comparison(A, B):
        other_nodes = G.nodes - {A, B}
        prefers_A = [
            n
            for n in other_nodes
            if shortest_paths_len[n][A] < shortest_paths_len[n][B]
        ]
        prefers_B = [
            n
            for n in other_nodes
            if shortest_paths_len[n][A] > shortest_paths_len[n][B]
        ]
        if len(prefers_A) > len(prefers_B):
            return 1
        elif len(prefers_A) < len(prefers_B):
            return -1
        return 0

    # Compute Scores
    scores = {candidate: 0 for candidate in G.nodes}
    for X, Y in itertools.combinations(G.nodes, 2):
        comparison = pairwise_comparison(X, Y)
        scores[X] += comparison
        scores[Y] -= comparison
    return scores


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def borda_centrality(G):
    """Rank nodes using Borda's voting rule.

    According to Borda voting, each voter V assigns (m-1) points to the best
    candidate in V's perspective, (m-2) to the second best, and so on. Thereby,
    m is the total number of candidates. In other words, V assigns 1 point to a
    candidate X for every candidate X beats. Assigned points from all voters are
    summed up. The candidate with the most total points wins.

    This function applies a variant of this Borda rule to networks. A voter node
    prefers candidate nodes which are closer to him/her. Due to the many ties
    (nodes at same distance), in this function a voter assigns one point to a
    candidate X for every candidate X beats, and subtracts one point from X for
    every candidate X is beaten by. This version of Borda was proposed e.g. in
    [2]_ and applied to networks in [1]_.

    For more background on Borda see https://en.wikipedia.org/wiki/Borda_count

    Notes
    -----
    Borda centrality only works with undirected networks (no multigraph).
    Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    borda_centrality : dict
        For each node the dict contains the Borda score.

    See Also
    --------
    satisfaction_approval_centrality, sequential_proportional_voting,
    pairwise_centrality, single_transferable_vote

    Examples
    --------
    >>> G = nx.Graph([(1, 6), (1, 2), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)])
    >>> nx.borda_centrality(G)
    {1: 0, 6: -12, 2: 9, 3: 5, 4: 5, 5: -7}

    References
    ----------
    .. [1] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous
        Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
    .. [2] Gärdenfors, P. (1973)
        "Positionalist voting functions."
        In: Theory and Decision 4
        Pages: 6, 16
    """

    shortest_paths_len = {}
    for start, distances in nx.shortest_path_length(G, source=None, target=None):
        shortest_paths_len[start] = distances

    # Function for computing Borda score candidate receives from voter
    def borda_score(candidate, voter):
        if candidate == voter:
            return 0  # by convention, nodes do not vote for themselves
        nodes_remaining = set(G.nodes) - {candidate, voter}
        distance_candidate = shortest_paths_len[voter][candidate]
        better = [
            c
            for c in nodes_remaining
            if shortest_paths_len[voter][c] < distance_candidate
        ]
        worse = [
            c
            for c in nodes_remaining
            if shortest_paths_len[voter][c] > distance_candidate
        ]
        return len(worse) - len(better)

    # Compute Scores
    scores = {
        candidate: sum(borda_score(candidate, voter) for voter in G.nodes)
        for candidate in G.nodes
    }
    return scores


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def single_transferable_vote(G, number_of_nodes):
    """Select a set of influential nodes using Single Transferable Vote (STV).

    Single transferable vote (STV) follows the idea that a committee should be
    representative for the set of voters. The key idea is that each of X
    committee members should be supported by strictly more than the 1/(X+1)
    fraction of the voters (in fact, N/(X+1) + 1; the droop quota). For X = 2 it
    simply means that to be elected one needs strictly more than half of all
    voters' support. For X = 2 members, each member should be supported by
    strictly more than 1/3 of the voters. This way, even the combined support of
    all non-elected candidates is less than the support of each elected
    candidate. This goes on for larger X, too.

    Since usually there are no X candidates which reach the quota N/(X+1) + 1,
    STV repeats the following until X candidates are elected. If no candidate
    reaches the quota, remove the worst candidate from the election. Everyone
    who voted for this candidate now votes for their second-most preferred
    candidate. If a candidate reaches the quota, elect the candidate C with the
    most support among the voters. The excess to the quota of C is then
    distributed among the voters for C, so that they can still vote for their
    second-most preferred candidate with a reduced voting ability.

    This function computes the STV winners of a network. Nodes prefer candidates
    more the closer they are (shortest-path distance). This method has been
    proposed for networks in [1]_ (although this implementation is slightly
    different as it doesn't involve nondeterminsm). For more information on STV,
    we refer to https://en.wikipedia.org/wiki/Single_transferable_vote

    Notes
    -----
    STV centrality only works with undirected networks (no multigraph).
    Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    number_of_nodes : integer
        The number of nodes to select.

    Returns
    -------
    single_transferable_vote : set
        The selected nodes.

    See Also
    --------
    pairwise_centrality, satisfaction_approval_centrality, borda_centrality,
    sequential_proportional_voting

    Examples
    --------
    >>> G = nx.Graph([(1,2), (2,3), (3,4), (3,5), (2,6)])
    >>> nx.single_transferable_vote(G, 2)
    {2, 3}

    References
    ----------
    .. [1] Laussmann, C. (2023).
        "Network Centrality Through Voting Rules"
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-
        Universitaet Duesseldorf
        Pages 27-45.
    """

    shortest_path_len = {}
    for start, distances in nx.shortest_path_length(G, source=None, target=None):
        shortest_path_len[start] = distances

    selected_nodes = set()
    voting_abilities = {v: 1 for v in G.nodes}
    candidates_left = set(G.nodes)
    # This is not the Droop quota, since we implicitly assume nodes to prefer
    # themselves over the others, although they do not formally vote for
    # themselves. Thus our quota is lower by one.
    quota = len(G.nodes) // (number_of_nodes + 1)

    def plurality_winner_loser():
        plur_scores = {c: 0 for c in candidates_left}
        for v in G.nodes:
            best_candidate = min(candidates_left - {v}, key=shortest_path_len[v].get)
            for c in candidates_left:
                if shortest_path_len[v][c] == shortest_path_len[v][best_candidate]:
                    plur_scores[c] += voting_abilities[v]
        best = max(candidates_left, key=plur_scores.get)
        worst = min(candidates_left, key=plur_scores.get)
        return (best, plur_scores[best], worst)

    def reduce_voting_ability(elected_candidate, score_of_elected):
        exceed = score_of_elected - quota
        avg_voting_ability_afterwards = exceed / score_of_elected
        for v in G.nodes:
            best_candidate = min(candidates_left - {v}, key=shortest_path_len[v].get)
            if (
                shortest_path_len[v][best_candidate]
                == shortest_path_len[v][elected_candidate]
            ):
                voting_abilities[v] = (
                    voting_abilities[v] * avg_voting_ability_afterwards
                )

    while len(selected_nodes) < number_of_nodes:
        winner, win_score, loser = plurality_winner_loser()
        if win_score >= quota:
            reduce_voting_ability(winner, win_score)
            selected_nodes.add(winner)
            candidates_left.remove(winner)
            voting_abilities[winner] = 0
        else:
            candidates_left.remove(loser)
    return selected_nodes


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
def sequential_proportional_voting(G, number_of_nodes=None, reduction_fn=None):
    """Select a set of influential nodes using Sequential Proportional Approval
    Voting (SPAV).

    Sequential proportional centrality (introduced in [2]_ and based on the
    framework in [3]_ ) lets each node vote on the centrality of its neighbors
    in multiple rounds. In each round, the node with the highest voting score is
    elected where each node contributes the same points to each of its
    neighbors. Thereby, whenever a node is elected, all neighbors' voting
    ability is reduced so that in the next round they contribute less points to
    their neighbors (similar to VoteRank [4]_). By how far the voting ability is
    reduced depends on the reduction_fn, which maps an integer (how many nodes
    from the neighborhood of a "voter" are already selected) to a real number
    (voting ability). By default, reduction_fn(0) = 1, reduction_fn(1) = 1/2,
    reduction_fn(2) = 1/3, etc., is used.

    The original voting method SPAV was first proposed by Thorvald Thiele around
    1900. For an introduction, and a study on SPAV's properties, see e.g. [1]_
    and https://en.wikipedia.org/wiki/Sequential_proportional_approval_voting

    Notes
    -----
    Sequential proportional centrality only works with undirected networks (no
    multigraph). Weights are ignored.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    number_of_nodes : integer (Optional)
        The number of nodes to select. If None, all nodes are selected.

    reduction_fn : function: non-negative integer -> non-negative float
        A function f(x) returning the voting ability of a node when x neighbors
        are elected already. If None, the default function f(x) = 1/(x+1) will
        be used.

    Returns
    -------
    sequential_proportional_voting : list
        The sequence in which the number_of_nodes nodes are elected.

    See Also
    --------
    pairwise_centrality, satisfaction_approval_centrality, borda_centrality,
    single_transferable_vote

    Examples
    --------
    >>> G = nx.Graph([(1,2), (2,3), (3,4), (3,5), (2,6)])
    >>> nx.sequential_proportional_voting(G, number_of_nodes=2)
    [2, 3]

    References
    ----------
    .. [1] Aziz, H. et al. (2017).
        "Justified Representation in Approval-based Committee Voting"
        In: Social Choice and Welfare 48
        Pages 461-485.
    .. [2] Laussmann, C. (2023).
        "Network Centrality Through Voting Rules"
        In: COMSOC Methods in Real-World Applications (Dissertation).
        Publisher: Universitaets- und Landesbibliothek der Heinrich-Heine-
        Universitaet Duesseldorf
        Pages 27-45.
    .. [3] Brandes, U. and Laussmann, C. and Rothe, J. (2022).
        "Voting for Centrality (Extended Abstract)"
        In: Proceedings of the 21st International Conference on Autonomous
        Agents and Multiagent Systems (AAMAS)
        Publisher: IFAAMAS
        https://www.ifaamas.org/Proceedings/aamas2022/pdfs/p1554.pdf
    .. [4] Zhang, J.-X. et al. (2016).
        "Identifying a set of influential spreaders in complex networks."
        In: Sci. Rep. 6, 27823.
        https://doi.org/10.1038/srep27823
    """

    # Set default values
    if number_of_nodes is None or number_of_nodes > len(G.nodes):
        number_of_nodes = len(G.nodes)
    if reduction_fn is None:
        reduction_fn = lambda x: 1 / (x + 1)
    # Select nodes sequentially
    selected_nodes = []
    neighbors_already_selected = {voter: 0 for voter in G.nodes}
    candidates = set(G.nodes)
    for _ in range(number_of_nodes):
        scores = {}
        for candidate in candidates:
            candidate_score = 0
            for voter in G.neighbors(candidate):
                candidate_score += reduction_fn(neighbors_already_selected[voter])
            scores[candidate] = candidate_score
        best = max(candidates, key=scores.get)
        selected_nodes.append(best)
        candidates.remove(best)
        for voter in G.neighbors(best):
            neighbors_already_selected[voter] += 1
    return selected_nodes
