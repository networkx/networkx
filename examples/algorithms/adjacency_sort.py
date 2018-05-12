"""
Sorting the adjacency lists of a graph.
Complexity: O(m+n)

Input: The unsorted adjacency lists of a graph G = (V, E)
and a order of vertices
Output: The sorted adjacency lists

The Algorithm is represented by Martin Charles Golumbic in 2004.
Golumbic, Martin Charles. Algorithmic graph theory and perfect graphs.
Vol. 57. Elsevier, 2004. (Page 36)

@book{golumbic2004algorithmic,
  title={Algorithmic graph theory and perfect graphs},
  author={Golumbic, Martin Charles},
  volume={57},
  year={2004},
  publisher={Elsevier}
}
"""
import networkx as nx
def sort_adjacencylists(G, order):
    """
    Input: `G` is a networkx graph
    `order` is a sorted vertices list
    Ouput: adjacency lists with all sorted lists
    """
    adjacency = {}
    for node in order:
        adjacency[node] = []
    for node in order:
        for adjnode in G.neighbors(node):
            adjacency[adjnode].append(node)
    return adjacency
G = nx.karate_club_graph()
order = [1,2,3,0,4,5,6,7,8,9,10,20,21,22,23,24,25,11,12,13,14,15,16,
17,18,26,27,28,30,29,31,32,33,19]
adjlist = sort_adjacencylists(G, order)
