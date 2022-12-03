"""
Converting a code with semantic meaning to a control flow graph.
"""

__all__ = ["build_control_graph"]


def build_control_graph(semantic_program):
    """Converting a given program's code with semantic meaning to a control flow graph.

    Parameters
    ----------
    program : string
        A path to the file that contains the semantic code

    Returns
    -------
    control_flow_graph : NetworkX Graph
        A graph that represents the flow of the code.    

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
    path = '/Users/liozakirav/Documents/computer-science/fourth-year/Research-Algorithms/networkx/networkx/algorithms/malicious/code-examples/'
    file_name = 'semantic1.txt'
    file1 = path + file_name
    with open(file1, 'w') as f:
        f.write('1: dim n\n\
    2: dim p\n\
    3: dim i\n\
    4: n=5\n\
    5: p=1\n\
    6: i=1\n\
    7: if i ≤ n then\n\
    8: p=p * i\n\
    9: i=i + 1\n\
    10: goto 7:\n\
    11: end if')

    >>> build_control_graph(file1)

    

    Example 2: invalid path
    -----------------------
    file_name2 = 'semantic-code2.txt'
    file2 = path + file_name # file does not exist

    >>> convert_to_semantic(file2)
    Exception: NetworkXPathDoesNotExist
    """
    return 0  # Empty implementation



