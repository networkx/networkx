import networkx as nx

__all__ = ["edge_coloring"]


@nx.utils.not_implemented_for("directed")
@nx.utils.not_implemented_for("multigraph")
@nx._dispatchable
def edge_coloring(G):
    """This function performs edge coloring on a given graph G.

    Edge coloring is the assignment of colors to the edges of a graph in such a way
    that no two adjacent edges share the same color.

    Parameters
    ----------
    G: NetworkX graph object representing the input graph.

    Returns
    -------
    coloring: A dictionary where keys are tuples representing edges of the graph,
                and values are integers representing colors assigned to the edges.


    References
    ----------
    This implementation follows the proof of the lemma given in Zdenek Dvorak's lecture notes
    titled Graph coloring: Heawood and Brooks theorems, edge coloring which states
    Let G be a graph of maximum degree at most d with edges properly colored using
    d + 1 colors. Let u and v be distinct non-adjacent vertices of G.
    Then there exists a proper edge coloring using d + 1 colors
    such that the same color missing at both u and v.
    https://iuuk.mff.cuni.cz/~rakdver/kgii/lesson20-6.pdf
    """

    # function to color an edge
    def color_edge(edge, color):
        u, v = edge
        used_colors[u][color] = v
        used_colors[v][color] = u
        coloring[(u, v)] = color
        coloring[(v, u)] = color

    G = G.copy()
    delta = max(deg for node, deg in G.degree)
    colors = set(range(delta + 1))
    coloring = {}
    used_colors = {node: {} for node in G.nodes}

    for edge in G.edges:
        u, v = edge
        u_colors = used_colors[u]
        v_colors = used_colors[v]
        available_colors = colors - (u_colors.keys() | v_colors.keys())

        # no conflict case
        if available_colors:
            color = min(available_colors)
            color_edge((u, v), color)

        else:
            fan_vertices = []
            fan_colors = []
            c = next(c for c in colors if c not in u_colors)
            kempe_flag = 0

            # Start finding fan
            while True:
                xk = v_colors[c]
                fan_vertices.append(xk)
                fan_colors.append(c)
                xk_colors = set(used_colors[xk].keys())
                available_colors = colors - (xk_colors | v_colors.keys())

                # Simple fan recoloring case
                if available_colors:
                    col = min(available_colors)
                    break

                c = next(iter(v_colors.keys() - xk_colors), None)

                # Kempe Chain Case
                if c in fan_colors:
                    kempe_flag = 1
                    break

            # Finding Kempe Chain
            if kempe_flag:
                a = c
                b = min(colors - v_colors.keys())
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

                        # Kempe chain ending at v
                        if t == v:
                            index_b = fan_colors.index(b)
                            fan_colors = fan_colors[:index_b]
                            fan_vertices = fan_vertices[:index_b]
                            col = c
                            break

                        col = B

                        # Kempe chain ending at u
                        if t == u:
                            fan_vertices = []
                            fan_colors = []
                            break

                        # Kempe chain ending at one of the fan vertices
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

            # Recoloring the fan
            while fan_vertices:
                x = fan_vertices.pop()
                old_color = coloring[(x, v)]
                used_colors[x].pop(old_color)
                color_edge((x, v), col)
                if fan_colors:
                    col = fan_colors.pop()

            color_edge((u, v), col)

    return coloring
