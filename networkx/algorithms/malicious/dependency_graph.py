"""
Building a dependency graph from a control flow graph.
"""

__all__ = ["build_DG_from_CFG"]
import networkx as nx


def build_DG_from_CFG(semantic_program):
    """Converting a control flow graph (CFG) to a dependency graph (DG).

    Parameters
    ----------
    control_flow_graph : NetworkX DiGraph
        A CFG graph

    Returns
    -------
    dependency_graph : NetworkX DiGraph
        A dependency graph    

    Notes
    -----
    A dependency graph (DG) is a data structure formed by a directed graph that 
    describes the dependency of an entity in the system on the other entities of the same system.

    https://deepsource.io/glossary/dependency-graph/

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example 1: building a DG graph
    ------------------------------
    # creates and builds the DG graph
    >>> directed_G1 = nx.DiGraph()
    >>> directed_G1.add_nodes_from(range(1,12))
    >>> directed_G1.add_edges_from([(1, 4),(2, 5),(3, 6),(4, 7),(5, 8),(6, 7),(6, 8),(6, 9),(8, 8),(9, 7),(9, 8),(9,9)])

    # runs the function
    >>> build_control_graph(file1)
    directed_G1
    """
    return 0  # Empty implementation
