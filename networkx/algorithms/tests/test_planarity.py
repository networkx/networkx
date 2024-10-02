import pytest
import networkx as nx
from networkx.algorithms.planarity import (
    check_planarity_recursive,
    get_counterexample,
    get_counterexample_recursive,
)

# Your existing class and function definitions...



class PlanarEmbedding(nx.PlanarEmbedding):
    def to_undirected(self, reciprocal=True):
        """Returns the undirected version of the embedding without 'cw' and 'ccw' attributes.

        Parameters
        ----------
        reciprocal : bool (optional, default=True)
            If True, only keep an edge in the undirected graph if both directed
            edges exist. If False, keep the edge if either directed edge exists.

        Returns
        -------
        G : Graph
            An undirected graph with the same nodes and edges as the directed
            graph, but without 'cw' and 'ccw' attributes.
        """
        # Call the original to_undirected method to get the basic undirected graph
        undirected_graph = super().to_undirected(reciprocal=reciprocal)

        # Remove 'cw' and 'ccw' attributes from all edges
        for u, v, attr in undirected_graph.edges(data=True):
            # Remove 'cw' and 'ccw' attributes if present
           if "cw" in attr:
+                del attr["cw"]
+          if "ccw" in attr:
+                del attr["ccw"]

        return undirected_graph


class TestLRPlanarity:
    """Nose Unit tests for the :mod:`networkx.algorithms.planarity` module.

    Tests three things:
    1. Check that the result is correct
        (returns planar if and only if the graph is actually planar)
    2. In case a counter example is returned: Check if it is correct
    3. In case an embedding is returned: Check if its actually an embedding
    """

    @staticmethod
    def check_graph(G, is_planar=None):
        """Raises an exception if the lr_planarity check returns a wrong result

        Parameters
        ----------
        G : NetworkX graph
        is_planar : bool
            The expected result of the planarity check.
            If set to None only counter example or embedding are verified.

        """
        # obtain results of planarity check
        is_planar_lr, result = nx.check_planarity(G, True)
        is_planar_lr_rec, result_rec = check_planarity_recursive(G, True)

        if is_planar is not None:
            # set a message for the assert
            if is_planar:
                msg = "Wrong planarity check result. Should be planar."
            else:
                msg = "Wrong planarity check result. Should be non-planar."

            # check if the result is as expected
            assert is_planar == is_planar_lr, msg
            assert is_planar == is_planar_lr_rec, msg

        if is_planar_lr:
            # check embedding
            check_embedding(G, result)
            check_embedding(G, result_rec)
        else:
            # check counter example
            check_counterexample(G, result)
            check_counterexample(G, result_rec)


def check_embedding(G, embedding):
    """Raises an exception if the combinatorial embedding is not correct

    Parameters
    ----------
    G : NetworkX graph
    embedding : a dict mapping nodes to a list of edges
        This specifies the ordering of the outgoing edges from a node for
        a combinatorial embedding

    Notes
    -----
    Checks the following things:
        - The type of the embedding is correct
        - The nodes and edges match the original graph
        - Every half edge has its matching opposite half edge
        - No intersections of edges (checked by Euler's formula)
    """

    if not isinstance(embedding, nx.PlanarEmbedding):
        raise nx.NetworkXException("Bad embedding. Not of type nx.PlanarEmbedding")

    # Check structure
    embedding.check_structure()

    # Check that graphs are equivalent
    assert set(G.nodes) == set(
        embedding.nodes
    ), "Bad embedding. Nodes don't match the original graph."

    # Check that the edges are equal
    g_edges = set()
    for edge in G.edges:
        if edge[0] != edge[1]:
            g_edges.add((edge[0], edge[1]))
            g_edges.add((edge[1], edge[0]))
    assert g_edges == set(
        embedding.edges
    ), "Bad embedding. Edges don't match the original graph."


# Example usage
G = nx.Graph(((0, 1), (1, 2), (2, 3), (3, 0), (0, 2)))
is_planar, P = nx.check_planarity(G)
print(is_planar)  # Should print: True

# Check edge attributes before conversion to undirected graph
print(P[0][2], P[2][0])  # Should show 'cw' and 'ccw' attributes

# Convert to undirected
U = P.to_undirected()
print(U[0][2])  # Should not contain 'cw' or 'ccw' attributes
