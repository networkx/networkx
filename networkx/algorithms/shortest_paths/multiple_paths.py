"""K minimum sum edge-disjoint paths using bhandari and suurballe algorithms."""

import heapq

import networkx as nx

__all__ = ["multiple_paths"]


def multiple_paths(graph, source, target, k: int, method="bhandari") -> list:
    """
    Returns a list of minimum edge-disjoint paths, each path is a list of edges, between source and target
    using bhandari or suurballe's algorithm

    There may be less than k edge disjoint minimum sum paths. This returns all of them

    Parameters
    ----------
    graph : NetworkX graph (MultiDiGraph, MultiGraph, DiGraph, Graph)

    source : node
       Starting node for path

    target : node
       Ending node for path

    k : int
       Number of minimum sum edge disjoint paths

    method: string
        Name of method used, options are ('suurballe', 'bhandari')

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target
    NodeNotFound
        If source or target nodes are not in graph

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> edges = [ ('A', 'B', 4), ('A', 'C', 2), ('B', 'C', -3), ('B', 'D', 2),
    >>>          ('C', 'D', 2), ('D', 'E', 1), ('C', 'E', 4) ]
    >>> G.add_weighted_edges_from(edges)
    >>>  path_2 = multiple_paths.multiple_paths(test_graph, 'A', 'E', 2) # [['A', 'B', 'C', 'D', 'E'], ['A', 'C', 'E']]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    """

    def calculate_shortest_path(graph: nx.MultiDiGraph, method: str) -> dict:
        """
        Computes the shortest path between source and target according method chosen,
        method could be 'suurballe' or 'bhandari', suurballe uses dijkstra while bhandari
        uses bellman-ford

        Parameters
        ----------
        graph : networkx.MultiDiGraph

        method: string
            method name, 'suurballe' or 'bhandari'

        Raises
        ------
        NetworkXNoPath
            If no path exists between source and target

        Returns
        --------
        d_path: dict
            dictionary with key 'path' representing the shortest path from source to target as
            list of nodes, if method is suurballe, key 'distance' contains dict of distances
            from source node
        """

        nonlocal source
        nonlocal target

        def bellman_ford(graph: nx.MultiDiGraph, source, target) -> list:
            """
            Compute minimum path from a source node to target node in a multidigraph

            Parameters
            ----------
            graph : networkx.MultiDiGraph

            source: node
               Starting node for path

            target: node
               Ending node for path

            Raises
            ------
            NetworkXNoPath
                If no path exists between source and target

            Returns
            -------
            path: list of nodes in the shortest path from source to target
            """

            # Initialize distances and predecessors
            distances = {node: float("inf") for node in graph.nodes}
            predecessors = {node: None for node in graph.nodes}
            distances[source] = 0

            # Relax edges |V| - 1 times
            for _ in range(len(graph.nodes) - 1):
                for u, v, key in graph.edges(keys=True):
                    weight = graph[u][v][key]["weight"]
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
                        predecessors[v] = u

            # Check for negative-weight cycles
            for u, v, key in graph.edges(keys=True):
                weight = graph[u][v][key]["weight"]
                if distances[u] + weight < distances[v]:
                    raise ValueError("Graph contains a negative-weight cycle")

            # build path between source and target
            path = []
            node = target
            while node is not None:
                path.insert(0, node)
                node = predecessors[node]

            if path[0] != source:
                raise nx.NetworkXNoPath(f"{target} is not reachable from {source}")

            return path

        def dijkstra(graph: nx.MultiDiGraph, source, target) -> (dict, list):
            """
            Compute distances from source to all other nodes, and minimum path from source to target in a multidigraph.

            Parameters
            ----------
            graph : networkx.MultiDiGraph

            source: node
               Starting node for path

            target: node
               Ending node for path

            Raises
            ------
            NetworkXNoPath
                If no path exists between source and target

            Returns
            --------
            distances: dict of shortest distances from the source to each node
            path: list of nodes in the shortest path between source and target
            """

            # Priority queue (min-heap)
            priority_queue = []
            heapq.heappush(priority_queue, (0, source))

            # Distances and predecessors
            distances = {node: float("inf") for node in graph.nodes}
            predecessors = {node: None for node in graph.nodes}
            distances[source] = 0

            # Visited nodes
            visited = set()

            while priority_queue:
                # Get node with the smallest distance
                current_distance, current_node = heapq.heappop(priority_queue)

                # Skip if already visited
                if current_node in visited:
                    continue
                visited.add(current_node)

                # Relax edges
                for u, v, key in graph.out_edges(current_node, keys=True):
                    weight = graph[u][v][key]["weight"]
                    distance = current_distance + weight

                    if distance < distances[v]:
                        distances[v] = distance
                        predecessors[v] = current_node
                        heapq.heappush(priority_queue, (distance, v))
            # build path
            path = []
            node = target
            while node is not None:
                path.insert(0, node)
                node = predecessors[node]

            if path[0] != source:
                raise nx.NetworkXNoPath(f"{target} is not reachable from {source}")

            return distances, path

        path = None
        d_len = None
        try:
            if method == "bhandari":
                path = bellman_ford(graph, source, target)
            elif method == "suurballe":
                d_len, path = dijkstra(graph, source, target)
        except nx.NetworkXNoPath:
            return {"path": None}

        if path is None:
            raise ValueError(
                "Unknown exception occurred in method 'calculate_shortest_path'"
            )

        # Convert into path of edges
        path = zip(path, path[1:])

        # Add key to edges, since it is the shortest path, the key with minimum weight
        path_with_keys = []
        for u, v in path:
            edge_keys = graph[u][v]  # Get all ways for edge (u, v)
            min_key = min(
                edge_keys, key=lambda k: graph[u][v][k]["weight"]
            )  # Find the key with the minimum weight
            path_with_keys.append((u, v, min_key))  # Save the edge with its key

        d_out = {"path": path_with_keys}
        if method == "suurballe":
            if d_len is None:
                raise ValueError(
                    "Unknown exception occurred in method 'calculate_shortest_path'"
                )
            d_out["distance"] = d_len

        return d_out

    def transform_graph(graph: nx.MultiDiGraph, d_path: dict, method: str) -> None:
        """
        transforms graph according method and information given in d_path

        Parameters
        ----------
        graph: networkx.MultiDiGraph

        d_path: dict
             dictionary with key 'path', storing a list of nodes of shortest path between source and target
             and if method is 'suurballe' contains a key called 'distance' storing a dictionary of distance
             of source to all nodes in graph

        method: str, name of method, 'suurballe' or 'bhandari'
        """
        nonlocal source
        path = d_path["path"]

        if method == "bhandari":
            for u, v, key in path:
                weight = graph[u][v][key]["weight"]
                graph.remove_edge(u, v, key)
                graph.add_edge(v, u, key=key, weight=-weight)

        elif method == "suurballe":
            # STEP1: find distances

            edges_lst = list(graph.edges)
            d_len = d_path["distance"]

            # STEP2: transform edges
            for u, v, key in edges_lst:
                new_w = graph[u][v][key]["weight"] + d_len[u] - d_len[v]
                if (u, v, key) in path:
                    graph.remove_edge(u, v, key)
                    graph.add_edge(v, u, key=key, weight=new_w)
                else:
                    graph[u][v][key]["weight"] = new_w

    def copy_with_unique_keys(graph: nx.MultiDiGraph):
        """
        copies given multidigraph with unique keys

        Parameters
        ----------
        graph: networkx.MultiDiGraph

        return
        ------
        graph: networkx.MultiDiGraph
            a graph with unique keys
        """
        new_graph = nx.MultiDiGraph()
        counter = 0
        for u, v, data in graph.edges(
            data=True,
        ):
            new_graph.add_edge(u, v, key=counter, **data)
            counter += 1
        return new_graph

    # check input is valid
    if k <= 0:
        raise ValueError("Number of paths must be positive.")
    if source == target:
        raise ValueError(f"Target {target} is Equal to Source {source}")
    if source not in graph:
        raise nx.NodeNotFound(f"Source {source} is not in G")
    if target not in graph:
        raise nx.NodeNotFound(f"Target {target} is not in G")
    if method not in ("suurballe", "bhandari"):
        raise ValueError(f"method not supported: {method}")

    graph_nodes = list(graph.nodes)
    # copy original graph and transform to multidigraph
    if isinstance(graph, nx.MultiDiGraph):
        working_graph = copy_with_unique_keys(graph)
    elif isinstance(graph, nx.MultiGraph):
        working_graph = copy_with_unique_keys(graph.to_directed())
    elif isinstance(graph, nx.DiGraph):
        working_graph = copy_with_unique_keys(nx.MultiDiGraph(graph))
    elif isinstance(graph, nx.Graph):
        working_graph = copy_with_unique_keys(nx.MultiDiGraph(nx.DiGraph(graph)))
    else:
        raise ValueError("graph type not supported")

    for v in graph_nodes:
        if v not in working_graph.nodes:
            working_graph.add_node(v)

    if method == "suurballe":
        for u, v, key in working_graph.edges(keys=True):
            if working_graph[u][v][key]["weight"] < 0:
                raise ValueError("suurballe can't run with negative weights")

    original_graph = working_graph.copy()

    path_list = []

    d_path = calculate_shortest_path(working_graph, method)
    current_path = d_path["path"]
    # check target is reachable from source
    if current_path is None:
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")

    path_list.append(current_path)
    for _ in range(k - 1):
        transform_graph(
            working_graph, d_path, method
        )  # transform working graph on last path
        d_path = calculate_shortest_path(working_graph, method)
        current_path = d_path["path"]
        if current_path is None:
            break
        path_list.append(current_path)

    # Delete overlapping edges
    d_valid_edges = {}
    for path in path_list:
        for u, v, key in path:
            edge_set = frozenset([u, v, key])
            if edge_set in d_valid_edges:
                del d_valid_edges[edge_set]
            else:
                d_valid_edges[edge_set] = (u, v, key)
    valid_edges = set(d_valid_edges.values())

    # build edge-disjoint paths from set of edges that are not overlapping
    d_src_to_edges = {}  # u -> [edges in the form (u, v, key)]
    for u, v, key in valid_edges:
        if u not in d_src_to_edges:
            d_src_to_edges[u] = []
        d_src_to_edges[u].append((u, v, key))

    # build paths into a list
    paths = []
    while len(d_src_to_edges[source]) > 0:
        path = []
        current = d_src_to_edges[source].pop(0)
        path.append(current)
        # follow the path
        while current[1] != target:
            current = d_src_to_edges[current[1]].pop(0)
            path.append(current)
        paths.append(path)

    # sort paths by weight
    sorted_paths = sorted(
        paths,
        key=lambda path: (sum(original_graph[u][v][k]["weight"] for u, v, k in path)),
    )

    # convert paths from list of edges to list of nodes
    nodes_sorted_path = []
    for p in sorted_paths:
        n = len(p)
        new_p = []
        for i in range(n):
            e = p[i]
            new_p.append(e[0])
            if i == n - 1:
                new_p.append(e[1])

        nodes_sorted_path.append(new_p)

    return nodes_sorted_path
