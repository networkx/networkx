"""
Classes solving a Linear Sum Assignment Problem (*LSAP*)

Solving a *LSAP* allows to compute an optimum assignment
of each element from the two sets $A$ and $B$,
given a cost matrix $C$ where $C_{i, j}$ represents
the matching cost between $a_i \\in A$ and $b_j \\in B$

Sets $A$ and $B$ must have the same size ($|A| = |B| = n$).
Let $\\{ \\phi_1, \\dots, \\phi_{n} \\}$ be the solution of the *LSAP*
where element $a_i$ is matched with the element $b_{\\phi_i}$.

This solution minimizes the
matching cost $\\sum_{i = 1}^n C_{i, \\phi_i}$
"""

from typing import Protocol


class Solver(Protocol):
    """`Solver` Protocol

    Designs the optimum matching solver classes.

    Any custom solver must implement the `solve` method.
    """

    def solve(self, cost_matrix) -> tuple:
        """Compute optimum assignment between two sets where
        `cost_matrix` encodes the assignment costs : `cost_matrix[i, j]`
        contains the assignment cost between element of index `i` in $A$
        and element of index `j` in $B$.

        Parameters
        ----------
        cost_matrix : np.array
            The $n * n$ matching cost matrix between the two sets

        Returns
        -------
        rho, varrho : np.array
            `rho[i]` indicates the index in the second set of the element assigned to `i`

            `varrho[j]` indicates the index in the first set
            of the element assigned to `j` (inverse of rho)

        Notes
        -----
        `cost_matrix` must be a square matrix. Hence to ensure the full
        matching in the case of two graphs with different number of nodes,
        empty nodes are added to the matrix. The output arrays will then
        contain indices of nodes that do not exist in the graphs.
        Assume indices $i$ and $j$ are matched :

        * if they both exist in their graphs, it repretents a substitution
        * if only $i$ exists, it represents a deletion
        * if only $j$ exists, it represents an insertion

        If neither of them exist in the graphs, it can be ignored, it does
        not represent any edit operation and is the consequnce of
        the way the assignment cost matrix is built.

        See Also
        --------
        :func:`.compute_bipartite_cost_matrix` : More informations on the assignment cost matrix
        :func:`.convert_mapping` : A function to convert the *LSAP* solution into a node mapping
        """
        ...


class SolverLSAP:
    """LSAP Solver

    Solves a Linear Sum Assignment Problem between
    two sets given an assignment cost matrix.
    """

    def __init__(self):
        pass

    def solve(self, C) -> tuple:
        """Solves the LSAP using the Jonker-Volgenant Algorithm from `scipy` [1]_.

        Compute optimum assignment between two sets where
        `cost_matrix` encodes the assignment costs : `cost_matrix[i, j]`
        contains the assignment cost between element of index `i` in $A$
        and element of index `j` in $B$.

        Parameters
        ----------
        cost_matrix : np.array
            The $n * n$ matching cost matrix between the two sets

        Returns
        -------
        rho, varrho : np.array
            `rho[i]` indicates the index in the second set of the element assigned to `i`

            `varrho[j]` indicates the index in the first set
            of the element assigned to `j` (inverse of rho)

        Examples
        --------
        In this example, we use the :func:`.compute_bipartite_cost_matrix`
        function. We create 2 graphs of 3 and 2 nodes. The cost
        matrix will be a (2 + 3) * (2 + 3) matrix, and the solutions
        will be two `numpy` arrays of size (2 + 3).

        >>> import networkx as nx
        >>> # We create two very simple graphs
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
        >>> # We compute the cost matrix using a cost function :
        >>> cf = nx.bipartite_ged.ConstantCostFunction(1, 2, 1, 2, compare_nodes)
        >>> C = nx.bipartite_ged.compute_bipartite_cost_matrix(g1, g2, cf)
        >>> # And we use it along with the solver to find an optimum node matching :
        >>> solver = nx.bipartite_ged.SolverLSAP()
        >>> solver.solve(C)
        (array([0, 1, 2, 3, 4]), array([2, 1, 0, 3, 4]))

        The first array corresponds to the indices of the rows of the cost matrix
        (ie, the indices of the nodes from `g1`). The second array contains the
        matched indices of the columns (ie, the indices of the nodes from `g2`).

        For instance, we see that indices 2 and 0 are matched, which means
        node of index 2 from `g1` (`u3`) is matched with node of index 0 from
        `g2` (`v1`). We also see that nodes of indices 0 and 2 are matched,
        but there is no node of index 2 in `g2`. It represents the deletion
        of the node of index 0 from `g1` (`u1`).

        Notes
        -----
        `cost_matrix` must be a square matrix. Hence to ensure the full
        matching in the case of two graphs with different number of nodes,
        empty nodes are added to the matrix. The output arrays will then
        contain indices of nodes that do not exist in the graphs.
        Assume indices $i$ and $j$ are matched :

        * if they both exist in their graphs, it repretents a substitution
        * if only $i$ exists, it represents a deletion
        * if only $j$ exists, it represents an insertion

        If neither of them exist in the graphs, it can be ignored, it does
        not represent any edit operation and is the consequnce of
        the way the assignment cost matrix is built.

        See Also
        --------
        :func:`.compute_bipartite_cost_matrix` : More informations on the assignment cost matrix
        :func:`.convert_mapping` : A function to convert the *LSAP* solution into a node mapping

        References
        ----------
        .. [1] The SciPy Community, Documentation,
           scipy.optimize.linear_sum_assignment,
           https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
        """
        import scipy as sp

        row_ind, col_ind = sp.optimize.linear_sum_assignment(C)
        return row_ind, col_ind
