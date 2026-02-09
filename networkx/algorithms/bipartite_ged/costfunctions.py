"""
Classes encoding cost functions

A cost function class must provide elementary
costs for elementary edit operations. Namely:

- cns : node substitution cost
- cnd : node deletion cost
- cni : node insertion cost

- ces : edge substitution cost
- ced : edge deletion cost
- cei : edge insertion cost
"""

import sys
from collections.abc import Callable
from typing import Any, Protocol

import networkx as nx


class CostFunction(Protocol):
    """`CostFunction` protocol

    Designs the methods for classes defining cost functions.

    Any custom cost function must implement these methods

    Notes
    -----
    Edges' type used in these methods are a 2-tuple of nodes.
    """

    def cns(self, node_u: Any, node_v: Any, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between
        `node_u` from `g1` and `node_v` from `g2`.

        Parameters
        ----------
        node_u : Any
            Source node in `g1`
        node_v : Any
            Target node in `g2`
        g1 : networkx.Graph
            Graph containing `node_u`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        ...

    def cnd(self, node_u: Any, g1: nx.Graph) -> int:
        """Computes the deletion cost of `node_u` in `g1`.

        Parameters
        ----------
        node_u : Any
            Node to delete from `g1`
        g1 : networkx.Graph
            Graph containing `node_u`

        Returns
        -------
        A positive int value
        """
        ...

    def cni(self, node_v: Any, g2: nx.Graph) -> int:
        """Computes the insertion cost of `node_v` in `g2`.

        Parameters
        ----------
        node_v : Any
            Node to insert into `g2`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        ...

    def ces(self, e1: tuple, e2: tuple, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between edge
        `e1` from `g1` and edge `e2` from `g2`.

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Source edge in `g1`
        e2 : tuple[Any, Any]
            Target edge in `g2`
        g1 : networkx.Graph
            Graph containing `e1`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        ...

    def ced(self, e1: tuple, g1: nx.Graph) -> int:
        """Computes the deletion cost of edge `e1` in `g1`.

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Edge to delete from `g1`
        g1 : networkx.Graph
            Graph containing `e1`

        Returns
        -------
        A positive int value
        """
        ...

    def cei(self, e2: tuple, g2: nx.Graph) -> int:
        """Computes the insertion cost of edge `e2` in `g2`.

        Parameters
        ----------
        e2 : tuple[Any, Any]
            Edge to insert into `g2`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        ...


class ConstantCostFunction:
    """Define a symmetric constant cost function for edit operations"""

    def __init__(
        self,
        cns: int,
        cni: int,
        ces: int,
        cei: int,
        node_comp: Callable | None = None,
        edge_comp: Callable | None = None,
    ):
        """Creates an elementary constant cost function for edit operations

        Parameters
        ----------
        cns : int
            Node substitution cost
        cni : int
            Node insertion and deletion cost
        ces : int
            Edge substitution cost
        cei : int
            Edge insertion and deletion cost
        node_comp : Callable(Any, Any, nx.Graph, nx.Graph) -> bool, optional
            Boolean function for node comparison. The function will be called this way :

            .. code-block:: python

                node_comp(u, v, g1, g2)

            with `u` and `v`, nodes from resp. `g1` and `g2`

            Shoud return `True` if nodes `u` and `v` are equivalent

            For instance, if we want to compare the node attribute `"Label"`
            to measure the similarity, we can define the comparison function :

            .. code-block:: python

                def compare_nodes(u, v, g1, g2):
                    return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]

        edge_comp : Callable(tuple[Any, Any], tuple[Any, Any], nx.Graph, nx.Graph) -> bool, optional
            Boolean function for edge comparison. The function will be called this way :

            .. code-block:: python

                edge_comp(e1, e2, g1, g2)

            with `e1` and `e2`, edges from resp. `g1` and `g2`

            Should return `True` if edges `e1` and `e2` are equivalent

            For instance, if we want to compare the edge attribute `"weight"`
            to measure the similarity, we can define the comparison function :

            .. code-block:: python

                def compare_edges(e1, e2, g1, g2):
                    return g1[e1[0]][e1[1]]["weight"] == g2[e2[0]][e2[1]]["weight"]

        Examples
        --------
        >>> import networkx as nx
        >>> # We define first the labelled example graphs
        >>> g1, g2 = nx.Graph(), nx.Graph()
        >>> g1.add_nodes_from(
        ...     [("u1", {"Label": 1}), ("u2", {"Label": 2}), ("u3", {"Label": 3})]
        ... )
        >>> g1.add_edges_from(
        ...     [
        ...         ("u1", "u2", {"weight": 1}),
        ...         ("u2", "u3", {"weight": 2}),
        ...         ("u3", "u1", {"weight": 1}),
        ...     ]
        ... )
        >>> g2.add_nodes_from(
        ...     [("v1", {"Label": 1}), ("v2", {"Label": 2}), ("v3", {"Label": 4})]
        ... )
        >>> g2.add_edges_from(
        ...     [("v1", "v2", {"weight": 2}), ("v2", "v3", {"weight": 1})]
        ... )
        >>> # Then we define the comparison functions
        >>> # If they return True, the substitution cost is 0
        >>> def compare_nodes(u, v, g1, g2):
        ...     return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]
        >>> def compare_edges(e1, e2, g1, g2):
        ...     return g1[e1[0]][e1[1]]["weight"] == g2[e2[0]][e2[1]]["weight"]
        >>> # Finally, we create our cost function
        >>> # We use here cost of 1 for any substitution, and a cost of 2
        >>> # for any insertion and deletion (for both nodes and edges)
        >>> cf = nx.bipartite_ged.ConstantCostFunction(
        ...     1, 2, 1, 2, compare_nodes, compare_edges
        ... )
        >>>
        >>> # The substitution cost of 2 similar nodes is 0 :
        >>> cf.cns("u1", "v1", g1, g2)
        0
        >>> # But for different nodes, it's 1 :
        >>> cf.cns("u3", "v3", g1, g2)
        1
        >>> # It works the same way for the edges :
        >>> cf.ces(("u1", "u2"), ("v1", "v2"), g1, g2)
        1
        >>> cf.ces(("u1", "u3"), ("v2", "v3"), g1, g2)
        0
        >>> # And the costs for node deletion and insertion
        >>> # (It works the same for edges)
        >>> cf.cnd("u3", g1)
        2
        >>> cf.cni("v3", g2)
        2

        See Also
        --------
        :class:`.RiesenCostFunction` : An improved cost function
        :class:`.NeighborhoodCostFunction` : An extended version of `RiesenCostFunction`

        Notes
        -----
        * An edge is a `tuple` of 2 nodes (`Any`)
        * `node_comp` and `edge_comp` should return `True`
          whether the nodes/edges can be considered as equivalent
        * Equivalent nodes or edges do not require a substitution, thus the substitution cost becomes 0
        * If a comparison function is not given, nodes/edges cannot considered equivalent
        """
        self.cns_ = cns
        self.cni_ = self.cnd_ = cni
        self.ces_ = ces
        self.cei_ = self.ced_ = cei
        self.compare_nodes = (
            node_comp if node_comp is not None else (lambda u, v, g1, g2: False)
        )
        self.compare_edges = (
            edge_comp if edge_comp is not None else (lambda e1, e2, g1, g2: False)
        )

    def cns(self, node_u: Any, node_v: Any, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between
        `node_u` from `g1` and `node_v` from `g2`.

        Parameters
        ----------
        node_u : Any
            Source node in `g1`
        node_v : Any
            Target node in `g2`
        g1 : networkx.Graph
            Graph containing `node_u`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        return 0 if self.compare_nodes(node_u, node_v, g1, g2) else self.cns_

    def cnd(self, node_u: Any, g1: nx.Graph) -> int:
        """Computes the deletion cost of `node_u` in `g1`.

        Parameters
        ----------
        node_u : Any
            Node to delete from `g1`
        g1 : networkx.Graph
            Graph containing `node_u`

        Returns
        -------
        A positive int value
        """
        return self.cnd_

    def cni(self, node_v: Any, g2: nx.Graph) -> int:
        """Computes the insertion cost of `node_v` in `g2`.

        Parameters
        ----------
        node_v : Any
            Node to insert into `g2`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        return self.cni_

    def ces(self, e1: tuple, e2: tuple, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between edge
        `e1` from `g1` and edge `e2` from `g2`.

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Source edge in `g1`
        e2 : tuple[Any, Any]
            Target edge in `g2`
        g1 : networkx.Graph
            Graph containing `e1`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        return 0 if self.compare_edges(e1, e2, g1, g2) else self.ces_

    def ced(self, e1: tuple, g1: nx.Graph) -> int:
        """Computes the deletion cost of edge `e1` in `g1`.

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Edge to delete from `g1`
        g1 : networkx.Graph
            Graph containing `e1`

        Returns
        -------
        A positive int value
        """
        return self.ced_

    def cei(self, e2: tuple, g2: nx.Graph) -> int:
        """Computes the insertion cost of edge `e2` in `g2`.

        Parameters
        ----------
        e2 : tuple[Any, Any]
            Edge to insert into `g2`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        return self.cei_


class RiesenCostFunction:
    """Cost function associated to the computation of a cost matrix between nodes for LSAP

    Features the very local graph structure to improve the matching by increasing
    the nodes assignement costs based on the possible adjacent edges edit costs.
    """

    def __init__(self, cf: CostFunction, lsap_solver: Callable | None = None):
        """Creates a cost function taking the node's edges edit costs into account

        Parameters
        ----------
        cf : CostFunction
            The cost function for elementary edit costs
        lsap_solver : Callable(np.ndarray) -> tuple[np.ndarray, np.ndarray], optional
            Function to solve the LSAP problem. It will be given a cost matrix and must
            return the optimum nodes matching as 2 `numpy` arrays of rows and cols indices.
            If `None`, the `linear_sum_assignment` function from `scipy` will be used.

        Examples
        --------

        By using the same graphs and cost function from the `ConstantCostFunction` example
        and the same comparison functions and the `ConstantCostFunction` we created :

        >>> import networkx as nx
        >>> # We take back the ConstantCostFunction example
        >>> g1, g2 = nx.Graph(), nx.Graph()
        >>> g1.add_nodes_from(
        ...     [("u1", {"Label": 1}), ("u2", {"Label": 2}), ("u3", {"Label": 3})]
        ... )
        >>> g1.add_edges_from(
        ...     [
        ...         ("u1", "u2", {"weight": 1}),
        ...         ("u2", "u3", {"weight": 2}),
        ...         ("u3", "u1", {"weight": 1}),
        ...     ]
        ... )
        >>> g2.add_nodes_from(
        ...     [("v1", {"Label": 1}), ("v2", {"Label": 2}), ("v3", {"Label": 4})]
        ... )
        >>> g2.add_edges_from(
        ...     [("v1", "v2", {"weight": 2}), ("v2", "v3", {"weight": 1})]
        ... )
        >>>
        >>> def compare_nodes(u, v, g1, g2):
        ...     return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]
        >>> def compare_edges(e1, e2, g1, g2):
        ...     return g1[e1[0]][e1[1]]["weight"] == g2[e2[0]][e2[1]]["weight"]
        >>>
        >>> cf = nx.bipartite_ged.ConstantCostFunction(
        ...     1, 2, 1, 2, compare_nodes, compare_edges
        ... )
        >>>
        >>> # We define the improved cost function
        >>> # using the ConstantCostFunction cf
        >>> rcf = nx.bipartite_ged.RiesenCostFunction(cf)
        >>> # The substitution cost is not 0 anymore as
        >>> # the adjacent edges are not the same
        >>> rcf.cns("u1", "v1", g1, g2)
        3.0
        >>> # But here, the adjacent edges have the same weights
        >>> rcf.cns("u2", "v2", g1, g2)
        0.0
        >>> # These edges are also taken into account for deletion and insertion
        >>> rcf.cnd("u1", g1)
        6
        >>> rcf.cni("v3", g2)
        4

        Note that the edges edit costs are the same as for the given `CostFunction`,
        which is here the `ConstantCostFunction` defined in its example.

        See Also
        --------
        :class:`.ConstantCostFunction` : The cost function for elementary costs
        :class:`.NeighborhoodCostFunction` : An extended version of this cost function

        Notes
        -----
        To improve the matching, this cost function takes the edit costs of
        adjacent edges into account to compute the node edit costs.

        The assignment costs for edges is based on the given `CostFunction`.
        Hence, it is important for this given cost function to be able to
        compare edges (ie, by providing an edges comparison function).
        """
        import numpy as np
        import scipy as sp

        self.np = np
        self.cf_ = cf
        self.lsap_solver_ = (
            lsap_solver
            if lsap_solver is not None
            else sp.optimize.linear_sum_assignment
        )

    def cns(self, node_u: Any, node_v: Any, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between
        `node_u` from `g1` and `node_v` from `g2`.

        The result is based on the comparison of adjacent edges of `node_u`
        with adjacent edges of `node_v`. This comparison aims to match these
        edges by using the edge edit cost function from the given `CostFunction`.

        Parameters
        ----------
        node_u : Any
            Source node in `g1`
        node_v : Any
            Target node in `g2`
        g1 : networkx.Graph
            Graph containing `node_u`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        n = len(g1[node_u])
        m = len(g2[node_v])
        sub_C = self.np.ones([n + m, n + m]) * sys.maxsize
        sub_C[n:, m:] = 0
        i = 0
        l_nbr_u = g1[node_u]
        l_nbr_v = g2[node_v]
        for nbr_u in l_nbr_u:
            j = 0
            e1 = (node_u, nbr_u)
            for nbr_v in g2[node_v]:
                e2 = (node_v, nbr_v)
                sub_C[i, j] = self.cf_.ces(e1, e2, g1, g2)
                j += 1
            i += 1

        i = 0
        for nbr_u in l_nbr_u:
            sub_C[i, m + i] = self.cf_.ced((node_u, nbr_u), g1)
            i += 1

        j = 0
        for nbr_v in l_nbr_v:
            sub_C[n + j, j] = self.cf_.cei((node_v, nbr_v), g2)
            j += 1
        row_ind, col_ind = self.lsap_solver_(sub_C)
        cost = self.np.sum(sub_C[row_ind, col_ind])
        return self.cf_.cns(node_u, node_v, g1, g2) + cost.item()

    def cnd(self, node_u: Any, g1: nx.Graph) -> int:
        """Computes the deletion cost of `node_u` in `g1`.

        The result is based on the existing adjacent edges deletion costs,
        as a node deletion causes its adjacent edges to be deleted too.
        This deletion cost is provided by the given `CostFunction`.

        Parameters
        ----------
        node_u : Any
            Node to delete from `g1`
        g1 : networkx.Graph
            Graph containing `node_u`

        Returns
        -------
        A positive int value
        """
        cost = 0
        for nbr in g1[node_u]:
            cost += self.cf_.ced((node_u, nbr), g1)

        return self.cf_.cnd(node_u, g1) + cost

    def cni(self, node_v: Any, g2: nx.Graph) -> int:
        """Computes the insertion cost of `node_v` in `g2`.

        The result is based on the existing adjacent edges insertion costs,
        as a node insertion causes its adjacent edges to be inserted too.
        This insertion cost is provided by the given `CostFunction`.

        Parameters
        ----------
        node_v : Any
            Node to insert into `g2`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        cost = 0
        for nbr in g2[node_v]:
            cost += self.cf_.cei((node_v, nbr), g2)
        return self.cf_.cni(node_v, g2) + cost

    def ces(self, e1: tuple, e2: tuple, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between edge
        `e1` from `g1` and edge `e2` from `g2`.

        This substitution cost is provided by the given `CostFunction`.

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Source edge in `g1`
        e2 : tuple[Any, Any]
            Target edge in `g2`
        g1 : networkx.Graph
            Graph containing `e1`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        return self.cf_.ces(e1, e2, g1, g2)

    def ced(self, e1: tuple, g1: nx.Graph) -> int:
        """Computes the deletion cost of edge `e1` in `g1`.

        This deletion cost is provided by the given `CostFunction`

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Edge to delete from `g1`
        g1 : networkx.Graph
            Graph containing `e1`

        Returns
        -------
        A positive int value
        """
        return self.cf_.ced(e1, g1)

    def cei(self, e2: tuple, g2: nx.Graph) -> int:
        """Computes the insertion cost of edge `e2` in `g2`.

        This insertion cost is provided by the given `CostFunction`

        Parameters
        ----------
        e2 : tuple[Any, Any]
            Edge to insert into `g2`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        return self.cf_.cei(e2, g2)

    @property
    def ccf(self) -> CostFunction:
        """Accesses the associated elementary cost function

        Returns
        -------
        The associated elementary `CostFunction`
        """
        return self.cf_


class NeighborhoodCostFunction:
    """Cost function associated to the computation of a cost matrix between nodes for LSAP

    In the same way as :class:`.RiesenCostFunction`, it features the local graph structure to improve the
    matching by increasing assignment costs based on possible edit costs on adjacent edges and neighbors.
    """

    def __init__(self, cf: CostFunction, lsap_solver: Callable | None = None):
        """Creates a cost function taking the node's edges and neighbors edit costs into account

        Parameters
        ----------
        cf : CostFunction
            The cost function for elementary edit costs
        lsap_solver : Callable(np.ndarray) -> tuple[np.ndarray, np.ndarray]
            (default: the `linear_sum_assignment` function from `scipy`)
            Function to solve the LSAP problem. It will be given a cost matrix and must
            return the optimum nodes matching as 2 `numpy` arrays of rows and cols indices

        Examples
        --------

        By using the same graphs from the `ConstantCostFunction` example and the same
        comparison functions and the `ConstantCostFunction` we created :

        >>> import networkx as nx
        >>> # We take back the ConstantCostFunction example
        >>> g1, g2 = nx.Graph(), nx.Graph()
        >>> g1.add_nodes_from(
        ...     [("u1", {"Label": 1}), ("u2", {"Label": 2}), ("u3", {"Label": 3})]
        ... )
        >>> g1.add_edges_from(
        ...     [
        ...         ("u1", "u2", {"weight": 1}),
        ...         ("u2", "u3", {"weight": 2}),
        ...         ("u3", "u1", {"weight": 1}),
        ...     ]
        ... )
        >>> g2.add_nodes_from(
        ...     [("v1", {"Label": 1}), ("v2", {"Label": 2}), ("v3", {"Label": 4})]
        ... )
        >>> g2.add_edges_from(
        ...     [("v1", "v2", {"weight": 2}), ("v2", "v3", {"weight": 1})]
        ... )
        >>>
        >>> def compare_nodes(u, v, g1, g2):
        ...     return g1.nodes[u]["Label"] == g2.nodes[v]["Label"]
        >>> def compare_edges(e1, e2, g1, g2):
        ...     return g1[e1[0]][e1[1]]["weight"] == g2[e2[0]][e2[1]]["weight"]
        >>>
        >>> cf = nx.bipartite_ged.ConstantCostFunction(
        ...     1, 2, 1, 2, compare_nodes, compare_edges
        ... )
        >>>
        >>> # We define the improved cost function
        >>> # using the ConstantCostFunction cf
        >>> ncf = nx.bipartite_ged.NeighborhoodCostFunction(cf)
        >>> # Unlike the RiesenCostFunction, as the neighbors
        >>> # are not similar, the cost is not 0
        >>> ncf.cns("u2", "v2", g1, g2)
        2.0

        The deletion and insertion costs are the same as for the `RiesenCostFunction`, and the
        edges edit costs are also from the given `CostFunction` (here, a `ConstantCostFunction`).
        The improvement focuses on the substitution cost.

        See Also
        --------
        :class:`.ConstantCostFunction` : The cost function for elementary costs
        :class:`.RiesenCostFunction` : Another improved cost function

        Notes
        -----
        In the same way `RiesenCostFunction` does, this cost function improves the matching by
        taking adjacent edges and neighbors edit costs into account to compute the node edit costs.

        The assignment costs for edges is based on the given `CostFunction`.
        Hence, it is important for this given cost function to be able to
        compare edges (ie, by providing an edges comparison function).
        """
        import numpy as np
        import scipy as sp

        self.np = np
        self.cf_ = cf
        self.lsap_solver_ = (
            lsap_solver
            if lsap_solver is not None
            else sp.optimize.linear_sum_assignment
        )

    def cns(self, node_u: Any, node_v: Any, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between
        `node_u` from `g1` and `node_v` from `g2`.

        The result is based on the comparison of adjacent edges and neighbors of `node_u` with
        `node_v`'s ones. This comparison aims to match the adjacent edges and the neighbors
        by using the constant edit costs from the given `CostFunction`.

        Parameters
        ----------
        node_u : Any
            Source node in `g1`
        node_v : Any
            Target node in `g2`
        g1 : networkx.Graph
            Graph containing `node_u`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        n = len(g1[node_u])
        m = len(g2[node_v])
        sub_C = self.np.ones([n + m, n + m]) * sys.maxsize
        sub_C[n:, m:] = 0
        i = 0
        l_nbr_u = g1[node_u]
        l_nbr_v = g2[node_v]
        for nbr_u in l_nbr_u:
            j = 0
            e1 = (node_u, nbr_u)
            for nbr_v in g2[node_v]:
                e2 = (node_v, nbr_v)
                sub_C[i, j] = self.cf_.ces(e1, e2, g1, g2)
                sub_C[i, j] += self.cf_.cns(nbr_u, nbr_v, g1, g2)
                j += 1
            i += 1

        i = 0
        for nbr_u in l_nbr_u:
            sub_C[i, m + i] = self.cf_.ced((node_u, nbr_u), g1)
            sub_C[i, m + i] += self.cf_.cnd(nbr_u, g1)
            i += 1

        j = 0
        for nbr_v in l_nbr_v:
            sub_C[n + j, j] = self.cf_.cei((node_v, nbr_v), g2)
            sub_C[n + j, j] += self.cf_.cni(nbr_v, g2)
            j += 1

        row_ind, col_ind = self.lsap_solver_(sub_C)
        cost = self.np.sum(sub_C[row_ind, col_ind])
        return self.cf_.cns(node_u, node_v, g1, g2) + cost.item()

    def cnd(self, node_u: Any, g1: nx.Graph) -> int:
        """Computes the deletion cost of `node_u` in `g1`.

        In the same way as `RiesenCostFunction`, the result is based on
        the existing adjacent edges deletion costs, as a node deletion
        causes its adjaccent edges to be deleted too.
        This deletion cost is provided by the given `CostFunction`.

        Parameters
        ----------
        node_u : Any
            Node to delete from `g1`
        g1 : networkx.Graph
            Graph containing `node_u`

        Returns
        -------
        A positive int value
        """
        cost = 0
        for nbr in g1[node_u]:
            cost += self.cf_.ced((node_u, nbr), g1)
        return self.cf_.cnd(node_u, g1) + cost

    def cni(self, node_v: Any, g2: nx.Graph) -> int:
        """Computes the insertion cost of `node_v` in `g2`.

        In the same way as `RiesenCostFunction`, the result is based on
        the existing adjacent edges insertion costs, as a node insertion
        causes its adhacent edges to be inserted too.
        This insertion cost is provided by the given `CostFunction`.

        Parameters
        ----------
        node_v : Any
            Node to insert into `g2`
        g2 : networkx.Graph
            Graph containing `node_v`

        Returns
        -------
        A positive int value
        """
        cost = 0
        for nbr in g2[node_v]:
            cost += self.cf_.cei((node_v, nbr, g2), g2)
        return self.cf_.cni(node_v, g2) + cost

    def ces(self, e1: tuple, e2: tuple, g1: nx.Graph, g2: nx.Graph) -> int:
        """Computes the substitution cost between edge
        `e1` from `g1` and edge `e2` from `g2`.

        This substitution cost is provided by the given `CostFunction`.

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Source edge in `g1`
        e2 : tuple[Any, Any]
            Target edge in `g2`
        g1 : networkx.Graph
            Graph containing `e1`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        return self.cf_.ces(e1, e2, g1, g2)

    def ced(self, e1: tuple, g1: nx.Graph) -> int:
        """Computes the deletion cost of edge `e1` in `g1`.

        This deletion cost is provided by the given `CostFunction`

        Parameters
        ----------
        e1 : tuple[Any, Any]
            Edge to delete from `g1`
        g1 : networkx.Graph
            Graph containing `e1`

        Returns
        -------
        A positive int value
        """
        return self.cf_.ced(e1, g1)

    def cei(self, e2: tuple, g2: nx.Graph) -> int:
        """Computes the insertion cost of edge `e2` in `g2`.

        This insertion cost is provided by the given `CostFunction`

        Parameters
        ----------
        e2 : tuple[Any, Any]
            Edge to insert into `g2`
        g2 : networkx.Graph
            Graph containing `e2`

        Returns
        -------
        A positive int value
        """
        return self.cf_.cei(e2, g2)

    @property
    def ccf(self) -> CostFunction:
        """Accesses the associated elementary cost function

        Returns
        -------
        The basic cost function
        """
        return self.cf_
