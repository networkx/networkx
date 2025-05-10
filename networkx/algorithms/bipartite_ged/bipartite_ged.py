"""
Graph Edit Distance module

Defines a fully configurable class, able
to approximate the Graph Edit Distance (*GED*)
between two graphs by computing an upper bound.
"""

from collections.abc import Callable
from typing import Any

import networkx as nx
from networkx.algorithms.bipartite_ged.bpged_utils import (
    compute_bipartite_cost_matrix,
    convert_mapping,
)
from networkx.algorithms.bipartite_ged.costfunctions import (
    ConstantCostFunction,
    CostFunction,
    NeighborhoodCostFunction,
    RiesenCostFunction,
)
from networkx.algorithms.bipartite_ged.solvers import Solver, SolverLSAP

__all__ = ["BipartiteGED"]


class BipartiteGED:
    """Bipartite Graph Edit Distance class

    Computes an upper bound of the GED between two graphs
    given a cost function and a node matching solver,
    by using the approximation algorithm of K. Riesen.

    This class can be used without advanced configuration
    by using the name of the cost function or solver and
    providing it other optional parameters.

    It can also be configured using the built-in classes,
    available in the :mod:`networkx.algorithms.bipartite_ged` module.

    And it can be given custom cost function or solver classes
    to test new parameters or improve the approximation.
    """

    _valid_cf = {"const", "riesen", "neighborhood"}
    _valid_solver = {"lsap"}
    _valid_cf_params = {
        "cns": (int, 0),
        "cni": (int, 1),
        "ces": (int, 0),
        "cei": (int, 1),
    }

    def __init__(
        self,
        cost_function: str | CostFunction = "const",
        cns: int = 1,
        cni: int = 1,
        ces: int = 1,
        cei: int = 1,
        compare_nodes: Callable | None = None,
        compare_edges: Callable | None = None,
        solver: str | Solver = "lsap",
    ):
        """Create a Graph Edit Distance estimator

        Parameters
        ----------
        cost_function : str or CostFunction (default: "const")
            If `str`, name of the :class:`.CostFunction` used for the node matching :

            * `const` : A cost function with constant costs

            * `riesen` : A cost function taking adjacent edges
              edit costs into account to improve the matching

            * `neighborhood` : A cost function taking adjacent edges and
              neighbors edit costs into account to improve the matching


            Else, the :class:`.CostFunction` instance to be used. The cost function
            must follow the design of the :class:`.CostFunction` protocol.
            (See *Warnings* section)

            If a :class:`.CostFunction` instance is given, the edit costs
            parameters will be ignored.

            By default, a :class:`.ConstantCostFunction` will be used,
            with the provided edit costs (of 1, by default).

        cns : int|float (default: 1)
            Node substitution cost (cannot be negative)

        cni : int|float (default: 1)
            Node insertion and deletion costs (cannot be negative nor zero)

        ces : int|float (default: 1)
            Edge substitution cost (cannot be negative)

        cei : int|float (default: 1)
            Edge insertion and deletion costs (cannot be negative nor zero)

        compare_nodes : Callable, optional
            Node comparison function. It defines how nodes can be considered
            equivalent. If two matched nodes are equivalent, substitution is
            not required anymore (the edit cost becomes 0).
            It will be called like

            .. code-block:: python

                compare_nodes(u, v, g1, g2)

            where `u` is a node of `g1`, and `v` a node of `g2`.

            Should return `True` if `u` and `v` are equivalent.

            If `None`, a constant cost will be used in all cases.

        compare_edges : Callable, optional
            Edge comparison function. Same as `compare_nodes`, it defines how
            edges can be considered equivalent (making the substitution cost 0).
            It will be called like

            .. code-block:: python

                compare_edges((u1, u2), (v1, v2), g1, g2)

            where `u1` and `u2` are nodes of `g1`, and `v1` and `v2` are
            nodes of `g2`. Also, there must be an edge between `u1` and
            `u2` as well as between `v1` and `v2`.

            Should return `True` if these edges are equivalent.

            If `None`, a constant cost will be used in all cases.

        solver : str or Solver (default: "lsap")
            If `str`, name of the LSAP solver :

            * `lsap` : A solver using the Jonker-Volgenant Algorithm (`scipy`)

            Else, the :class:`.Solver` instance to be used.

            The solver must follow the design of the :class:`.Solver` protocol.

            By default, a :class:`.SolverLSAP` will be used.

        Raises
        ------
        TypeError
            If the given cost is not an `int` or a `float`
        ValueError
            If a parameter does not match the constraints

        Warnings
        --------
        If a custom cost function or a custom solver is given, it must follow
        the design of the :class:`.CostFunction` or the :class:`.Solver` protocol.

        A custom cost function should be based on an elementary :class:`.CostFunction`
        (eg :class:`.ConstantCostFunction`). As it aims to enhance the matching result
        by increasing some edit costs, using this cost function to compute the
        approximation may result in an overastimated GED.

        Every built-in :class:`.CostFunction` is based on the :class:`.ConstantCostFunction`.
        If a custom cost function does not implement elementary costs, it
        should provide a `ccf` property to access the elementary cost function.
        If this property is not found, the custom cost function will be considered as
        an elementary cost function. If it was not supposed to be the case, the
        result of the approximation might be overestimated.

        See also
        --------

        networkx.algorithms.bipartite_ged.costfunctions : some cost function classes
        networkx.algorithms.bipartite_ged.solvers : some solver classes

        Notes
        -----

        * All Edit costs cannot be negative
        * Insertion and Deletion costs are equal and cannot be null
        """

        if isinstance(cost_function, str):
            for param, (param_name, (param_type, param_min)) in zip(
                (cns, cni, ces, cei), self._valid_cf_params.items()
            ):
                if not isinstance(param, param_type):
                    raise TypeError(
                        f"Unexpected type for `{param_name}`. Got `{type(param).__name__}` instead of `{param_type}`"
                    )
                if param < param_min:
                    raise ValueError(
                        f"Invalid value for parameter `{param_name}` ({param}). Should be at least {param_min}"
                    )

            # Every other CostFunction is based on a ConstantCostFunction
            self.cf: CostFunction
            self.solver: Solver
            ccf = ConstantCostFunction(cns, cni, ces, cei, compare_nodes, compare_edges)
            if cost_function == "riesen":
                self.cf = RiesenCostFunction(ccf)
            elif cost_function == "neighborhood":
                self.cf = NeighborhoodCostFunction(ccf)
            elif cost_function == "const":
                self.cf = ccf
            else:
                raise ValueError(
                    f"Invalid cost function `{cost_function}`, expected one of {', '.join(self._valid_cf)}"
                )
        else:
            self.cf = cost_function

        # TODO Add conditions on param 'solver' if new solvers are added
        if isinstance(solver, str):
            if solver == "lsap":
                self.solver = SolverLSAP()
            else:
                raise ValueError(
                    f"Invalid solver `{solver}`, expected one of {', '.join(self._valid_solver)}"
                )
        else:
            self.solver = solver

    def _valid_mapping(
        self,
        rho: dict[Any, Any | None],
        varrho: dict[Any, Any | None],
        g1: nx.Graph,
        g2: nx.Graph,
    ) -> None:
        """Checks whether the node mapping encoded in `rho`
        and `varrho` is valid (ie all their nodes exist in
        the graphs and none is forgotten)
        """
        for mapping, graph, param in [(rho, g1, "rho"), (varrho, g2, "varrho")]:
            if missing_node := set(graph) - set(mapping.keys()):
                raise ValueError(
                    f"Incomplete mapping : Missing nodes in `{param}` : {missing_node}"
                )
            if extra_node := set(mapping.keys()) - set(graph):
                raise KeyError(
                    f"Invalid mapping : Unknown nodes {extra_node} in `{param}`"
                )
        for u in g1:
            v = rho[u]
            if v is not None and varrho.get(v) != u:
                raise ValueError(
                    f"Asymetric mapping : node {u} mapped to {v}, but node {v} mapped to {varrho.get(v)}"
                )

    def ged(
        self,
        g1: nx.Graph,
        g2: nx.Graph,
        rho: dict[Any, Any | None] | None = None,
        varrho: dict[Any, Any | None] | None = None,
        return_mapping: bool = False,
    ) -> int | tuple:
        """Approximate Graph Edit Distance between `g1` and `g2`.

        The calculation can be performed based on a provided mapping.
        Otherwise, the mapping is computed using the provided parameters.

        Parameters
        ----------
        g1, g2: networkx.Graph
            Graphs between which the GED is approximated

        rho, varrho: dictionaries of nodes to nodes, optional
            Result of the mapping between nodes.

            If either of them is `None`, they will be computed.
            A node mapped to `None` indicates that it must
            be deleted (if in `rho`), or inserted (if in `varrho`)

        return_mapping: bool (default: `False`)
            If set to `True`, this method will also
            return the computed nodes mapping

        Returns
        -------
        ged : int
            The upper bound of the Graph Edit Distance
        rho, varrho : dictionnries of nodes to nodes
            Result of the mapping between nodes.

            Returned only if `return_mapping` is `True`

        Raises
        ------
        ValueError
            If the given mapping is either incomplete or asymmetric. (for
            instance, having `u1 -> v1` in `rho`, but `v1 -> u2` in `varrho`).

            Only if `rho` and `varrho` are not `None`.

        KeyError
            If a wrong node appears in `rho` or `varrho`.

            Only if `rho` and `varrho` are not `None`.

        Examples
        --------
        A simple use case :

        >>> import networkx as nx
        >>> g1 = nx.complete_graph(5)
        >>> g2 = nx.complete_graph(6)
        >>> bpged = nx.BipartiteGED("const", 1, 1, 1, 1)
        >>> bpged.ged(g1, g2)
        21

        Note that the graphs used here are not labelled, hence node or edge
        comparison function cannot be defined. This results in the substitution
        cost being used in all cases as the algorithm cannot consider two
        nodes or two edges equivalent.

        Now by creating custom graphs, we can give the comparison functions
        to compute a more accurate approximation of the GED :

        >>> # We create labelled graphs :
        >>> g1, g2 = nx.Graph(), nx.Graph()
        >>> g1.add_nodes_from(
        ...     [("u1", {"Label": 1}), ("u2", {"Label": 2}), ("u3", {"Label": 1})]
        ... )
        >>> g1.add_edges_from(
        ...     [("u1", "u2", {"weight": 1}), ("u2", "u3", {"weight": 2})]
        ... )
        >>> g2.add_nodes_from([("v1", {"Label": 1}), ("v2", {"Label": 2})])
        >>> g2.add_edge("v1", "v2", weight=1)
        >>> # And we define the comparison functions :
        >>> def compare_nodes(u, v, g1, g2):
        ...     return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]
        >>> def compare_edges(e1, e2, g1, g2):
        ...     return g1[e1[0]][e1[1]]["weight"] == g2[e2[0]][e2[1]]["weight"]
        >>> # Now we can recreate our GED estimator and compute the approximation :
        >>> bpged = nx.BipartiteGED("const", 1, 1, 1, 1, compare_nodes, compare_edges)
        >>> bpged.ged(g1, g2)
        3

        This is also possible to provide a :class:`.CostFunction` (see
        :mod:`.costfunctions`), or to use the :class:`.RiesenCostFunction` or the
        :class:`.NeighborhoodCostFunction` which are more complex cost functions, and
        particularly useful for graphs with a larger number of nodes and edges.
        """
        if (rho is None) or (varrho is None):
            C = compute_bipartite_cost_matrix(g1, g2, self.cf)
            r, v = self.solver.solve(C)
            rho, varrho = convert_mapping(r, v, g1, g2)
        else:
            self._valid_mapping(rho, varrho, g1, g2)
        assert (rho is not None) and (varrho is not None)

        # The final cost is based on elementary costs
        # If improved cost functions are used, the result will be overestimaed.
        # ccf = self.cf if isinstance(self.cf, ConstantCostFunction) else self.cf.ccf
        ccf = self.cf.ccf if hasattr(self.cf, "ccf") else self.cf

        # Nodes edit operations
        ged = 0
        for v in g1.nodes():
            phi_i = rho[v]
            if phi_i is None:
                ged += ccf.cnd(v, g1)
            else:
                ged += ccf.cns(v, phi_i, g1, g2)
        for u in g2.nodes():
            phi_j = varrho[u]
            if phi_j is None:
                ged += ccf.cni(u, g2)

        # Edges edit operations
        for e in g1.edges():
            i = e[0]
            j = e[1]
            phi_i = rho[i]
            phi_j = rho[j]
            if (phi_i is not None) and (phi_j is not None):
                if any(x == phi_j for x in g2[phi_i]):
                    e2 = (phi_i, phi_j)
                    min_cost = min(
                        ccf.ces(e, e2, g1, g2), ccf.ced(e, g1) + ccf.cei(e2, g2)
                    )
                    ged += min_cost
                else:
                    ged += ccf.ced(e, g1)
            else:
                ged += ccf.ced(e, g1)
        for e in g2.edges():
            i = e[0]
            j = e[1]
            phi_i = varrho[i]
            phi_j = varrho[j]
            if (phi_i is not None) and (phi_j is not None):
                if not any(x == phi_j for x in g1[phi_i]):
                    ged += ccf.cei(e, g2)
            else:
                ged += ccf.ced(e, g2)

        return (ged, rho, varrho) if return_mapping else ged
