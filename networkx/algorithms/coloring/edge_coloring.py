import networkx as nx

__all__ = ["edge_coloring"]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatchable
def edge_coloring(G):
    """This function performs edge coloring on a given graph G.

    Parameters
    ----------
    G: NetworkX graph object representing the input graph.

    Returns
    -------
    coloring: A dictionary where keys are tuples representing edges of the graph,
                and values are integers representing colors assigned to the edges.

    Edge coloring is the assignment of colors to the edges of a graph in such a way
    that no two adjacent edges share the same color. This implementation follows
    the edge coloring algorithm proposed by Vizing.

    """

    def color_edge(edge, color):
        u, v = edge
        used_colors[u][color] = v
        used_colors[v][color] = u
        coloring[(u, v)] = color
        coloring[(v, u)] = color

    G = G.copy()
    degrees = dict(G.degree())
    delta = max(degrees.values())
    colors = set(range(delta + 1))
    coloring = {}
    used_colors = {node: {} for node in G.nodes}

    for edge in G.edges:
        u, v = edge
        u_colors = set(used_colors[u].keys())
        v_colors = set(used_colors[v].keys())
        available_colors = colors - (u_colors | v_colors)

        if available_colors:
            color = min(available_colors)
            color_edge((u, v), color)

        else:
            fan_vertices = []
            fan_colors = []
            c1 = list(colors - set(used_colors[u].keys()))[0]
            fan_colors.append(c1)
            c = c1
            while True:
                xk = used_colors[v][c]
                fan_vertices.append(xk)
                xk_colors = set(used_colors[xk].keys())
                missing_colors_set = colors - (xk_colors.union(v_colors))
                missing_color = next(iter(missing_colors_set), None)

                if missing_color is not None:
                    col = missing_color
                    break

                c = next(iter(v_colors - xk_colors), None)

                if c in fan_colors:
                    a = c
                    b = next(iter(colors - set(used_colors[v].keys())))
                    B = b
                    t = used_colors[xk][b]
                    used_colors[xk].pop(b)
                    s = xk

                    while True:
                        coloring[(s, t)] = a
                        coloring[(t, s)] = a
                        used_colors[s][a] = t

                        if a not in used_colors[t]:
                            used_colors[t].pop(b)
                            used_colors[t][a] = s

                            if t == v:
                                index_b = fan_colors.index(b)
                                fan_colors = fan_colors[:index_b]
                                fan_vertices = fan_vertices[:index_b]
                                col = c
                                break

                            col = B

                            if t == u:
                                fan_vertices = []
                                fan_colors = []
                                break

                            if t in fan_vertices:
                                index_t = fan_vertices.index(t)
                                fan_colors = fan_colors[: index_t + 1]
                                fan_vertices = fan_vertices[: index_t + 1]
                                break

                            break

                        t_old = t
                        t = used_colors[t_old][a]
                        used_colors[t_old][a] = s
                        s = t_old
                        a, b = b, a

                    break

                fan_colors.append(c)

            while fan_vertices:
                x = fan_vertices.pop()
                old_color = coloring[(x, v)]
                used_colors[x].pop(old_color)
                color_edge((x, v), col)
                if fan_colors:
                    col = fan_colors.pop()

            color_edge((u, v), col)

    return coloring
