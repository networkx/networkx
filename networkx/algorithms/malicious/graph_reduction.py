"""
Building a reduced graph from a dependency graph.
"""

__all__ = ["build_GR_from_DG"]
import networkx as nx


def build_RG_from_DG(dependency_graph):
    """
    Building a reduced graph (RG) from a dependency graph (DG)

    Parameters
    ----------
    dependency_graph : NetworkX DiGraph
        A dependency graph 

    Returns
    -------
    reduced_graph : NetworkX DiGraph
        A reduced graph    

    Notes
    -----
    The size of a dependency graph may be reduced. Some
    part of the code where the control flow never reaches can
    be removed. In addition, vertices that satisfy one of the
    following four conditions can be eliminated:
        • A vertex with only one outgoing edge without any incoming
          edge. It is mostly the declaration of a variable,
          which is not critical when only considering the core
          part of the program.
        • A vertex with only one incoming edge without any
          outgoing edge. It means that the first vertex uses the
          value of the latter one.
        • A vertex with only one incoming and one outgoing
          edge. It plays a role in conveying a value or data from
          one vertex to another mainly.

    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example 1: building a RG graph
    ------------------------------
    # creates and builds the DG graph
    >>> directed_G1 = nx.DiGraph()
    >>> directed_G1.add_nodes_from(range(1,12))
    >>> directed_G1.add_edges_from([(1, 4),(2, 5),(3, 6),(4, 7),(5, 8),(6, 7),(6, 8),(6, 9),(8, 8),(9, 7),(9, 8),(9,9)])

    # creates and builds the RG graph by removing irrelevant edges and nodes from the DG graph 
    >>> reduction_G1 = directed_G1
    >>> reduction_G1.remove_edges_from([(1,4),(2,5),(3,6),(4, 7),(5, 8)])
    >>> reduction_G1.remove_nodes_from([1,2,3,4,5,10,11])

    # runs the function
    >>> build_RG_from_DG(directed_G1)
    reduction_G1
    
    Example 2: a graph that can not be reduced (the original graph will be return)
    ------------------------------------------------------------------------------
    # creates and builds the DG graph
    >>> directed_G2 = nx.DiGraph()
    >>> directed_G2.add_nodes_from(range(1,7))
    >>> directed_G2.add_edges_from([(1,2),(2,3)])

    # runs the function
    >>> build_RG_from_DG(directed_G2)
    directed_G2
    """
    return 0  # Empty implementation
