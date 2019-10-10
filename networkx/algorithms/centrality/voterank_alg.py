#   Copyright (C) 2017 by
#   Fredrik Erlandsson <fredrik.e@gmail.com>
#   All rights reserved.
#   BSD license.
#
"""Algorithm to compute influential seeds in a graph using voterank."""
from networkx.utils.decorators import not_implemented_for

__all__ = ['voterank']
__author__ = """\n""".join(['Fredrik Erlandsson <fredrik.e@gmail.com>',
                            'Piotr Brodka (piotr.brodka@pwr.edu.pl'])


@not_implemented_for('directed')
def voterank(G, number_of_nodes=None, max_iter=10000):
    """Compute a list of seeds for the nodes in the graph using VoteRank

    VoteRank [1]_ computes a ranking of the nodes in the graph G based on a voting
    scheme. With VoteRank, all nodes vote for each neighbours and the node with
    the highest score is elected iteratively. The voting ability of neighbors of
    elected nodes will be decreased in subsequent turn.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    number_of_nodes : integer, optional
        Number of ranked nodes to extract (default all nodes).

    max_iter : integer, optional
        Maximum number of iterations to rank nodes.

    Returns
    -------
    voterank : list
        Ordered list of computed seeds.

    Raises
    ------
    NetworkXNotImplemented:
        If G is digraph.

    References
    ----------
    .. [1] Zhang, J.-X. et al. (2016).
        Identifying a set of influential spreaders in complex networks.
        Sci. Rep. 6, 27823; doi: 10.1038/srep27823.
    """
    voterank = []
    if len(G) == 0:
        return voterank
    if number_of_nodes is None or number_of_nodes > len(G):
        number_of_nodes = len(G)
    avgDegree = sum(deg for _, deg in G.degree()) / float(len(G))
    # step 1 - initiate all nodes to (0,1) (score, voting ability)
    for _, v in G.nodes(data=True):
        v['voterank'] = [0, 1]
    # Repeat steps 1b to 4 until num_seeds are elected.
    for _ in range(max_iter):
        # step 1b - reset rank
        for _, v in G.nodes(data=True):
            v['voterank'][0] = 0
        # step 2 - vote
        for n, nbr in G.edges():
            G.nodes[n]['voterank'][0] += G.nodes[nbr]['voterank'][1]
            G.nodes[nbr]['voterank'][0] += G.nodes[n]['voterank'][1]
        for n in voterank:
            G.nodes[n]['voterank'][0] = 0
        # step 3 - select top node
        n, value = max(G.nodes(data=True),
                       key=lambda x: x[1]['voterank'][0])
        if value['voterank'][0] == 0:
            return voterank
        voterank.append(n)
        if len(voterank) >= number_of_nodes:
            return voterank
        # weaken the selected node
        G.nodes[n]['voterank'] = [0, 0]
        # step 4 - update voterank properties
        for nbr in G.neighbors(n):
            G.nodes[nbr]['voterank'][1] -= 1 / avgDegree
    return voterank
