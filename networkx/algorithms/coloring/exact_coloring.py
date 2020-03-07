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

# backGCP algorithm
def exact_color(graph, upper_bound_on_number_of_steps: int = -1, alpha_ratio: float = 1.0):
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

    if len(graph) == 0:
        return {}

    # solution = (colorCount, vertex_to_color)
    dummy_solution = [custom_infinity, {}]
    initial_solution = [0, {}]

    best_solution, remaining_number_of_steps = _recurse(graph, initial_solution, dummy_solution, upper_bound_on_number_of_steps, alpha_ratio)
    return best_solution[1]


def _recurse(graph, current_solution, best_solution, upper_bound_on_number_of_steps, alpha_ratio):
    upper_bound_on_number_of_steps_left = upper_bound_on_number_of_steps

    # there exists a limit to the number of executed steps
    # and already found a valid solution
    if upper_bound_on_number_of_steps != -1 and len(best_solution[1]) == len(graph):
        if upper_bound_on_number_of_steps == 0:
            return best_solution
        else:
            upper_bound_on_number_of_steps -= 1
    
    if len(current_solution[1]) < len(graph):
    
        # choose a vertex to color
        vertex_to_color = 0
        coloring_possibilities = []
        if False:
            vertex_to_color, coloring_possibilities = _choose_suitable_vertex_fast(graph, current_solution, best_solution)
        else:
            vertex_to_color, coloring_possibilities = _choose_suitable_vertex(graph, current_solution, best_solution)

        # for in possible colors
        for color in coloring_possibilities:
            increased_color_count = False
            if color >= current_solution[0]:
                current_solution[0] += 1
                increased_color_count = True
            if current_solution[0] * alpha_ratio < best_solution[0]:
                current_solution[1][vertex_to_color] = color

                # recurse and update best statistics
                best_solution, upper_bound_on_number_of_steps_left = _recurse(graph, current_solution, best_solution, upper_bound_on_number_of_steps_left, alpha_ratio)

                del current_solution[1][vertex_to_color]
            if increased_color_count:
                current_solution[0] -= 1
    
    else:
        # warning! there may be vertices with negative colorings!
        best_solution = (current_solution[0], current_solution[1].copy())

    return best_solution, upper_bound_on_number_of_steps_left

    # may return -1 if there is no suitable vertex
def _choose_suitable_vertex(graph, current_solution, best_solution):
    min_color_possibilities = custom_infinity
    max_neighbor_count = -1
    max_vertex = -1
    best_coloring = None

    for node in graph.nodes:
        if node not in current_solution[1]:
            colorings_neighbor = _get_possible_colorings(graph, node, current_solution, best_solution)
            if len(colorings_neighbor) == 0:
                best_coloring = colorings_neighbor
                return node, best_coloring
            score = len(colorings_neighbor)
            if colorings_neighbor[len(colorings_neighbor) - 1] == current_solution[0]:
                score += custom_infinity / 2
            if score < min_color_possibilities or (score == min_color_possibilities and len(graph[node]) > max_neighbor_count):
                max_neighbor_count = len(graph[node])
                min_color_possibilities = score
                max_vertex = node
                best_coloring = colorings_neighbor

    return max_vertex, best_coloring


def _choose_suitable_vertex_fast(graph, current_solution, best_solution):
    max_neighbor_count = -1
    max_vertex = -1

    for node in graph.nodes:
        if node not in current_solution[1]:
            score = len(graph[node])
            if score > max_neighbor_count:
                max_neighbor_count = score
                max_vertex = node

    best_coloring = _get_possible_colorings(graph, max_vertex, current_solution, best_solution)
    return max_vertex, best_coloring

def _get_possible_colorings(graph, vertex, current_solution, best_solution):
    possibilities = []
    maximumInclusivePermissiblecolor = min(current_solution[0], best_solution[0] - 2)
    numberOfUnknownVertices = 0
    occupiedcolors = [False] * (len(graph[vertex]) + 1)
    for neighbor in graph[vertex]:
        if neighbor not in current_solution[1]:
            numberOfUnknownVertices += 1
        else:
            color = current_solution[1][neighbor]
            if (color < len(occupiedcolors)):
                occupiedcolors[color] = True

    colorCandidate = 0
    while colorCandidate <= maximumInclusivePermissiblecolor \
        and len(possibilities) <= numberOfUnknownVertices:
        if not occupiedcolors[colorCandidate]:
            possibilities.append(colorCandidate)
        colorCandidate += 1

    return possibilities;