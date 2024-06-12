r"""Compute the DomiRank centrality for the graph `G`."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["domirank"]


# @nx._dispatchable(edge_attrs="weight")
@not_implemented_for("multigraph")
def domirank(
    G,
    method="iterative",
    alpha=0.95,
    dt=0.1,
    epsilon=1e-5,
    max_iter=1000,
    patience=10,
    max_depth=50,
):
    r"""Compute the DomiRank centrality for the graph `G`.

    DomiRank centrality [1]_ computes the centrality for a node by aggregating
    1 minus the centrality of each node in its neighborhood. This essentially finds the
    dominance of a node in its neighborhood, where the parameter $\alpha$ determines
    the amount of competition in the system by modulating $\sigma = \alpha/|\lambda_N|$.
    The competition parameter $\alpha$ tunes the balance of DomiRank centrality's
    integration of local and global topological information, to find nodes that are either
    locally or globally dominant. It is important to note that for the iterative formulation
    of DomiRank (as seen below) the competition parameter is bounded: $\sigma \in (0,1/|\lambda_N|]$.
    The DomiRank centrality of node $i$ is defined as the stationary solution to the dynamical system:

    .. math::

        d\Gamma_i(t)/dt = \sigma (d_i - \sum_j A_{ij} \Gamma_j(t)) - \Gamma_i(t),

    where $A$ is the adjacency matrix, $\lambda_N$ its smallest eigenvalue, and $d_i$ is the degree of node $i$.
    Note that the definition presented here is valid for unweighted, weighted,
    directed, and undirected networks, so in the more general case,
    a non-zero entry of the adjacency matrix $A_{ij}=w_{ij}$
    represents the existence of a link from node $i$ to node $j$
    with a weight $w_{ij}$. The steady state solution to this equation
    is computed using Newton's method. In general, one will notice that important
    nodes identified by DomiRank will be connected to a lot of other,
    unimportant nodes. However, positionally important nodes
    can also be dominated by joint-dominance of nodes, that work together
    in order to dominate the positionally important node. This centrality
    gives rise to many interesting emergent phenomena;
    see [1]_ for more information.
    DomiRank centrality can also be
    expressed in its analytical form, where the competition can now be
    supercharged - i.e. $\sigma \in [0,+\infty)$. The analytical equation
    takes the form:

    .. math::

        \boldsymbol{\Gamma} = \sigma (\sigma A + I_{N\times N})^{-1}  A  \boldsymbol{1}_{N\times 1},

    where $I$ is the identity matrix. This analytical equation can be solved
    as a linear system.

    DomiRank tends to have only positive values for relatively low
    competition levels ($\sigma \to 0$). However as the competition
    level increases, negative values might emerge. Nodes with negative
    dominance represent completely submissive nodes, which instead
    of fighting for their resources/dominance, directly give up these
    resources to their neighborhood.

    Finally, DomiRank centrality does not require the network to be weakly or strongly
    connected, and can be applied to networks with many components.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    method: string, optional (default="iterative")
        The {``"analytical"``, ``"iterative"``} method
        for computing DomiRank. Note that the computational
        time cost of the analytical method is large for
        non-regular graphs, but provides the true DomiRank.

    alpha: float, optional (default=0.95)
        The level of competition for DomiRank.

    dt: float, optional (default=0.1)
        The step size for the Newton iteration.

    epsilon: float, optional (default=1e-5)
        The relative stopping criterion for convergence.

    max_iter: integer, optional (default=100)
        Maximum number of Newton iterations allowed.
        It is recommended that ''max_iter >= 50''.

    patience: integer, optional (default=10)
        The number of steps between convergence checks.
        It is recommended that ''patience >= 10''.

    max_depth: integer, optional (default=50)
        The number of bisection steps to find the smallest
        eigenvalue. Having lower 'max_depth' reduces the
        accuracy of the smallest eigenvalue computation, but improves performance.
        It is recommended that ''max_depth > 25''.

    Returns
    -------
    nodes : dictionary
        Dictionary keyed by node with DomiRank centrality of the node as value.

    sigma : float
        $\alpha$ normalized by the smallest eigenvalue.

    converged : boolean | None
        Whether the centrality computation converged. Returns ``None`` if ``method = "analytical"``.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> centrality, sigma, converged = nx.domirank(G)
    >>> print([f"{node} {centrality[node]:0.2f}" for node in centrality])
    ['0 -0.54', '1 1.98', '2 -1.08', '3 1.98', '4 -0.54']

    Raises
    ------
    NetworkXPointlessConcept
        If the graph `G` is the null graph.

    NetworkXUnfeasible
        If `alpha` is negative (and thus outside its bounds): ``alpha < 0``.

        If ``alpha > 1`` when ``method = "iterative"``.

    NetworkXAlgorithmError
        If the method is not one of {``"analytical"``, ``"iterative"``}.

        If ``patience > max_iter // 3``.

        If ``max_iter < 1``.

        If 'dt' does not satisfy: ``0 < dt < 1``.

        If `epsilon` is not greater than zero: ``epsilon <= 0``.

        If ``max_depth < 1``.

    Warning
        If supercharging the competition parameter for the analytical solution: ``alpha > 1`` and ``method = "analytical"``.

        If ``method="analytical"`` for a large graph, i.e. more than ``5000`` nodes, as the algorithm will be slow.

    See Also
    --------
    :func:`~networkx.algorithms.centrality.degree_centrality`
    :func:`~networkx.algorithms.link_analysis.pagerank_alg.pagerank`
    :func:`~networkx.algorithms.link_analysis.hits_alg.hits`

    References
    ----------
    .. [1] Engsig, M., Tejedor, A., Moreno, Y. et al.
        "DomiRank Centrality reveals structural fragility of complex networks via node dominance."
        Nat Commun 15, 56 (2024). https://doi.org/10.1038/s41467-023-44257-0
    """
    import numpy as np
    import scipy as sp

    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "cannot compute centrality for the null graph"
        )
    if patience > max_iter // 3:
        raise nx.NetworkXAlgorithmError("it is mandatory that max_iter > 3 * patience")
    if max_iter < 1:
        raise nx.NetworkXAlgorithmError("it is mandatory that max_iter >= 1")
    if patience < 1:
        raise nx.NetworkXAlgorithmError("it is mandatory that patience >= 1")
    if max_depth < 1:
        raise nx.NetworkXAlgorithmError("it is mandatory that max_depth >= 1")
    if dt <= 0 or dt >= 1:
        raise nx.NetworkXAlgorithmError(
            "it is mandatory that dt be bounded such that: 0 < dt < 1"
        )
    if epsilon <= 0:
        raise nx.NetworkXAlgorithmError(
            "it is mandatory that epsilon > 0 and recommended that epsilon = 1e-5"
        )
    GAdj = nx.to_scipy_sparse_array(G)  # convert to scipy sparse csr array

    # Here we create a warning (I couldn't find a networkxwarning, only exceptions and erros), that suggests to use the iterative formulation of DomiRank rather than the analytical form.
    # Here we create another warning for alpha being supercharged
    if alpha > 1:
        if method == "iterative":
            raise nx.NetworkXUnfeasible(
                "supercharging the competition parameter (alpha > 1) requires the method = 'analytical' argument"
            )
        else:
            import warnings

            warnings.warn(
                "The competition parameter is supercharged (alpha > 1); this is only allowed because method = 'analytical'"
            )
    if alpha < 0:
        raise nx.NetworkXUnfeasible(
            "the competition parameter alpha must be positive: alpha > 0"
        )
    if GAdj.shape[0] > 5000 and method == "analytical":
        import warnings

        warnings.warn("consider using method = 'iterative' for large systems")

    # Here we renormalize alpha with the smallest eigenvalue (most negative eigenvalue) by calling the "hidden" function _find_smallest_eigenvalue()
    # Note, this function always uses the iterative definition
    sigma = np.abs(
        alpha
        / _find_smallest_eigenvalue(
            GAdj,
            max_depth=max_depth,
            dt=dt,
            epsilon=epsilon,
            max_iter=max_iter,
            patience=patience,
        )
    )
    match method:
        case "analytical":
            converged = None
            psi = sp.sparse.linalg.spsolve(
                sigma * GAdj + sp.sparse.identity(GAdj.shape[0]),
                sigma * GAdj.sum(axis=-1),
            )
        case "iterative":
            psi, converged = _domirank_iterative(
                GAdj,
                sigma=sigma,
                dt=dt,
                epsilon=epsilon,
                max_iter=max_iter,
                patience=patience,
            )
        case _:
            raise nx.NetworkXUnfeasible(
                "method must be one of {'iterative', 'analytical'}"
            )
    psi = dict(zip(G, (psi).tolist()))
    return psi, sigma, converged


def _find_smallest_eigenvalue(
    G,
    min_val=0,
    max_val=1,
    max_depth=50,
    dt=0.1,
    epsilon=1e-5,
    max_iter=100,
    patience=10,
):
    """
    This function is simply used to find the smallest eigenvalue, by seeing when the DomiRank algorithm diverges. It uses
    a kind of binary search algorithm, however, with a bias to larger eigenvalues, as finding divergence is faster than
    verifying convergence.
    This function outputs the smallest eigenvalue - i.e. most negative eigenvalue.
    """
    x = (min_val + max_val) / G.sum(axis=-1).max()
    for _ in range(max_depth):
        if max_val - min_val < epsilon:
            break
        _, converged = _domirank_iterative(
            G, sigma=x, dt=dt, epsilon=epsilon, max_iter=max_iter, patience=patience
        )
        if converged:
            min_val = x
        else:
            max_val = (x + max_val) / 2
        x = (min_val + max_val) / 2
    final_val = (max_val + min_val) / 2
    return -1 / final_val


def _domirank_iterative(GAdj, sigma=0, dt=0.1, epsilon=1e-5, max_iter=100, patience=10):
    """
    This function is used for the iterative computation of DomiRank when `method = "iterative"`.
    It is also used to find the smallest eigenvalue - i.e. called in the `_find_smallest_eigenvalue()` function.
    It yields a boolean indicating convergence, and an array of the DomiRank values ordered according to `G`'s adjacency matrix.
    """
    import numpy as np

    # store this to prevent more redundant calculations in the future
    pGAdj = sigma * GAdj.astype(np.float32)
    # initialize a proportionally (to system size) small non-zero uniform vector
    psi = np.ones(pGAdj.shape[0], dtype=np.float32) / pGAdj.shape[0]
    # initialize a zero array to store values (this could be done with a smaller array with some smart indexing, but isn't computationally or memory heavy)
    max_vals = np.zeros(max_iter // patience, dtype=np.float32)
    # ensure dt is a float
    dt = np.float32(dt)
    # start a counter
    j = 0
    # set up a boundary condition for stopping divergence
    boundary = epsilon * pGAdj.shape[0] * dt
    for i in range(max_iter):
        # DomiRank iterative definition
        temp_val = ((pGAdj @ (1 - psi)) - psi) * dt
        # Newton iteration addition step
        psi += temp_val.real
        # Here we do the checking to see if we are diverging
        if i % patience == 0:
            if np.abs(temp_val).sum() < boundary:
                break
            max_vals[j] = temp_val.max()
            if j >= 2:
                if max_vals[j] > max_vals[j - 1] and max_vals[j - 1] > max_vals[j - 2]:
                    # If we are diverging, return the current step, but, with the argument that you have diverged.
                    return psi, False
            j += 1
    return psi, True
