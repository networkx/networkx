import networkx as nx

def rainbow_matching(graph : nx.Graph, k : int) -> int:
    """
    "Parameterized Algorithms and Kernels for Rainbow Matching" by
    S. Gupta and S. Roy and S. Saurabh and M. Zehavi, https://drops.dagstuhl.de/opus/volltexte/2017/8124/pdf/LIPIcs-MFCS-2017-71.pdf

    Algorithm 1: Receives a colored path and an integer "k".
    Returns "true" (1) if there is a rainbow matching of size "k",
    and returns "false" (0) if there isn't.
    >>> rainbow_matching(nx.Graph() , 1 )
    0

    >>> G = nx.Graph()
    >>> G.add_nodes_from([1, 3])
    >>> G.add_edge(1, 2, color = "blue")
    >>> G.add_edge(2, 3, color="red")
    >>> rainbow_matching(nx.Graph() , 1 )
    1
    >>> rainbow_matching(nx.Graph() , 2)
    0
    """


    return -1;

if __name__ == '__main__':
    import doctest
    doctest.testmod()
