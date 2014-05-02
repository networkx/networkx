import networkx as nx

class Node(object):

    __slots__ = ['node_id', 'color', 'adj_list', 'adj_color']

    def __init__(self, node_id, n):
        self.node_id = node_id
        self.color = -1
        self.adj_list = None
        self.adj_color = [None for _ in range(n)]

    def __repr__(self):
        return "Node_id: {0}, Color: {2}, Adj_list: ({3}), adj_color: ({4})".format(
            self.node_id, self.color, self.adj_list, self.adj_color)

    def assign_color(self, adjEntry, color):
        adjEntry.col_prev = None
        adjEntry.col_next = self.adj_color[color]
        self.adj_color[color] = adjEntry
        if adjEntry.col_next != None:
            adjEntry.col_next.col_prev = adjEntry

    def clear_color(self, adjEntry, color):
        if adjEntry.col_prev == None:
            self.adj_color[color] = adjEntry.col_next
        else:
            adjEntry.col_prev.col_next = adjEntry.col_next
        if adjEntry.col_next != None:
            adjEntry.col_next.col_prev = adjEntry.col_prev

    def iter_neighbors(self):
        adj_node = self.adj_list
        while adj_node != None:
            yield adj_node
            adj_node = adj_node.next

    def iter_neighbors_color(self, color):
        adj_color_node = self.adj_color[color]
        while adj_color_node != None:
            yield adj_color_node
            adj_color_node = adj_color_node.col_next

class AdjEntry(object):

    __slots__ = ['node_id', 'next', 'mate', 'col_next', 'col_prev']

    def __init__(self, node_id):
        self.node_id = node_id
        self.next = None
        self.mate = None
        self.col_next = None
        self.col_prev = None

    def __repr__(self):
        return "Node_id: {0}, Next: ({1}), Mate: ({2}), col_next: ({3}), col_prev: ({4})".format(
            self.node_id, self.next, self.mate.node_id, None if self.col_next == None else self.col_next.node_id, None if self.col_prev == None else self.col_prev.node_id)

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
    for node_id in original_graph.nodes_iter():
        graph[node_id] = Node(node_id, n)
    for (node1, node2) in original_graph.edges_iter():
        adj_entry1 = AdjEntry(node2)
        adj_entry2 = AdjEntry(node1)
        adj_entry1.mate = adj_entry2
        adj_entry2.mate = adj_entry1
        node1_head = graph[node1].adj_list
        adj_entry1.next = node1_head
        graph[node1].adj_list = adj_entry1
        node2_head = graph[node2].adj_list
        adj_entry2.next = node2_head
        graph[node2].adj_list = adj_entry2

    k = 0
    for node in nodes:
        # Find the color with the lowest possible value
        k1 = 0
        col_used = [0 for i in range(k+2)]
        for adj_node in graph[node].iter_neighbors():
            col = graph[adj_node.node_id].color
            if col != -1:
                col_used[col] = 1
        while col_used[k1] != 0:
            k1 += 1

        # k1 is now the lowest available color
        if k1 > k:
            connected = True
            visited = set()
            col1 = -1
            col2 = -1
            while connected and col1 < k:
                col1 += 1
                col1_adj = []
                for col1_adj_iter in graph[node].iter_neighbors_color(col1):
                    col1_adj.append(col1_adj_iter.node_id)

                col2 = col1
                while connected and col2 < k:
                    col2 += 1
                    visited = set(col1_adj)
                    frontier = list(col1_adj)
                    i = 0
                    while i < len(frontier):
                        search_node = frontier[i]
                        i += 1
                        col_opp = col2 if graph[search_node].color == col1 else col1
                        for neighbour in graph[search_node].iter_neighbors_color(col_opp):
                            if not neighbour.node_id in visited:
                                visited.add(neighbour.node_id)
                                frontier.append(neighbour.node_id)

                    # Search if node is not adj to any col2 vertex
                    connected = False
                    for col2_adj in graph[node].iter_neighbors_color(col2):
                        connected = connected or col2_adj.node_id in visited

            # If connected is false then we can swap !!!
            if not connected:
                # Update all the nodes in the component
                for search_node in visited:
                    graph[search_node].color = col2 if graph[search_node].color == col1 else col1
                    col2_adj = graph[search_node].adj_color[col2]
                    graph[search_node].adj_color[col2] = graph[search_node].adj_color[col1]
                    graph[search_node].adj_color[col1] = col2_adj
                # Update all the neighboring nodes
                for search_node in visited:
                    col = graph[search_node].color
                    col_opp = col1 if col == col2 else col2
                    for adj_node in graph[search_node].iter_neighbors():
                        if graph[adj_node.node_id].color != col_opp:
                            adj_mate = adj_node.mate # Direct reference to entry
                            graph[adj_node.node_id].clear_color(adj_mate, col_opp)
                            graph[adj_node.node_id].assign_color(adj_mate, col)
                k1 = col1

        # We can color this node color k1
        graph[node].color = k1
        if k1 > k:
            k = k1

        # Update this nodes neighbors
        for adj_node in graph[node].iter_neighbors():
            adj_mate = adj_node.mate
            graph[adj_node.node_id].assign_color(adj_mate, k1)

    if returntype == 'sets': # determine desired return type
        sets = [set() for i in range(k+1)]
        for node in graph.values():
            sets[node.color].add(node.node_id)
        return sets
    else:
        colors = {}
        for node in graph.values():
            colors[node.node_id] = node.color
        return colors
