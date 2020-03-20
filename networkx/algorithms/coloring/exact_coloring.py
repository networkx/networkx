"""
Exact graph coloring.
"""

import networkx as nx

__all__ = ['exact_color']

# https://home.mis.u-picardie.fr/~cli/color6COR2014publishedVersion.pdf
# https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.connected_components.html
# https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.is_connected.html
# https://networkx.github.io/documentation/stable/reference/generators.html
# https://networkx.github.io/documentation/stable/developer/contribute.html
# https://networkx.github.io/documentation/stable/developer/gitwash/development_workflow.html#development-workflow
# https://networkx.github.io/documentation/networkx-1.10/reference/credits.html
# https://matthew-brett.github.io/pydagogue/rebase_without_tears.html
# https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard

custom_infinity = 2**31

class Solution():
    def __init__(self, used_colors, color_mapping):
        self.used_colors = used_colors
        self.color_mapping = color_mapping

    def copy(self):
        return Solution(
            self.used_colors,
            self.color_mapping.copy()
        )


# backGCP algorithm
def exact_color(graph, is_connected = False):
    """Color a graph using the minimum number of colors.
    
    Finds an exact coloring of the given graph.
    If the graph is not connected, the algorithm recursively colors
    all connected components separately.
    
    Although the algorithm is already present in the literature [1]_,
    it is the heuristic that is critical to the performance of the algorithm.
    
    This implementation has a custom heuristic optimized for random graphs
    the original can be seen in [2]_.

    Parameters
    ----------
    G : NetworkX graph

    References
    ----------
    .. [1] (TODO) https://home.mis.u-picardie.fr/~cli/color6COR2014publishedVersion.pdf
    .. [2] (TODO) (my github)
    """

    # color mapping for an empty graph
    if len(graph) == 0:
        return {}

    if is_connected or nx.is_connected(graph):
        # this dummy solution will be replaced by the algorithm
        dummy_solution = Solution(custom_infinity, {})
        initial_solution = Solution(0, {})
        best_solution = _recurse(graph, initial_solution, dummy_solution)
        return best_solution.color_mapping
    else:
        connected_components = nx.connected_components(graph)
        solutions = dict()
        for connected_component in connected_components:
            solution = exact_color(graph.subgraph(connected_component), True)
            solutions = {**solutions, **solution}
        return solutions


def _recurse(graph, current_solution, best_solution):
    """ Returns best solution given the currently considered solution and
        best solution found so far.
    """
    
    if len(current_solution.color_mapping) < len(graph):
        node_to_color, usable_colors = _choose_branching_node(
            graph,
            current_solution, 
            best_solution
            )

        # for in possible colors
        for color in usable_colors:
            increased_color_count = False
            if color >= current_solution.used_colors:
                current_solution.used_colors += 1
                increased_color_count = True
            if current_solution.used_colors < best_solution.used_colors:
                current_solution.color_mapping[node_to_color] = color

                # recurse and update best statistics
                best_solution = _recurse(graph, current_solution, best_solution)

                del current_solution.color_mapping[node_to_color]
            if increased_color_count:
                current_solution.used_colors -= 1
    
    else:
        # all of the nodes are colored
        # clone the current solution since it is the best solution found so far
        best_solution = current_solution.copy()

    return best_solution


def _choose_branching_node(graph, current_solution, best_solution):
    """ may return -1 if there is no suitable node """
    
    min_score = custom_infinity
    max_neighbor_count = -1
    best_node = None
    best_allowed_colors = None

    for node in graph.nodes:
        # node is not colored
        if node not in current_solution.color_mapping:
            usable_colors = _get_possible_colorings(
                graph,
                node,
                current_solution,
                best_solution
                )

            # cannot color a node, return immediately
            if len(usable_colors) == 0:
                return node, usable_colors

            score = len(usable_colors)

            # defer nodes that require using more colors
            if usable_colors[-1] == current_solution.used_colors:
                score += custom_infinity / 2

            if score < min_score  or \
                (score == min_score and len(graph[node]) > max_neighbor_count):
                max_neighbor_count = len(graph[node])
                min_score = score
                best_node = node
                best_allowed_colors = usable_colors

    return best_node, best_allowed_colors


def _get_possible_colorings(graph, node, current_solution, best_solution):
    usable_colors = []
    # there can be at most 1 new color and it should be less that current best
    maximum_inclusive_permissible_color = min(
        current_solution.used_colors,
        best_solution.used_colors - 2
        )
    uncolored_neighbors = 0
    allowed_colors = [True] * (len(graph[node]) + 1)
    for neighbor in graph[node]:
        if neighbor not in current_solution.color_mapping:
            uncolored_neighbors += 1
        else:
            color = current_solution.color_mapping[neighbor]
            if (color < len(allowed_colors)):
                allowed_colors[color] = False

    color = 0
    # key heuristic: limit the number of used colors as much as possible
    while color <= maximum_inclusive_permissible_color \
            and len(usable_colors) <= uncolored_neighbors:
        if allowed_colors[color]:
            usable_colors.append(color)
        color += 1

    return usable_colors