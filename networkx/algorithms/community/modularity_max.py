"""Functions for detecting communities based on modularity."""

from collections import Counter

import networkx as nx
from networkx.algorithms.community.quality import modularity
from networkx.utils.mapped_queue import MappedQueue
from networkx.utils import not_implemented_for

__all__ = [
    "greedy_modularity_communities",
    "naive_greedy_modularity_communities",
    "_naive_greedy_modularity_communities",
]


def _greedy_modularity_communities_init(G, weight=None, resolution=1):
    r"""Initializes the data structures for greedy_modularity_communities().

    Clauset-Newman-Moore Eq 8-9. Eq 8 was missing a factor of 2 (from A_ij + A_ji).
    See [2]_ at :func:`greedy_modularity_communities`.

    Parameters
    ----------
    G : NetworkX graph

    weight : string or None, optional (default=None)
        The name of an edge attribute that holds the numerical value used
        as a weight.  If None, then each edge has weight 1.
        The degree is the sum of the edge weights adjacent to the node.

    resolution : float (default=1)
        If resolution is less than 1, modularity favors larger communities.
        Greater than 1 favors smaller communities.

    Returns
    -------
    dq_dict : dict of dict's
        dq_dict[i][j]: dQ for merging community i, j

    dq_heap : dict of MappedQueue's
        dq_heap[i][n] : (-dq, i, j) for communitiy i nth largest dQ

    H : MappedQueue
        (-dq, i, j) for community with nth largest max_j(dQ_ij)

    a, b : dict
        undirected:
            a[i]: fraction of (total weight of) edges within community i
            b : None
        directed:
            a[i]: fraction of (total weight of) edges with tails within community i
            b[i]: fraction of (total weight of) edges with heads within community i

    See Also
    --------
    :func:`greedy_modularity_communities`
    :func:`~networkx.algorithms.community.quality.modularity`
    """
    # Count nodes and edges (or the sum of edge-weights for weighted graphs)
    N = G.number_of_nodes()
    m = G.size(weight)

    # Calculate degrees
    if G.is_directed():
        k_in = dict(G.in_degree(weight=weight))
        k_out = dict(G.out_degree(weight=weight))
        q0 = 1.0 / m
    else:
        k_in = k_out = dict(G.degree(weight=weight))
        q0 = 1.0 / (2.0 * m)

    a = {node: kout * q0 for node, kout in k_out.items()}
    if G.is_directed():
        b = {node: kin * q0 for node, kin in k_in.items()}
    else:
        b = None

    dq_dict = {
        i: {
            j: q0
            * (
                G.get_edge_data(i, j, default={weight: 0}).get(weight, 1.0)
                + G.get_edge_data(j, i, default={weight: 0}).get(weight, 1.0)
                - resolution * q0 * (k_out[i] * k_in[j] + k_in[i] * k_out[j])
            )
            for j in nx.all_neighbors(G, i)
            if j != i
        }
        for i in G.nodes()
    }

    # dq correction for multi-edges
    # In case of multi-edges, get_edge_data(i, j) returns the key: data dict of the i, j
    # edges, which does not have a 'weight' key. Therefore, when calculating dq for i, j
    # Aij is always 1.0 and a correction is required.
    if G.is_multigraph():
        edges_count = dict(Counter(G.edges()))
        multi_edges = [edge for edge, count in edges_count.items() if count > 1]
        for edge in multi_edges:
            total_wt = sum(d.get(weight, 1) for d in G.get_edge_data(*edge).values())
            if G.is_directed():
                # The correction applies only to the direction of the edge. The edge at
                # the other direction is either not a multiedge (where the weight is
                # added correctly), non-existent or it is also a multiedge, in which
                # case it will be handled singly when its turn in the loop comes.
                q00 = q0
            else:
                q00 = 2 * q0
            dq_dict[edge[0]][edge[1]] += q00 * (total_wt - 1)
            dq_dict[edge[1]][edge[0]] += q00 * (total_wt - 1)

    dq_heap = {
        i: MappedQueue([(-dq, i, j) for j, dq in dq_dict[i].items()]) for i in G.nodes()
    }
    H = MappedQueue([dq_heap[i].h[0] for i in G.nodes() if len(dq_heap[i]) > 0])

    return dq_dict, dq_heap, H, a, b


def greedy_modularity_communities(G, weight=None, resolution=1, n_communities=1):
    r"""Find communities in G using greedy modularity maximization.

    This function uses Clauset-Newman-Moore greedy modularity maximization [2]_.

    Greedy modularity maximization begins with each node in its own community
    and joins the pair of communities that most increases modularity until no
    such pair exists or until number of communities `n_communities` is reached.

    This function maximizes the generalized modularity, where `resolution`
    is the resolution parameter, often expressed as $\gamma$.
    See :func:`~networkx.algorithms.community.quality.modularity`.

    Parameters
    ----------
    G : NetworkX graph

    weight : string or None, optional (default=None)
        The name of an edge attribute that holds the numerical value used
        as a weight.  If None, then each edge has weight 1.
        The degree is the sum of the edge weights adjacent to the node.

    resolution : float (default=1)
        If resolution is less than 1, modularity favors larger communities.
        Greater than 1 favors smaller communities.

    n_communities: int
        Desired number of communities: the community merging process is
        terminated once this number of communities is reached, or until
        modularity can not be further increased. Must be between 1 and the
        total number of nodes in `G`. Default is ``1``, meaning the community
        merging process continues until all nodes are in the same community
        or until the best community structure is found.

    Returns
    -------
    partition: list
        A list of frozensets of nodes, one for each community.
        Sorted by length with largest communities first.

    Examples
    --------
    >>> from networkx.algorithms.community import greedy_modularity_communities
    >>> G = nx.karate_club_graph()
    >>> c = greedy_modularity_communities(G)
    >>> sorted(c[0])
    [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]

    See Also
    --------
    modularity

    References
    ----------
    .. [1] Newman, M. E. J. "Networks: An Introduction", page 224
       Oxford University Press 2011.
    .. [2] Clauset, A., Newman, M. E., & Moore, C.
       "Finding community structure in very large networks."
       Physical Review E 70(6), 2004.
    .. [3] Reichardt and Bornholdt "Statistical Mechanics of Community
       Detection" Phys. Rev. E74, 2006.
    .. [4] Newman, M. E. J."Analysis of weighted networks"
       Physical Review E 70(5 Pt 2):056131, 2004.
    """
    N = G.number_of_nodes()
    if (n_communities < 1) or (n_communities > N):
        raise ValueError(
            f"n_communities must be between 1 and {N}. Got {n_communities}"
        )

    # Initialize data structures
    dq_dict, dq_heap, H, a, b = _greedy_modularity_communities_init(
        G, weight, resolution
    )
    # Initialize single-node communities
    communities = {i: frozenset([i]) for i in G.nodes()}
    # Initial modularity
    q_cnm = modularity(G, communities.values(), resolution=resolution)

    # Merge communities until we can't improve modularity or until desired number of
    # communities (n_communities) is reached.
    while len(H) > n_communities:
        # Find best merge
        # Remove from heap of row maxes
        # Ties will be broken by choosing the pair with lowest min community id
        try:
            dq, i, j = H.pop()
        except IndexError:
            break
        dq = -dq
        # Remove best merge from row i heap
        dq_heap[i].pop()
        # Push new row max onto H
        if len(dq_heap[i]) > 0:
            H.push(dq_heap[i].h[0])
        # If this element was also at the root of row j, we need to remove the
        # duplicate entry from H
        if dq_heap[j].h[0] == (-dq, j, i):
            H.remove((-dq, j, i))
            # Remove best merge from row j heap
            dq_heap[j].remove((-dq, j, i))
            # Push new row max onto H
            if len(dq_heap[j]) > 0:
                H.push(dq_heap[j].h[0])
        else:
            # Duplicate wasn't in H, just remove from row j heap
            dq_heap[j].remove((-dq, j, i))
        # Stop when change is non-positive
        if dq <= 0:
            break

        # Perform merge
        communities[j] = frozenset(communities[i] | communities[j])
        del communities[i]
        # New modularity
        q_cnm += dq
        # Get list of communities connected to merged communities
        i_set = set(dq_dict[i].keys())
        j_set = set(dq_dict[j].keys())
        all_set = (i_set | j_set) - {i, j}
        both_set = i_set & j_set
        # Merge i into j and update dQ
        for k in all_set:
            # Calculate new dq value
            if k in both_set:
                dq_jk = dq_dict[j][k] + dq_dict[i][k]
            elif k in j_set:
                if G.is_directed():
                    dq_jk = dq_dict[j][k] - resolution * (a[i] * b[k] + a[k] * b[i])
                else:
                    dq_jk = dq_dict[j][k] - 2.0 * resolution * a[i] * a[k]
            else:
                # k in i_set
                if G.is_directed():
                    dq_jk = dq_dict[i][k] - resolution * (a[j] * b[k] + a[k] * b[j])
                else:
                    dq_jk = dq_dict[i][k] - 2.0 * resolution * a[j] * a[k]
            # Update rows j and k
            for row, col in [(j, k), (k, j)]:
                # Save old value for finding heap index
                if k in j_set:
                    d_old = (-dq_dict[row][col], row, col)
                else:
                    d_old = None
                # Update dict for j,k only (i is removed below)
                dq_dict[row][col] = dq_jk
                # Save old max of per-row heap
                if len(dq_heap[row]) > 0:
                    d_oldmax = dq_heap[row].h[0]
                else:
                    d_oldmax = None
                # Add/update heaps
                d = (-dq_jk, row, col)
                if d_old is None:
                    # We're creating a new nonzero element, add to heap
                    dq_heap[row].push(d)
                else:
                    # Update existing element in per-row heap
                    dq_heap[row].update(d_old, d)
                # Update heap of row maxes if necessary
                if d_oldmax is None:
                    # No entries previously in this row, push new max
                    H.push(d)
                else:
                    # We've updated an entry in this row, has the max changed?
                    if dq_heap[row].h[0] != d_oldmax:
                        H.update(d_oldmax, dq_heap[row].h[0])

        # Remove row/col i from matrix
        i_neighbors = dq_dict[i].keys()
        for k in i_neighbors:
            # Remove from dict
            dq_old = dq_dict[k][i]
            del dq_dict[k][i]
            # Remove from heaps if we haven't already
            if k != j:
                # Remove both row and column
                for row, col in [(k, i), (i, k)]:
                    # Check if replaced dq is row max
                    d_old = (-dq_old, row, col)
                    if dq_heap[row].h[0] == d_old:
                        # Update per-row heap and heap of row maxes
                        dq_heap[row].remove(d_old)
                        H.remove(d_old)
                        # Update row max
                        if len(dq_heap[row]) > 0:
                            H.push(dq_heap[row].h[0])
                    else:
                        # Only update per-row heap
                        dq_heap[row].remove(d_old)

        del dq_dict[i]
        # Mark row i as deleted, but keep placeholder
        dq_heap[i] = MappedQueue()
        # Merge i into j and update a
        a[j] += a[i]
        a[i] = 0
        if G.is_directed():
            b[j] += b[i]
            b[i] = 0

    partition = sorted(communities.values(), key=len, reverse=True)
    return partition


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def naive_greedy_modularity_communities(G, resolution=1):
    r"""Find communities in G using greedy modularity maximization.

    This implementation is O(n^4), much slower than alternatives, but it is
    provided as an easy-to-understand reference implementation.

    Greedy modularity maximization begins with each node in its own community
    and joins the pair of communities that most increases modularity until no
    such pair exists.

    This function maximizes the generalized modularity, where `resolution`
    is the resolution parameter, often expressed as $\gamma$.
    See :func:`~networkx.algorithms.community.quality.modularity`.

    Parameters
    ----------
    G : NetworkX graph

    resolution : float (default=1)
        If resolution is less than 1, modularity favors larger communities.
        Greater than 1 favors smaller communities.

    Returns
    -------
    list
        A list of sets of nodes, one for each community.
        Sorted by length with largest communities first.

    Examples
    --------
    >>> from networkx.algorithms.community import \
    ... naive_greedy_modularity_communities
    >>> G = nx.karate_club_graph()
    >>> c = naive_greedy_modularity_communities(G)
    >>> sorted(c[0])
    [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]

    See Also
    --------
    greedy_modularity_communities
    modularity
    """
    # First create one community for each node
    communities = list([frozenset([u]) for u in G.nodes()])
    # Track merges
    merges = []
    # Greedily merge communities until no improvement is possible
    old_modularity = None
    new_modularity = modularity(G, communities, resolution=resolution)
    while old_modularity is None or new_modularity > old_modularity:
        # Save modularity for comparison
        old_modularity = new_modularity
        # Find best pair to merge
        trial_communities = list(communities)
        to_merge = None
        for i, u in enumerate(communities):
            for j, v in enumerate(communities):
                # Skip i==j and empty communities
                if j <= i or len(u) == 0 or len(v) == 0:
                    continue
                # Merge communities u and v
                trial_communities[j] = u | v
                trial_communities[i] = frozenset([])
                trial_modularity = modularity(
                    G, trial_communities, resolution=resolution
                )
                if trial_modularity >= new_modularity:
                    # Check if strictly better or tie
                    if trial_modularity > new_modularity:
                        # Found new best, save modularity and group indexes
                        new_modularity = trial_modularity
                        to_merge = (i, j, new_modularity - old_modularity)
                    elif to_merge and min(i, j) < min(to_merge[0], to_merge[1]):
                        # Break ties by choosing pair with lowest min id
                        new_modularity = trial_modularity
                        to_merge = (i, j, new_modularity - old_modularity)
                # Un-merge
                trial_communities[i] = u
                trial_communities[j] = v
        if to_merge is not None:
            # If the best merge improves modularity, use it
            merges.append(to_merge)
            i, j, dq = to_merge
            u, v = communities[i], communities[j]
            communities[j] = u | v
            communities[i] = frozenset([])
    # Remove empty communities and sort
    return sorted((c for c in communities if len(c) > 0), key=len, reverse=True)


# old name
_naive_greedy_modularity_communities = naive_greedy_modularity_communities
