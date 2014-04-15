import networkx as nx

class Node:
    def __init__(self, nodeId, n):
        self.nodeId = nodeId
        self.color = -1
        self.adjList = None
        self.adjColor = [None for i in range(n)]

    def __repr__(self):
        return "NodeId: {0}, Degree: {1}, Color: {2}, AdjList: ({3}), adjColor: ({4})".format(self.nodeId, self.degree, self.color, self.adjList, self.adjColor)

    def assign_color(self, adjEntry, color):
        adjEntry.colPrev = None
        adjEntry.colNext = self.adjColor[color]
        self.adjColor[color] = adjEntry
        if adjEntry.colNext != None:
            adjEntry.colNext.colPrev = adjEntry

    def clear_color(self, adjEntry, color):
        if adjEntry.colPrev == None:
            self.adjColor[color] = adjEntry.colNext
        else:
            adjEntry.colPrev.colNext = adjEntry.colNext
        if adjEntry.colNext != None:
            adjEntry.colNext.colPrev = adjEntry.colPrev

class AdjEntry:
    def __init__(self, nodeId):
        self.nodeId = nodeId
        self.next = None
        self.mate = None
        self.colNext = None
        self.colPrev = None

    def __repr__(self):
        return "NodeId: {0}, Next: ({1}), Mate: ({2}), colNext: ({3}), colPrev: ({4})".format(self.nodeId, self.next, self.mate.nodeId, None if self.colNext == None else self.colNext.nodeId, None if self.colPrev == None else self.colPrev.nodeId)

class LLNode:
    def __init__(self, nodeId):
        self.nodeId = nodeId
        self.next = None

    def __repr__(self):
        return "NodeId: {0}, Next: ({1})".format(self.nodeId, self.next)

                            
"""
    This procedure is an adaption of the algorithm described by [1], and is an implementation of 
    coloring with interchange. Please be advised, that the datastructures used are rather complex
    because they are optimized to minimize the time spent identifying sub-components of the graph,
    which are possible candidates for color interchange.

References
----------
... [1] Maciej M. Syslo, Marsingh Deo, Janusz S. Kowalik,
    Discrete Optimization Algorithms with Pascal Programs, 415-424, 1983
    ISBN 0-486-45353-7
"""
def coloring_with_interchange(original_graph, nodes, returntype):
    n = len(original_graph)
    graph = {}
    for nodeId in original_graph.nodes_iter():
        graph[nodeId] = Node(nodeId, n)
    for (node1, node2) in original_graph.edges_iter():
        adjEntry1 = AdjEntry(node2)
        adjEntry2 = AdjEntry(node1)
        adjEntry1.mate = adjEntry2
        adjEntry2.mate = adjEntry1
        node1Head = graph[node1].adjList
        adjEntry1.next = node1Head
        graph[node1].adjList = adjEntry1
        node2Head = graph[node2].adjList
        adjEntry2.next = node2Head
        graph[node2].adjList = adjEntry2
    
    k = 0
    for node in nodes:
        # Find the color with the lowest possible value
        k1 = 0
        colUsed = [0 for i in range(k+2)]
        adjNode = graph[node].adjList
        while adjNode != None:
            col = graph[adjNode.nodeId].color
            if col != -1:
                colUsed[col] = 1
            adjNode = adjNode.next
        while colUsed[k1] != 0:
            k1 += 1
        
        # k1 is now the lowest available color
        if k1 > k:
            connected = True
            col1 = -1
            col2 = -1
            while connected and col1 < k:
                col1 += 1
                col1Head = None
                col1Tail = None
                col1Adj = graph[node].adjColor[col1]
                while col1Adj != None:
                    newNode = LLNode(col1Adj.nodeId)
                    if col1Head == None:
                        col1Tail = newNode
                    newNode.next = col1Head
                    col1Head = newNode
                    col1Adj = col1Adj.colNext
                
                col2 = col1
                while connected and col2 < k:
                    col2 += 1
                    visited = set()
                    col1Tail.next = None
                    searchTail = col1Tail
                    col1Adj = col1Head
                    while col1Adj != None:
                        visited.add(col1Adj.nodeId)
                        col1Adj = col1Adj.next
                    
                    searchNode = col1Head
                    while searchNode != None:
                        colOpp = col2 if graph[searchNode.nodeId].color == col1 else col1
                        neighbour = graph[searchNode.nodeId].adjColor[colOpp]
                        while neighbour != None:
                            if not neighbour.nodeId in visited:
                                visited.add(neighbour.nodeId)
                                newNode = LLNode(neighbour.nodeId)
                                searchTail.next = newNode
                                searchTail = newNode
                            neighbour = neighbour.colNext
                        searchNode = searchNode.next
                    
                    # Search if node1 is not adj to any col2 vertex
                    connected = False
                    col2Adj = graph[node].adjColor[col2]
                    while col2Adj != None and not connected:
                        connected = col2Adj.nodeId in visited
                        col2Adj = col2Adj.colNext
            
            # If connected is false then we can swap !!!
            if not connected:
                searchNode = col1Head
                # Update all the nodes in the component
                while searchNode != None:
                    graph[searchNode.nodeId].color = col2 if graph[searchNode.nodeId].color == col1 else col1
                    col2Adj = graph[searchNode.nodeId].adjColor[col2]
                    graph[searchNode.nodeId].adjColor[col2] = graph[searchNode.nodeId].adjColor[col1]
                    graph[searchNode.nodeId].adjColor[col1] = col2Adj
                    searchNode = searchNode.next
                # Update all the neighboring nodes
                searchNode = col1Head
                while searchNode != None:
                    col = graph[searchNode.nodeId].color
                    colOpp = col1 if col == col2 else col2
                    adjNode = graph[searchNode.nodeId].adjList
                    while adjNode != None: # Vi skal opdatere alle nabo knuder
                        if graph[adjNode.nodeId].color != colOpp:
                            adjMate = adjNode.mate # Direkte reference til entry
                            graph[adjNode.nodeId].clear_color(adjMate, colOpp)
                            graph[adjNode.nodeId].assign_color(adjMate, col)
                        adjNode = adjNode.next
                    searchNode = searchNode.next
                k1 = col1
        
        # We can color this node color k1
        graph[node].color = k1
        if k1 > k:
            k = k1
        
        # Update this nodes neighbors
        adjNode = graph[node].adjList
        while adjNode != None:
            adjMate = adjNode.mate
            graph[adjNode.nodeId].assign_color(adjMate, k1)
            adjNode = adjNode.next
    
    if returntype == 'sets': # determine desired return type
        sets = [set() for i in range(k+1)]
        for node in graph.values():
            sets[node.color].add(node.nodeId)
        return sets
    else:
        colors = {}
        for node in graph.values():
            colors[node.nodeId] = node.color
        return colors