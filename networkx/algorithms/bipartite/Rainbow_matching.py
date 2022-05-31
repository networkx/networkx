import networkx as nx
import copy


def rainbow_matching(graph : nx.Graph, k : int) -> int:
    """
    "Parameterized Algorithms and Kernels for Rainbow Matching" by
    S. Gupta and S. Roy and S. Saurabh and M. Zehavi, https://drops.dagstuhl.de/opus/volltexte/2017/8124/pdf/LIPIcs-MFCS-2017-71.pdf

    Algorithm 1: Receives a colored path with numbered vertices and an integer "k".
    Returns a rainbow matching of size k
    and returns an empty graph if there isn't.
    >>> Res = rainbow_matching(nx.Graph() , 1 )
    >>> list(Res.edges)
    []


    >>> G = nx.Graph()
    >>> G.add_nodes_from([1, 3])
    >>> G.add_edge(1, 2, color = "blue")
    >>> G.add_edge(2, 3, color="red")
    >>> Res = rainbow_matching(G , 1 )
    >>> list(Res.edges)
    [(1, 2)]
    >>> Res = rainbow_matching(G , 2)
    >>> list(Res.edges)
    []

    >>> G.add_node(4)
    >>> G.add_edge(3, 4, color = "green")
    >>> Res = rainbow_matching(G , 2)
    >>> list(Res.edges)
    [(1, 2), (3, 4)]
    >>> G.edges[3, 4]['color'] = "blue"
    >>> Res = rainbow_matching(G , 2)
    >>> list(Res.edges)
    []
    >>> G.edges[3, 4]['color'] = "red"
    >>> Res = rainbow_matching(G , 2)
    >>> list(Res.edges)
    [(1, 2), (3, 4)]
    """
    global original_path
    original_path = copy.deepcopy(graph)
    return Disjoint_Set_Rainbow_Matching(graph, [], k, nx.Graph())


def Disjoint_Set_Rainbow_Matching(P : nx.Graph, S : list, k : int, B : nx.Graph):
    """
    This function is a generalization of the Rainbow Matching problem.
    Given a path P, a collection S of vertex disjoint paths and an integer k,
    Is there a colorful matching of size k that uses exactly one edge from each path in S,
    and k - |S| edges from P?
    This function makes use of an auxiliary bi-partite graph B.
    The left side contains the colors of the edges as nodes and the right side contains disjoint paths.
    There will be an edge between a path P and a color c if there is an edge in P that is colored in c.

    """

    # First step is to check if Lemma 5 or Lemma 6 are applicable.
    # If they return an answer that is not "-1", we return the answer.
    result5 = Lemma5(P,S,k,B)
    result6 = Lemma6(P,S,k,B)
    if isinstance(result5, nx.Graph):
        return result5
    if result5 == False or result6 == False:
        return nx.Graph()

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
    if ans != False:
        return ans




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
    if ans != False:
        return ans

    return nx.Graph()





def add_path_to_B(P : nx.Graph, B : nx.Graph):
    """
    This function adds a path P to the auxiliary bipartite graph B.

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


    if len(P) <= 1:
        return

    path =' '.join(map(str, sorted(list(P.nodes())) ))
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

def get_rainbow_matching(B : nx.Graph):
    '''
    This function recieves a bipartite graph and returns a Graph with the corresponding rainbow matching.
    '''
    matching = nx.Graph()
    for path in nx.connected_components(B):
        component = B.subgraph(path)
        nodes = nx.bipartite.maximum_matching(component)
        for key in list(nodes.keys()):
            lst = key.split(" ")
            if lst[0].isnumeric():
                for i in lst[1:]:
                    int_i = int(i)
                    if original_path.has_edge(int_i-1, int_i) and nodes.get(key) == original_path.edges[int_i-1, int_i]['color']:
                        matching.add_nodes_from([int_i -1 , int_i])
                        matching.add_edge(int_i-1, int_i, color = nodes.get(key))
    return matching

# The following functions are Lemmas from the article that are very helpful for us.
def Lemma5(P : nx.Graph, S : list, k : int, B : nx.Graph):
    # This lemma focuses only on <=1
    if k - len(S) > 1:
        return -1

    # Less than 0, return 0
    elif k - len(S) < 0:
        return False

    # Exactly zero, return 1 if there is a matching in B that saturates S
    # If there isn't, return False (there is no rainbow matching)
    elif k - len(S) == 0:
        #check if there is a matching that covers all S in B
        if size_max_matching(B) == len(S):
            return get_rainbow_matching(B)
        else:
            return False

    # Exactly one, go through every edge and do the same as the 0 case
    elif k - len(S) == 1:
        if len(P) <= 1:
            return 0
        for i in P.nodes():
            #if i > 1:
                B_temp = copy.deepcopy(B)
                add_path_to_B(P.subgraph([i,i+1]), B_temp)
                #check if there is a matching that covers all S in B
                if size_max_matching(B_temp) == len(S)+1:
                    return get_rainbow_matching(B_temp)
        return False



def Lemma6(P : nx.Graph, S : list, k : int, B : nx.Graph):
    for i in P.nodes():
        #if i > 1:
            B_temp = copy.deepcopy(B)
            nodes = list(range(0,i))
            add_path_to_B(P.subgraph(nodes), B_temp)
            add_path_to_B(P.subgraph([i,i+1]), B_temp)

            max_match = size_max_matching(B_temp)
            if max_match > len(S)+1:
                return -1

    # if we checked all indexes and didn't find an index that satisfies the lemma's condition
    # there is no rainbow matching and we return 0
    return False

def Lemma8(P : nx.Graph, S : list, k : int, B : nx.Graph):
    # This lemma is called if lemma 6 returns "-1".
    # It finds the smallest index for which the lemma's condition is met.
    for i in P.nodes():
        #if i > 1:
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
    print(doctest.testmod())


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

    print(list(rainbow_matching(G, 5).edges))
    print(list(rainbow_matching(G, 6).edges))

    G = nx.Graph()
    G.add_nodes_from([1, 3])
    G.add_edge(1, 2, color="blue")
    G.add_edge(2, 3, color="red")
    Res = rainbow_matching(G, 1)
    print(list(Res.edges))


