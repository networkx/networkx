import math
import logging
import networkx as nx
import matplotlib.pyplot as plt

logger = logging.getLogger("contiguous_oriented_labeling")
formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: Line %(lineno)d: %(message)s')
console = logging.StreamHandler()
logger.handlers = [console]
console.setFormatter(formatter)
logging.basicConfig(filename="contiguous_oriented_labeling.log", level=logging.DEBUG)


def graph_example1():
    """
    Notice that this graph is almost bridgeless, if we add edge (3,6) for example  this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (4, 6), (4, 5), (5, 6)])
    # nx.draw(g)
    # plt.show()
    return g


def graph_example2():
    """
    Notice that this graph is almost bridgeless, if we add edge (1,5) for example  this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5])
    g.add_edges_from([(1, 2), (2, 3), (2, 5), (5, 4), (4, 3)])
    # nx.draw(g)
    # plt.show()
    return g


def graph_example3():
    """
    Notice that this graph is almost bridgeless, if we add edge (1,6) for example  this graph will be bridgeless
    """
    g = nx.Graph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2), (2, 3), (2, 5), (5, 4), (4, 3), (5, 6)])
    # nx.draw(g)
    # plt.show()
    return g


def get_contiguous_oriented_labeling(graph):
    """
    This algorithm admits a contiguous oriented labeling in an almost bridgeless graph
    Parameters
    ----------
    graph : NetworkX graph
        almost bridgeless graph

    Returns
    -------
    a contiguous oriented labeling.
    First value is a list of each edge ordered by its labeling.
    Second value is a dictionary of each vertex and its oriantations.

    Notes
    -------
    A bridge of a graph is an edge that is not contained in any cycle.
    A graph is said to be bridgeless if it contains no bridges.
    A graph is said to be almost bridgeless if we can add an edge so that the resulting
    graph is bridgeless.
    An oriented labeling of a graph with m edges is a labeling of the edges with
    numbers 1, 2, . . . ,m, using each number exactly once, together with a labeling of one endpoint of
    each edge i with i− and the other endpoint with i+ (so each vertex receives a number of labels
    equal to the number of edges adjacent to it). An oriented labeling is said to be contiguous if:
    • For each 2 ≤ i ≤ m, the edges labeled 1, 2, . . . , i − 1 form a connected subgraph, and the
    vertex labeled i− belongs to one of these edges.
    • For each 1 ≤ i ≤ m − 1, the edges labeled i + 1, i + 2, . . . ,m form a connected subgraph, and
    the vertex labeled i+ belongs to one of these edges.

     References
    ----------
    Based on an article by Xiaohui Bei and Warut Suksompong
    https://arxiv.org/pdf/1910.14129.pdf#subsection.4.1 - 2019

    Programmer : Eran Katz

    >>> get_contiguous_oriented_labeling(graph_example1())
    ([(1, 3), (3, 2), (1, 2), (2, 4), (4, 6), (6, 5), (5, 4)], InEdgeView([(1, 2), (3, 2), (2, 4), (5, 4), (1, 3), (4, 6), (6, 5)]))
    >>> get_contiguous_oriented_labeling(graph_example2())
    ([(1, 2), (2, 5), (5, 4), (4, 3), (2, 3)], InEdgeView([(1, 2), (2, 3), (4, 3), (2, 5), (5, 4)]))
    >>> get_contiguous_oriented_labeling(graph_example3())
    ([(1, 2), (2, 5), (2, 3), (3, 4), (4, 5), (5, 6)], InEdgeView([(1, 2), (2, 3), (3, 4), (4, 5), (2, 5), (5, 6)]))
    """
    g, u, v = almost_bridgeless_to_bridgless(graph)
    ordered_edges = []
    nodes_in_ears = []
    oriented_graph = nx.DiGraph()
    for path in nx.all_simple_paths(g, source=u, target=v): # find a path from u to v and add it's edges
        logger.info("Gets a path from u to v")
        for i in range(len(path) - 1):
            if path[i] != u or path[i + 1] != v:
                ordered_edges.append((path[i], path[i + 1]))
                oriented_graph.add_edge(path[i], path[i + 1])
                if path[i] not in nodes_in_ears:
                    nodes_in_ears.append(path[i])
                if path[i + 1] not in nodes_in_ears:
                    nodes_in_ears.append(path[i + 1])
        break
    idx = 0
    x_idx = math.inf
    t = x_idx
    c = 0
    cycle = False # a flag to determine if an ear is a cycle. if x = z
    t_update = True # a flag to determine where to insert edges in order
    for edge in graph.edges: # iterate over all the edges to find edge x,y. x in ear and y is not
        logger.info("Find an edge legal for an ear")
        if edge not in ordered_edges and tuple(reversed(edge)) not in ordered_edges:
            if edge[0] in nodes_in_ears and edge[1] not in nodes_in_ears: # find the x and y
                x = edge[0]
                y = edge[1]
                for node in nodes_in_ears: # iterate over all the nodes in ears and find a legal path from x to another node in ear
                    for path in nx.all_simple_paths(graph, source=x, target=node):
                        logger.info("Find ear")
                        if check_path(nodes_in_ears, path, node, edge) and c == 0:
                            logger.debug(f"A legal ear {path}")
                            cycle = True
                            for i in range(len(path) - 1): # go over he path and add the edges one by one
                                if (path[i], path[i + 1]) not in ordered_edges:
                                    logger.info("Insert the edges of the ear")
                                    if x == u: # we insert from the start of the order
                                        ordered_edges.insert(idx, (path[i], path[i + 1]))
                                        idx += 1
                                        oriented_graph.add_edge(path[i], path[i + 1])
                                    else: # we insert from the first edge directed to x
                                        if t_update:
                                            x_directed = oriented_graph.in_edges(x)
                                            for e1 in x_directed:
                                                if e1 in ordered_edges or tuple(reversed(e1)) in ordered_edges:
                                                    x_idx = min(ordered_edges.index(e1), x_idx)
                                                    t = x_idx + 1
                                        ordered_edges.insert(t, (path[i], path[i + 1]))
                                        oriented_graph.add_edge(path[i], path[i + 1])
                                        logger.debug(f"Ordered Edges {ordered_edges}")
                                        logger.debug(f"Oriented Graph {oriented_graph}")
                                        t += 1
                                        t_update = False
                                if path[i] not in nodes_in_ears:
                                    nodes_in_ears.append(path[i])
                                if path[i + 1] not in nodes_in_ears:
                                    nodes_in_ears.append(path[i + 1])
                            c = 1
                            idx = 0
                            x_idx = math.inf
                c = 0
                if not cycle: # if its a cycle we find a path from y back to x
                    logger.info("If its a cycle")
                    for path in nx.all_simple_paths(graph, source=y, target=x):
                        path.insert(0, x) # we add x at the start to complete the ear
                        if check_path(nodes_in_ears, path, x, (x, y)) and path != [x, y, x]:
                            for i in range(len(path) - 1):
                                if (path[i], path[i + 1]) not in ordered_edges:
                                    if x == u:
                                        ordered_edges.insert(idx, (path[i], path[i + 1]))
                                        idx += 1
                                        oriented_graph.add_edge(path[i], path[i + 1])
                                    else:
                                        if t_update:
                                            x_directed = oriented_graph.in_edges(x)
                                            for e1 in x_directed:
                                                if e1 in ordered_edges or tuple(reversed(e1)) in ordered_edges:
                                                    x_idx = min(ordered_edges.index(e1), x_idx)
                                                    t = x_idx + 1
                                        ordered_edges.insert(t, (path[i], path[i + 1]))
                                        oriented_graph.add_edge(path[i], path[i + 1])
                                        t += 1
                                        t_update = False

                cycle = False
            elif edge[0] in nodes_in_ears and edge[1] in nodes_in_ears: # if both of the vertices of the edge already in an ear we add it after the first edge directed into x
                logger.info("If both vertices already in an ear")
                x = edge[0]
                y = edge[1]
                if t_update:
                    x_directed = oriented_graph.in_edges(x)
                    for e1 in x_directed:
                        if e1 in ordered_edges or tuple(reversed(e1)) in ordered_edges:
                            x_idx = min(ordered_edges.index(e1), x_idx)
                            t = x_idx + 1
                ordered_edges.insert(t, (x, y))  # append after the first edge directed into x
                oriented_graph.add_edge(x, y)
                t += 1
                t_update = False

    return ordered_edges, oriented_graph.in_edges


def almost_bridgeless_to_bridgless(g):
    """
    This function takes an almost bridgeless graph and adds an edge so it makes it bridgeless
    """
    u, v = 0, 0
    graph = g.copy()
    for i in nx.non_edges(graph):
        graph.add_edges_from([i])
        if nx.has_bridges(graph):
            graph.remove_edge(i[0], i[1])
        else:
            u, v = i[0], i[1]
            break
    return graph, u, v


def check_path(nodes_in_ears: list, path: list, node, edge):
    """
    This function checks if the ear is a legal ear. Each ear is a path starting at a vertex of a previous ear and ending at a vertex of a
    previous ear (possibly the same as the former vertex, in which case the path becomes a cycle) but not going through any other vertex of a previous ear
    """
    if path[1] == edge[1] and path[-1] == node and all(n not in nodes_in_ears for n in path[2:-1]):
        return True
    return False
