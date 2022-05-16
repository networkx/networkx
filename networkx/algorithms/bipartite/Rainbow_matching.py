import networkx as nx
import copy


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
    >>> rainbow_matching(G , 1 )
    1
    >>> rainbow_matching(G , 2)
    0
    """
    return Disjoint_Set_Rainbow_Matching(graph, [], k, nx.Graph())


def Disjoint_Set_Rainbow_Matching(P : nx.Graph, S : list, k : int, B : nx.Graph):
    """
    This function is a generalization of the Rainbow Matching problem.
    Given a path P, a collection S of vertex disjoint paths and an integer k,
    Is there a colorful matching of size k that uses exactly one edge from each path in S,
    and k - |S| edges from P?

    >>> G = nx.Graph()
    >>> G.add_nodes_from([1, 3])
    >>> G.add_edge(1, 2, color = "blue")
    >>> G.add_edge(2, 3, color="red")
    >>> Disjoint_Set_Rainbow_Matching(G , [] , 1 , nx.Graph())
    1
    >>> Disjoint_Set_Rainbow_Matching(G , [] , 2 , nx.Graph())
    0
    """

    # First step is to check if Lemma 5 or Lemma 6 are applicable.
    # If they return an answer that is not "-1",
    # we return the answer.
    if Lemma5(P,S,k,B) == 1:
        return 1
    if Lemma5(P,S,k,B) == 0 or Lemma6(P,S,k,B) == 0:
        return 0

    # If both Lemma 5 and Lemma 6 are not applicable,
    # Lemma 8 guarantees us an index i for which the sub-path of P, (1, ..., i),
    # has exactly one edge in the Rainbow Match.
    i = Lemma8(P,S,k,B)
    P_1 = copy.deepcopy(P)
    S_1 = copy.deepcopy(S)

    # Add the sub-path (1, ..., i-1) and the sub-path (i, i+1)
    # to the set S_1
    nodes = list(range(0, i))
    list_nodes = list(P_1.subgraph(nodes))
    path = ' '.join(map(str, list_nodes))
    S_1.append(path)
    path = ' '.join(map(str, [i, i + 1]))
    S_1.append(path)

    # Update the auxiliary bipartite graph
    B_temp = copy.deepcopy(B)
    add_path_to_B(P_1.subgraph(nodes), B_temp)
    add_path_to_B(P_1.subgraph([i,i+1]), B_temp)

    # Update the path P_1 to start from vertex i+2
    P_1.remove_nodes_from(list(range(0, i + 2)))

    # First branch - if the edge (i,i+1) belongs to the rainbow matching
    ans = Disjoint_Set_Rainbow_Matching(P_1, S_1, k, B_temp)
    if ans == 1:
        return 1



    P_2 = copy.deepcopy(P)
    S_2 = copy.deepcopy(S)

    # Add the sub-path (1, ..., i) to the set S_2
    nodes = list(range(0, i+1))
    list_nodes = list(P_2.subgraph(nodes))
    path = ' '.join(map(str, list_nodes))
    S_2.append(path)

    # Update the auxiliary bipartite graph
    B_temp = copy.deepcopy(B)
    add_path_to_B(P_1.subgraph(nodes), B_temp)

    # Update the path P_2 to start from vertex i+1
    P_2.remove_nodes_from(list(range(0, i + 1)))

    # Second branch - if the edge (i,i+1) does not belongs to the rainbow matching
    ans = Disjoint_Set_Rainbow_Matching(P_2, S_2, k, B_temp)
    if ans == 1:
        return 1

    return 0





def add_path_to_B(P : nx.Graph, B : nx.Graph):
    """
    This function adds a path P to the auxiliary bipartite graph B.
    The left side contains the colors of the edges as nodes.
    The right side contains paths.
    There will be an edge between a path P and a color c
     if there is an edge in P that is colored in c.

     >>> P = nx.Graph()
     >>> P.add_edge(1, 2, color="red")
     >>> B = nx.Graph()
     >>> B.add_node("red")
     >>> B.add_node('3 4')
     >>> B.add_edge("red", '3 4')
     >>> add_path_to_B(P,B)
     >>> list(B.nodes)
     ['red', '3 4', '1 2']
     >>> list(B.edges)
     [('red', '3 4'), ('red', '1 2')]

    """


    if len(P) == 1:
        return

    path =' '.join(map(str, list(P.nodes()) ))
    B.add_node(path, bipartite=1)
    for i in P.nodes():
        if P.has_edge(i, i+1):
            color = P.edges[i, i + 1]['color']
            B.add_edge(color, path)


def size_max_matching(B : nx.Graph) -> int:
    """
    This function returns the size of the maximum matching in a given bipartite graph.
    Since the bipartite graph we use can be disconnected, we go through all of the components.
    >>> B = nx.Graph()
    >>> B.add_node("red")
    >>> B.add_node('1 2')
    >>> B.add_edge("red", '1 2')
    >>> size_max_matching(B)
    1.0
    """
    sum_matching = 0
    for path in nx.connected_components(B):
        component = B.subgraph(path)
        sum_matching += len(nx.bipartite.maximum_matching(component))/2

    return sum_matching


# The following functions are Lemmas from the article that are very helpful for us.
def Lemma5(P : nx.Graph, S : list, k : int, B : nx.Graph):
    # This lemma focuses only on <=1
    if k - len(S) > 1:
        return -1

    # Less than 0, return 0
    elif k - len(S) < 0:
        return 0

    # Exactly zero, return 1 if there is a matching in B that saturates S
    # If there isn't, return 0
    elif k - len(S) == 0:
        #check if there is a matching that covers all S in B
        if size_max_matching(B) == len(S):
            return 1
        else:
            return 0

    # Exactly one, go through every edge and do the same as the 0 case
    elif k - len(S) == 1:
        if len(P) <= 1:
            return 0
        for i in P.nodes():
            if i > 1:
                B_temp = copy.deepcopy(B)
                add_path_to_B(P.subgraph([i,i+1]), B_temp)
                #check if there is a matching that covers all S in B
                if size_max_matching(B_temp) == len(S):
                    return 1



def Lemma6(P : nx.Graph, S : list, k : int, B : nx.Graph):
    for i in P.nodes():
        if i > 1:
            B_temp = copy.deepcopy(B)
            nodes = list(range(0,i))
            add_path_to_B(P.subgraph(nodes), B_temp)
            add_path_to_B(P.subgraph([i,i+1]), B_temp)

            max_match = size_max_matching(B_temp)
            if max_match > len(S)+1:
                return -1

    # if we checked all indexes and didn't find an index that satisfies the lemma's condition
    # there is no rainbow matching and we return 0
    return 0

def Lemma8(P : nx.Graph, S : list, k : int, B : nx.Graph):
    # This lemma is called if lemma 6 returns "-1".
    # It finds the smallest index for which the lemma's condition is met.
    for i in P.nodes():
        if i > 1:
            B_temp = copy.deepcopy(B)

            nodes = list(range(0, i))
            add_path_to_B(P.subgraph(nodes), B_temp)
            add_path_to_B(P.subgraph([i, i + 1]), B_temp)

            max_match = size_max_matching(B_temp)
            if max_match == len(S) + 2:
                return i
    return -1



if __name__ == '__main__':
    import doctest
    doctest.testmod()


    G = nx.Graph()
    G.add_edge(1, 2, color="red")
    G.add_edge(2, 3, color="blue")
    G.add_edge(3, 4, color="red")
    G.add_edge(4, 5, color="yellow")
    G.add_edge(5, 6, color="green")
    G.add_edge(6, 7, color="yellow")
    G.add_edge(7, 8, color="black")
    G.add_edge(8, 9, color="red")
    G.add_edge(9, 10, color="green")
    G.add_edge(10, 11, color="white")
    G.add_edge(11, 12, color="white")
    G.add_edge(12, 13, color="yellow")
    G.add_edge(13, 14, color="black")

    print(rainbow_matching(G, 5))
    print(rainbow_matching(G, 6))
