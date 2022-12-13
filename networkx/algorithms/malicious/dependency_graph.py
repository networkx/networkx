"""
Building a dependency graph from a control flow graph.
"""

__all__ = ["build_DG_from_CFG"]

def build_DG_from_CFG(control_flow_graph):
    """
    Building a dependency graph (DG) from a control flow graph (CFG).
    The function returns the DG.

    Parameters
    ----------
    control_flow_graph : NetworkX DiGraph
        A CFG (dirceted) graph

    Returns
    -------
    dependency_graph : NetworkX DiGraph
        A dependency (dirceted) graph    

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

    Example: building a DG graph
    ------------------------------
    >>> import networkx as nx

   # creates and builds the control flow graph  
    >>> control_flow_graph = nx.DiGraph()
    >>> nodes = range(1, 12)
    >>> control_flow_graph.add_nodes_from(nodes)
    >>> edges = [(edge, edge+1) for edge in range(1, 11)]
    >>> edges.append((7,11))
    >>> edges.append((10, 7))
    >>> control_flow_graph.add_edges_from(edges)

    # creates and builds the DG graph
    >>> directed_G1 = nx.DiGraph()
    >>> directed_G1.add_nodes_from(range(1,12))
    >>> directed_G1.add_edges_from([(1, 4),(2, 5),(3, 6),(4, 7),(5, 8),(6, 7),(6, 8),(6, 9),(8, 8),(9, 7),(9, 8),(9,9)])

    # runs the function
    >>> build_DG_from_CFG(control_flow_graph)
    DiGraph with 11 nodes and 12 edges
    """
    return 0  # Empty implementation
