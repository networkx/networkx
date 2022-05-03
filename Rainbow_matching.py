import networkx as nx

def rainbow_matching(graph : nx.Graph, k : int) -> nx.Graph:
    """
    "Parameterized Algorithms and Kernels for Rainbow Matching" by
    S. Gupta and S. Roy and S. Saurabh and M. Zehavi, https://drops.dagstuhl.de/opus/volltexte/2017/8124/pdf/LIPIcs-MFCS-2017-71.pdf

    Algorithm 1: Receives a colored path and an integer "k".
    Returns a rainbow matching of size k if such exists,
    and returns an empty graph if there isn't.
    
    >>> Res = rainbow_matching(nx.Graph() , 1 )
    >>> list(Res.edges)
    []


    >>> G = nx.Graph()
    >>> G.add_nodes_from([1, 3])
    >>> G.add_edge(1, 2, color = "blue")
    >>> G.add_edge(2, 3, color="red")
    >>> Res = rainbow_matching(nx.Graph() , 1 )
    >>> list(Res.edges)
    [(0, 1)]
    >>> Res = rainbow_matching(nx.Graph() , 2)
    >>> list(Res.edges)
    []
    """


    return nx.Graph();

if __name__ == '__main__':
    import doctest
    doctest.testmod()

