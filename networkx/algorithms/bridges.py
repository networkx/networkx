import networkx as nx

__author__ = "Rohail Syed <rohailsyed@gmail.com>"

__all__ = [
    'all_bridges',
    'all_local_bridges',
    'bridges_exist',
    'local_bridges_exist'
]


def all_local_bridges(G, first_match=False):
    """ Looks through the graph object G for all local bridges.
    We formally define a local bridge to be any edge AB such that the removal
    of the edge results in a distance strictly greater than 2 between
    nodes A and B. Note that all bridges are local bridges.

    Parameters
    ----------
    G : Undirected Graph object
    first_match : boolean
        Tells us if we should only look for at least one instance of a local
        bridge (True) or look for all (False).

    Returns
    ----------
    dict
        edges : List of edges that are local bridges
        spans : List of corresponding spans of the ith local bridge

    Examples
    --------
    >>> G=nx.cycle_graph(5)
    >>> bridges_dict = all_local_bridges(G)
    >>> bridges_dict["edges"]
    [[0, 1], [0, 4], [1, 2], [2, 3], [3, 4]]
    >>> bridges_dict["spans"]
    [4, 4, 4, 4, 4]

    Notes
    ----------
    This function can be useful to quickly determine what local bridges exist
    in a given network and what their spans are. The function finds the local
    bridges as follows. For each node A in G, capture the list of all
    neighbors it has. For each of these neighbors, remove its edge with A
    and determine A's new shortest path to that node. If none exists, we have
    a bridge(which we represent as having span=-1). Otherwise, if the span
    is strictly greater than 2, that edge is a local bridge. Repeat this
    process for all edges.
    """

    nodeset = sorted(G.nodes())  # only need to sort for consistency in output.
    allBridges = []
    allSpans = []
    bridgeObjs = []
    usedNodes = []
    for startNode in nodeset:
        neighbors = sorted(G.neighbors(startNode))  # same as above
        for endNode in neighbors:
            if endNode in usedNodes:
                # this edge has already been checked. move on
                continue
            if [startNode, endNode] in allBridges:
                # this edge is already known to be a local bridge
                continue
            G.remove_edge(startNode, endNode)
            try:
                pathLength = nx.shortest_path_length(G, startNode, endNode)
                G.add_edge(startNode, endNode)
                if pathLength > 2:
                    # found a local bridge
                    bridgeObjs.append(
                        {"edge": [startNode, endNode], "span": pathLength})
                    if first_match:
                        allBridges.append(sorted([startNode, endNode]))
                        allSpans.append(pathLength)
                        return {"edges": allBridges, "spans": allSpans}

            except nx.NetworkXNoPath:
                # found a bridge
                bridgeObjs.append({"edge": [startNode, endNode], "span": -1})
                G.add_edge(startNode, endNode)
                if first_match:
                    allBridges.append(sorted([startNode, endNode]))
                    allSpans.append(-1)
                    return {"edges": allBridges, "spans": allSpans}
        usedNodes.append(startNode)

    # sort the list in ascending order (for consistency in output)
    for bridge in bridgeObjs:
        bridge["edge"] = sorted(bridge["edge"])
    bridgeObjs = sorted(bridgeObjs, key=lambda x: x["edge"])
    allBridges = []
    allSpans = []
    for bridge in bridgeObjs:
        allBridges.append(bridge["edge"])
        allSpans.append(bridge["span"])

    return {"edges": allBridges, "spans": allSpans}


""" Here, we define the global variables we will need for the Depth-First
Search used in our implementation of Tarjan's Bridge-finding algorithm. """

globalGraph = {}
T = 0
lowest = {}
vals = {}
bridges = []


def dfs(currentNode, parentNode):
    global globalGraph
    global lowest
    global vals
    global T
    global bridges

    vals[currentNode] = T
    lowest[currentNode] = T
    T += 1
    allNeighbors = globalGraph.neighbors(currentNode)
    for neighbor in allNeighbors:
        if not neighbor == parentNode:
            if vals[neighbor] == 0:
                # unvisited node
                dfs(neighbor, currentNode)
                if lowest[neighbor] > vals[currentNode]:
                    # found a bridge
                    bridges.append([currentNode, neighbor])
                lowest[currentNode] = min(
                    lowest[currentNode], lowest[neighbor])
            else:
                # already visited node
                lowest[currentNode] = min(lowest[currentNode], vals[neighbor])


def all_bridges(G):
    global globalGraph
    global lowest
    global vals
    global T
    global bridges

    """ Looks through the graph object G for all bridges.
    We formally define a bridge to be any edge AB such that the removal
    of the edge results in a distance of infinite between nodes A and B.
    Specifically, this means that the total number of connected components
    should increase by one after the removal of the edge.

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    list
        List of edges that are bridges

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> bridges = all_bridges(G)
    >>> bridges
    []
    >>> G.remove_edge(0,1)
    >>> all_bridges(G)
    [[0, 4], [1, 2], [2, 3], [3, 4]]

    Notes
    ----------
    This function can be useful to quickly determine what bridges exist
    in a given network. We use an implemenation of Tarjan's Bridge-finding
    algorithm to do this. In particular, we start with an initial node from
    G and from there run Depth-First Search (DFS) where we reach every node
    once. In each instance, we increment a time variable T, which tells us
    how many steps of the DFS recursion we have done so far. We assign each
    node a value, "vals" of T. This much is pretty standard DFS.

    Now, we go into Tarjan's algorithm. For each node we reached, we not
    only assign a time variable but also a "lowest" variable. The lowest
    variable indicates the distance of a node B to the root node A such
    that the *current* node has a path to B. For any new (unvisited) node
    we encounter, we update the current node's lowest variable to be the
    minimum of their own lowest and that neighbor's lowest since, by
    definition they have access to that neighbor. Similarly, if we encounter
    a node that has already been visited (excluding parents), we update
    the current node's lowest variable to be the minimum of their own
    lowest and that neighbor's time variable value.

    From this algorithm, we can see how to identify bridges. Any node that
    is not a bridge will have at least one non-parent edge that it can use
    to decrease its lowest variable to at minimum that of its parent.
    However, a bridge, having exactly one edge, and no other path, to the
    connected component, will be unable to improve its lowest variable as
    we didn't allow nodes to update from their parents. Therefore, any
    pair of nodes where the lowest variable of one node is strictly greater
    than the value of the other is a bridge.
    """

    # reset the global variables
    globalGraph = G
    T = 0
    bridges = []
    allnodes = G.nodes()
    # The algorithm finds bridges in a connected component. Run this for
    # all components
    all_components = (nx.connected_component_subgraphs(G))
    for comp in all_components:
        T = 0
        allnodes = comp.nodes()
        for node in allnodes:
            lowest[node] = 0
            vals[node] = 0
        # select a starting node
        startnode = allnodes[0]
        # run the DFS
        dfs(startnode, -1)
    # sort the bridges ascending order (for consistency in output)
    for edge in bridges:
        if edge[0] > edge[1]:
            temp = edge[1]
            edge[1] = edge[0]
            edge[0] = temp
    bridges = sorted(bridges)
    return bridges


def local_bridges_exist(G):
    """ Checks if any local bridges exist in this network. We will simply call
    the all_local_bridges() function with the first-match stop parameter.
    Since the search for local bridges will terminate after finding one
    instance, this function is faster if we just want to know if at least
    one local bridge exists in the network and what it is.

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    boolean
        True if we found at least one bridge.
        False otherwise.

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> local_bridges_exist(G)
    True
    >>> G = nx.complete_graph(5)
    >>> local_bridges_exist(G)
    False

    Notes
    ----------
    This function can be useful to quickly determine whether or not local
    bridges exist in a given network.
    """

    results = all_local_bridges(G, first_match=True)
    if len(results["spans"]) > 0:
        return True
    else:
        return False


def bridges_exist(G):
    """ Checks if any bridges exist in this network. We will simply call the
    all_bridges() function and look for non-zero list length.

    Parameters
    ----------
    G : Undirected Graph object

    Returns
    ----------
    boolean
        True if we found at least one bridge.
        False otherwise.

    Examples
    --------
    >>> G = nx.cycle_graph(5)
    >>> bridges_exist(G)
    False
    >>> G.remove_edge(1,2)
    >>> bridges_exist(G)
    True

    Notes
    ----------
    This function can be useful to quickly determine whether or not bridges
    exist in a given network.
    """

    results = all_bridges(G)
    if len(results) > 0:
        return True
    else:
        return False
