import networkx as nx


@nx._dispatch
def simple_cycles_le_k(graph, k):
    """
    Find simple cycles (elementary circuits) of a directed graph.
    A simple cycle, or elementary circuit, is a closed path where no node appears twice.
    Two elementary circuits are distinct if they are not cyclic permutations of each other.
    This is a nonrecursive, iterator/generator modified version of Johnson’s algorithm
    for finding all elementary cycles in a graph so that is does not search for cycles larger than some maximum length.
    found at :https://stackoverflow.com/questions/46590502/how-to-modify-johnsons-elementary-cycles-algorithm-to-cap-maximum-cycle-length

    >>> Digraph=nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,5,6,7,8])
    >>> Digraph.add_weighted_edges_from([(1,8,2),(8,1,4),(2,1,5),(1,3,4),(3,8,2),(8,2,3),(8,5,4),(5,7,3),(7,6,2),(6,5,4)])
    >>> Ys=simple_cycles_le_k(Digraph,3)
    >>> a=[y for y in Ys]
    >>> print(a)
    [[8, 2, 1], [8, 1, 3], [8, 1], [5, 7, 6]]
    >>> Digraph =nx.DiGraph()
    >>> Digraph.add_nodes_from([1,2,3,4])
    >>> Digraph.add_weighted_edges_from([(2,1,3),(1,3,1),(3,2,2),(3,4,5),(4,3,9)])
    >>> Ys=simple_cycles_le_k(Digraph,3)
    >>> a=[y for y in Ys]
    >>> print(a)
    [[1, 3, 2], [3, 4]]
    >>> graphEX3 = nx.DiGraph()
    >>> graphEX3.add_nodes_from([10,11,12,13,14,15,16])
    >>> Digraph.add_weighted_edges_from([(10,11,10),(11,12,5),(12,13,6),(13,10,4),(11,14,2),(14,16,3),(16,15,8),(15,14,6)])
    >>> Ys=simple_cycles_le_k(Digraph,3)
    >>> a=[y for y in Ys]
    >>> print(a)
    [[16, 15, 14], [1, 3, 2], [3, 4]]
    """
    subG = type(graph)(graph.edges())
    ccs = list(nx.strongly_connected_components(subG))
    while ccs:
        scc = ccs.pop()
        startnode = scc.pop()
        path = [startnode]
        blocked = set()
        blocked.add(startnode)
        stack = [(startnode, list(subG[startnode]))]

        while stack:
            thisnode, nbrs = stack[-1]

            if nbrs and len(path) <= k:
                nextnode = nbrs.pop()
                if nextnode == startnode:
                    yield path[:]
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append((nextnode, list(subG[nextnode])))
                    blocked.add(nextnode)
                    continue
            if not nbrs or len(path) >= k:
                blocked.remove(thisnode)
                stack.pop()
                path.pop()
        subG.remove_node(startnode)
        H = subG.subgraph(scc)
        ccs.extend(nx.strongly_connected_components(H))
