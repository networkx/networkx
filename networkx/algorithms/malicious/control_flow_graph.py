"""
Building a control flow graph from a code with semantic meaning.
"""

__all__ = ["build_CFG"]

def build_CFG(semantic_program):
    """
    Building a control flow graph (CFG) from the given program's code with semantic meaning.
    The function returns the CFG.

    Parameters
    ----------
    program : string
        A path to the file that contains the semantic code

    Returns
    -------
    control_flow_graph : NetworkX DiGraph
        A (dirceted) graph that represents the flow of the code.    

    Raises
    ------
    NetworkXPathDoesNotExist
        If the given path does not exist.

    Notes
    -----
    A control-flow graph (CFG) is a representation, using graph notation,
    of all paths that might be traversed through a program during its execution.

    https://en.wikipedia.org/wiki/Control-flow_graph

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example 1: valid path
    ---------------------
    >>> import networkx as nx

    # creates a semantic code 
    >>> path = '/Users/liozakirav/Documents/computer-science/fourth-year/Research-Algorithms/networkx/networkx/algorithms/malicious/code-examples/'
    >>> file_name = 'semantic1.txt'
    >>> path = '/Users/lioz'file1 = path + file_name
    >>> path = '/Users/lioz'file2 = path +with open(file1, 'w') as f:
    >>>    f.write('1: dim n\n\
    >>> 2: dim p\n\
    >>> 3: dim i\n\
    >>> 4: n=5\n\
    >>> 5: p=1\n\
    >>> 6: i=1\n\
    >>> 7: if i ≤ n then\n\
    >>> 8: p=p * i\n\
    >>> 9: i=i + 1\n\
    >>> 10: goto 7:\n\
    >>> 11: end if')

    # creates and builds the control flow graph  
    >>> control_flow_graph = nx.DiGraph()
    >>> nodes = range(1, 12)
    >>> control_flow_graph.add_nodes_from(nodes)
    >>> edges = [(edge, edge+1) for edge in range(1, 11)]
    >>> edges.append((7,11))
    >>> edges.append((10, 7))
    >>> control_flow_graph.add_edges_from(edges)

    # runs the function
    >>> build_CFG(file1)
    DiGraph with 11 nodes and 12 edges

    Example 2: invalid path
    -----------------------
    >>> file_name2 = 'semantic-code2.txt'
    >>> file2 = path + file_name # file does not exist

    >>> build_CFG(file2)
    Exception: NetworkXPathDoesNotExist
    """
    return 0  # Empty implementation



