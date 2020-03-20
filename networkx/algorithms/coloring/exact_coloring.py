"""
Exact graph coloring.
"""


import networkx as nx
from typing import Dict, List, TypeVar


T = TypeVar('T')


__all__ = ['exact_color']


class Solution():
    """Stores a node-color mapping.

    Attributes
    ----------
    used_colors : int
        Total number of unique colors used in the node-color mapping.
    color_mapping : Dict[Any, int]
        Partial mapping between graph nodes and integers representing colors.
    """

    def __init__(self, used_colors: int, color_mapping: Dict[T, int]):
        self.used_colors = used_colors
        self.color_mapping = color_mapping

    def copy(self):
        """Clones the contents into a new solution and returns it."""
        return Solution(
            self.used_colors,
            self.color_mapping.copy()
        )

    @staticmethod
    def initial():
        """This initial empty solution indicates that no nodes are colored."""
        return Solution(0, {})

    @staticmethod
    def dummy():
        """This dummy solution will always be replaced by the algorithm."""
        return Solution(float('inf'), {})


def exact_color(graph: nx.Graph) -> Dict[T, int]:
    """Color a graph using the minimum number of colors.

    Finds an exact coloring of the given graph.
    If the graph is not connected, the algorithm recursively colors
    all connected components separately.

    A valid coloring maps each node to a color in a way so that adjacent nodes
    are mapped to different colors.
    Exact coloring is a valid coloring that uses minimum number of
    unique colors. The problem is NP-Complete thus the algorithm relies on
    backtracking approach to find the coloring.

    The algorithm is known as backGCP, described in [1]_.

    The following implementation has a custom-engineered heuristic, optimized
    for random graphs.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    ----------
    Dict[Any, int]
        Mapping between graph nodes and integers representing colors

    References
    ----------
    .. [1] Zhaoyang Zhou, Chu-Min Li, Chong Huang, Ruchu Xu:
           An exact algorithm with learning for the graph coloring problem.
           Computers & Operations Research. Volume 51, November 2014,
           Pages 282-301.
           https://home.mis.u-picardie.fr/~cli/color6COR2014publishedVersion.pdf

    Examples
    ----------
    >>> import networkx as nx
    >>> graph = nx.generators.small.petersen_graph()
    >>> node_to_color_mapping = nx.coloring.exact_color(graph)
    >>> node_to_color_mapping
    {0: 0, 1: 1, 2: 0, 3: 1, 4: 2, 5: 1, 8: 0, 6: 2, 9: 0, 7: 2}
    >>> chromatic_number = len(set(node_to_color_mapping.values()))
    >>> chromatic_number
    3
    """

    # Color mapping for an empty graph
    if len(graph) == 0:
        return {}

    if nx.is_connected(graph):
        initial_solution = Solution.initial()
        dummy_solution = Solution.dummy()
        best_solution = _recurse(graph, initial_solution, dummy_solution)
        return best_solution.color_mapping
    else:
        connected_components = nx.connected_components(graph)
        color_mapping = dict()

        for connected_component in connected_components:
            initial_solution = Solution.initial()
            dummy_solution = Solution.dummy()
            best_solution = _recurse(
                                graph.subgraph(connected_component),
                                initial_solution,
                                dummy_solution
                                )
            # Amend the partial solution
            color_mapping = {**color_mapping, **best_solution.color_mapping}

        return color_mapping


def _recurse(
        graph: nx.Graph,
        partial_solution: Solution,
        best_solution: Solution
        ) -> Solution:
    """Finds best solution given partial coloring and best coloring found so far.

    Parameters
    ----------
    graph : NetworkX graph
    partial_solution : Solution
        Partial coloring: some of the nodes are already mapped to colors.
    best_solution : Solution
        Best solution found so far. Allows for efficient branch pruning.

    Returns
    ----------
    Solution
        Best solution found when taking into account partial mapping provided
        in the `partial_solution` variable. If the best solution found so far
        cannot be improved given partial matching, the algorithm simply
        returns `best_solution` parameter.
    """

    # There are sill nodes to color
    if len(partial_solution.color_mapping) < len(graph):
        node_to_color, usable_colors = _choose_branching_node(
                                            graph,
                                            partial_solution, 
                                            best_solution
                                            )

        if usable_colors is not None:
            for color in usable_colors:
                increased_color_count = False

                # Increase the number of used colors
                if color >= partial_solution.used_colors:
                    partial_solution.used_colors += 1
                    increased_color_count = True

                # Best solution could improve while iterating so this
                # comparison actually improves pruning unnecessary branches
                if partial_solution.used_colors < best_solution.used_colors:
                    partial_solution.color_mapping[node_to_color] = color
                    best_solution = _recurse(
                                        graph,
                                        partial_solution,
                                        best_solution
                                        )
                    del partial_solution.color_mapping[node_to_color]

                # Efficiently revert the partial solution
                if increased_color_count:
                    partial_solution.used_colors -= 1
    else:
        # All of the nodes are already colored
        # Clone the current solution since it is the best solution found so far
        best_solution = partial_solution.copy()

    return best_solution


def _choose_branching_node(
        graph: nx.Graph,
        partial_solution: Solution,
        best_solution: Solution
        ) -> T:
    """A heuristic that finds the best node for the algorithm to branch on.

    Parameters
    ----------
    graph : NetworkX graph
    partial_solution : Solution
        Partial coloring: some of the nodes are already mapped to colors.
    best_solution : Solution
        Best solution found so far. Allows for efficient branch pruning.

    Returns
    ----------
    Tuple[Union[None, int], Union[None, List[int]]]
        First tuple element: best node to branch on or no node at all
        indicating that the partial coloring cannot lead to a better solution
        than the one provided in the `best_solution` parameter.
        Second tuple element: valid colors for the specified node.
        The heuristic returns as few unique colors as possible while ensuring
        that the optimal solution will always be found.
    """

    # Store information about the most promising node
    best_usable_colors_count = 0
    best_neighbor_count = -1
    best_node = None
    best_occupied_colors = None

    for node in graph.nodes:
        # Make sure the node is not colored
        if node not in partial_solution.color_mapping:
            usable_colors = _get_usable_colorings(
                                graph,
                                node,
                                partial_solution,
                                best_solution
                                )

            # Cannot color a node, return immediately
            if len(usable_colors) == 0:
                return None, None

            usable_colors_count = len(usable_colors)
            neighbor_count = len(graph[node])

            # Promote nodes that do not increase the number of used colors
            definitely_replace = best_occupied_colors is None \
                or (usable_colors[-1] < partial_solution.used_colors
                    and best_occupied_colors[-1] == partial_solution.used_colors)

            # Disallow replacing solutions that increase the number of colors
            allow_replace = definitely_replace \
                or not (usable_colors[-1] == partial_solution.used_colors
                        and best_occupied_colors[-1] < partial_solution.used_colors)

            # Promote nodes that lead to less branching, in case of a tie,
            # choose the node with the largest number of neighbors
            found_better_node = definitely_replace \
                or (allow_replace \
                    and (usable_colors_count < best_usable_colors_count
                            or (usable_colors_count == best_usable_colors_count
                                and neighbor_count > best_neighbor_count)))

            if found_better_node:
                best_neighbor_count = neighbor_count
                best_usable_colors_count = usable_colors_count
                best_node = node
                best_occupied_colors = usable_colors

    return best_node, best_occupied_colors


def _get_usable_colorings(
        graph: nx.Graph,
        node: T,
        partial_solution: Solution,
        best_solution: Solution
        ) -> List[int]:
    """A heuristic finding as few unique colors as possible to color the node.

    Ensures that the optimal solution will be found if all colors are
    exhaustively tried out on the specified node.

    Parameters
    ----------
    graph : NetworkX graph
    node : int
        Node for which usable colors are to be determined.
    partial_solution : Solution
        Partial coloring: some of the nodes are already mapped to colors.
    best_solution : Solution
        Best solution found so far. Allows for efficient branch pruning.

    Returns
    ----------
    List[int]
        A list of usable colors for the specified node.
    """

    usable_colors = []
    # There can be at most 1 new color
    # It should be less that current optimum
    maximum_inclusive_permissible_color = min(
                                            partial_solution.used_colors,
                                            best_solution.used_colors - 2
                                            )
    uncolored_neighbors = 0
    occupied_colors = [False] * (len(graph[node]) + 1)

    for neighbor in graph[node]:
        if neighbor not in partial_solution.color_mapping:
            uncolored_neighbors += 1
        else:
            color = partial_solution.color_mapping[neighbor]
            if (color < len(occupied_colors)):
                occupied_colors[color] = True

    color = 0
    # Key heuristic: limit the number of used colors as much as possible
    while color <= maximum_inclusive_permissible_color \
            and len(usable_colors) <= uncolored_neighbors:
        if not occupied_colors[color]:
            usable_colors.append(color)
        color += 1

    return usable_colors
