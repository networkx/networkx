"""
Utility functions for the algorithm :

* A function to build the matching cost matrix
* A function to convert the index mapping into a node mapping
"""

from collections.abc import Sequence

import networkx as nx
from networkx.algorithms.bipartite_ged.costfunctions import (
    ConstantCostFunction,
    CostFunction,
)


def compute_bipartite_cost_matrix(
    g1: nx.Graph, g2: nx.Graph, cf: CostFunction | None = None
):
    """Compute a cost matrix according to cost function `cf`

    Let $n$ and $m$ be the number of nodes of `g1` and `g2` respectively,
    and assume all their nodes are indexed starting from 0.
    This matrix contains the assignment costs. Each row corresponds
    to the node of same index in `g1`, and each column, to the
    node of same index in `g2`.

    Finding a full matching is impossible, unless $n = m$.
    Let $V_1$ be the list of nodes from `g1`, and $V_2$, the list
    of nodes from `g2` To make sure we find a unique matching for
    every node, we add $m$ empty nodes to $V_1$, and $n$ empty nodes
    to $V_2$. We now have two lists of nodes of the same size $(n+m)$.
    We can now build a $(n + m) * (n + m)$ cost matrix $C$ to match
    every node from $V_1$ to a unique node from $V_2$.

    The cost matrix will be made up of four parts :

    * The upper left submatrix of size $n * m$ represents the assignment
      costs of the real nodes. In the context of the Graph Edit Distance,
      it corresponds to the substitution edit operation. For
      $i < n$ and $j < m$, $C_{i, j}$ represents the substitution cost
      between `g1` node of index $i$ and `g2` node of index $j$.

    * The upper right submatrix of size $n * n$ represents the assignment
      costs of real nodes from `g1` with the empty nodes from `g2`. It
      corresponds to the deletion edit operation. For $i < n$ and
      $m \\leqslant j < n + m$, $C_{i, j}$ represents the deletion cost of
      node $i$ from `g1`. Note that every cost outside the diagonal of
      the submatrix is infinite. It means a node can only be deleted once.

    * The lower left submatrix of size $m * m$ represents the assignment
      costs of empty nodes from `g1` with real nodes from `g2`. It corresponds
      to the insertion edit operation. For $n \\leqslant i < n + m$ and
      $j < m$, $C_{i, j}$ represents the insertion cost of node $j$ in `g2`.
      Note that like the deletion submatrix, every value outside the
      submatrix's diagonal is infinite as we can't insert the same node twice.

    * The lower right submatrix of size $m * n$ represents the assignment
      costs of empty nodes. It only exists to ensure the *LSAP* solver works
      ans does not correspond to any edit operation.
      All of these costs are equal to 0 as they do not impact the process.

    The solution of the matching using this cost matrix results in two
    arrays of indices. The first one contains the rows indices (ie, the
    indices of the nodes from `g1`), and the second one being the indices
    of the assigned columns (ie, the assigned indices of the nodes from `g2`).

    Parameters
    ----------
    g1, g2: networkx.Graph
        Graphs between witch an assignment cost matrix will be computed.
        This cost matrix allows an algorithm (*LSAP* solver) to find
        an optimum node matching minimizing the assignment costs.
    cf: CostFunction, optional
        Cost function to build the cost matrix.
        By default, uses a :class:`.ConstantCostFunction` with costs of
        1 for substitution and 3 for insertion/deletion.

    Returns
    -------
    C: np.ndarray
        The cost matrix as a `numpy` array, computed using the given :class:`.CostFunction`

    Examples
    --------
    >>> import networkx as nx
    >>> # We create the graphs from SolverLSAP example
    >>> g1, g2 = nx.Graph(), nx.Graph()
    >>> g1.add_nodes_from(
    ...     [("u1", {"Label": 1}), ("u2", {"Label": 2}), ("u3", {"Label": 1})]
    ... )
    >>> g1.add_edges_from([("u1", "u2"), ("u2", "u3")])
    >>> g2.add_nodes_from([("v1", {"Label": 1}), ("v2", {"Label": 2})])
    >>> g2.add_edge("v1", "v2")
    >>> # And we define the function for nodes comparison
    >>> def compare_nodes(u, v, g1, g2):
    ...     return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]
    >>> # We create the cost function used to build the cost matrix
    >>> cf = nx.bipartite_ged.ConstantCostFunction(1, 2, 1, 2, compare_nodes)
    >>> # And we can compute the cost matrix :
    >>> nx.bipartite_ged.compute_bipartite_cost_matrix(g1, g2, cf)
    array([[ 0.,  1.,  2., inf, inf],
           [ 1.,  0., inf,  2., inf],
           [ 0.,  1., inf, inf,  2.],
           [ 2., inf,  0.,  0.,  0.],
           [inf,  2.,  0.,  0.,  0.]])

    We can see the four parts with the substitution costs on the upper left
    part, the square submatrix for insertion and the one for deletrion
    (with the edit costs of 2 and the infinite values), and the null submatrix.

    Note that we only defined a node comparison function to make this example simple.
    An edge comparison function should be used, especially if the provided cost function
    is likely to take edges into account for the nodes assignment costs.

    See Also
    --------
    :mod:`.solvers` : More details about the solution of the *LSAP*
    :mod:`.costfunctions` : Edit cost function to build the assignment cost matrix
    """
    import numpy as np

    if cf is None:
        cf = ConstantCostFunction(1, 3, 1, 3)

    n = g1.number_of_nodes()
    m = g2.number_of_nodes()
    nm = n + m
    C = np.ones([nm, nm]) * np.inf
    C[n:, m:] = 0

    insertion_costs = False
    for i, u in enumerate(g1.nodes()):
        C[i, m + i] = cf.cnd(u, g1)
        for j, v in enumerate(g2.nodes()):
            C[i, j] = cf.cns(u, v, g1, g2)
            if not insertion_costs:
                C[n + j, j] = cf.cni(v, g2)

    return C


def convert_mapping(
    rho: Sequence[int],
    varrho: Sequence[int],
    g1: nx.Graph,
    g2: nx.Graph,
) -> tuple:
    """Converts a node indices assignment to a
    node mapping using the networkx nodes IDs.

    Using the matching found by solving the *LSAP*, creates
    two dictionaries of nodes, to map each node of the
    graphs with its assigned node of the other graph.

    The mapping is symmetric. If we have node `u` from `g1`
    mapped in the first dict to the node `v` in `g2`, then
    the node `v` in the second dict will be mapped to `u`.

    In the case of node deletion, the mapping will only
    appear in the first dict, with the node mapped to `None`.
    In the case of node insertion, the mapping will only
    appear in the second dict, with the node mapped to `None`.
    Aside from these cases, only existing nodes are considered
    (ie, the case of two matched empty nodes is ignored).

    Parameters
    ----------
    rho, varrho: Sequence or array of ints
        Lists of indices representing the results of nodes matching.

        For each node of index `i` in `g1`, `rho[i]`
        is the index of matched node in `g2`.
        `varrho` is the reversed matching
    g1, g2: networkx.Graph
        Graphs between which the node index matching
        is converted into a ID node mapping

    Returns
    -------
    g1_to_g2, g2_to_g1 : dictionaries of nodes to nodes
        Converted mapping into dicts

    Raises
    ------
    ValueError
        If the lists of indices `rho` and `varrho` are not of the same size

    Examples
    --------
    >>> import networkx as nx
    >>> # We create the graph from SolverLSAP example
    >>> g1, g2 = nx.Graph(), nx.Graph()
    >>> g1.add_nodes_from(
    ...     [("u1", {"Label": 1}), ("u2", {"Label": 2}), ("u3", {"Label": 1})]
    ... )
    >>> g1.add_edges_from([("u1", "u2"), ("u2", "u3")])
    >>> g2.add_nodes_from([("v1", {"Label": 1}), ("v2", {"Label": 2})])
    >>> g2.add_edge("v1", "v2")
    >>> # The node comparison function :
    >>> def compare_nodes(u, v, g1, g2):
    ...     return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]
    >>> # The cost matrix :
    >>> cf = nx.bipartite_ged.ConstantCostFunction(1, 2, 1, 2, compare_nodes)
    >>> C = nx.bipartite_ged.compute_bipartite_cost_matrix(g1, g2, cf)
    >>> # And the optimum node matching :
    >>> solver = nx.bipartite_ged.SolverLSAP()
    >>> rho, varrho = solver.solve(C)
    >>> # Now we can convert it into dictionaries of nodes :
    >>> nx.bipartite_ged.convert_mapping(rho, varrho, g1, g2)
    ({'u1': None, 'u2': 'v2', 'u3': 'v1'}, {'v2': 'u2', 'v1': 'u3'})

    We obtain the node mapping between `g1` and `g2`, in accordance
    with the solution found in the :class:`.SolverLSAP` example.

    See Also
    --------
    :mod:`.solvers` : More information about the *LSAP* solution
    """
    if len(rho) != len(varrho):
        raise ValueError(
            f"Parameters `rho` and `varrho` must be of the same length ({len(rho)} != {len(varrho)})"
        )
    nodes1, nodes2 = list(g1.nodes()), list(g2.nodes())
    g1_to_g2, g2_to_g1 = {}, {}
    for g1_index, g2_index in zip(rho, varrho):
        if g1_index < len(nodes1):
            g1_to_g2[nodes1[g1_index]] = (
                nodes2[g2_index] if g2_index < len(nodes2) else None
            )
        if g2_index < len(nodes2):
            g2_to_g1[nodes2[g2_index]] = (
                nodes1[g1_index] if g1_index < len(nodes1) else None
            )
    return g1_to_g2, g2_to_g1
