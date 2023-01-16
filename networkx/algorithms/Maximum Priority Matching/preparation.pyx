import networkx as nx
cimport cython

@cython.cdivision(True)
cpdef prepare_for_algo(G: nx.Graph, int Priority):

    cdef list roots = []
    cdef list eligible_edges = []

    cdef dict nodes_priorities = nx.get_node_attributes(G, 'priority')
    cdef dict nodes_matching = nx.get_node_attributes(G, 'isMatched')


    for node in G.nodes:
        check_node = str(node)
        if nodes_priorities[check_node] == Priority and not nodes_matching[check_node]:
            roots.append(node)
            nx.set_node_attributes(G, {check_node: {"root": check_node, "isPositive": True, "isReachable": True, "parent": None, "isExternal": True, "blossomsID": -1}})
        else:
            nx.set_node_attributes(G, {check_node: {"root": None, "isPositive": None, "isReachable": False, "parent": None, "isExternal": True, "blossomsID": -1}})

    for root in roots:
        for neighbor in G.neighbors(root):
            edge = (str(root), str(neighbor))
            eligible_edges.append(edge)

    return eligible_edges ,roots

