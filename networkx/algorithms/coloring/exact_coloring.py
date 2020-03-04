"""
Exact graph coloring.
"""

import networkx as nx
import sys

__all__ = ['backGCP']

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

def backGCP(graph, upper_bound_on_number_of_steps: int, alpha_ratio: float):
    """Color a graph using the minimum number of colours.
    
    Finds an exact colouring of the given graph.
    If the graph is not connected, the algorithm recursively colours
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
    # solution = (colourCount, vertexToColour)
    dummy_solution = (custom_infinity, {})
    initial_solution = (0, {node: -1 for node in graph.nodes})

    # TODO: check if sorting is really needed

    vertex_to_color = _recurse(graph, initial_solution, dummy_solution, upper_bound_on_number_of_steps, alpha_ratio)
    return vertex_to_color

def _recurse(graph, currentSolution, bestSolution, upperBoundOnNumberOfSteps, alphaRatio):
    if upperBoundOnNumberOfSteps != -1 and bestSolution.colourCount < custom_infinity:
        if upperBoundOnNumberOfSteps == 0:
            return bestSolution
        else:
            upperBoundOnNumberOfSteps -= 1
    if currentSolution.solvedCount < len(graph):
    
        # choose a vertex to colour
        vertexToColour = 0
        colouringPossibilities = []
        if len(graph) - currentSolution.solvedCount < 0:
            vertexToColour, colouringPossibilities = _choose_suitable_vertex_fast(graph, currentSolution, bestSolution)
        else:
            vertexToColour, colouringPossibilities = _choose_suitable_vertex(graph, currentSolution, bestSolution)

        # for in possible colours
        for colour in colouringPossibilities:
            increasedColourCount = False
            if colour >= currentSolution.colourCount:
                if colour > currentSolution.colourCount:
                    raise Exception("New color is too large")
                currentSolution.colourCount += 1
                increasedColourCount = True
            if currentSolution.colourCount * alphaRatio < bestSolution.colourCount:
                currentSolution.vertexToColour[vertexToColour] = colour
                currentSolution.solvedCount += 1

                # recurse and update best statistics
                bestSolution, upperBoundOnNumberOfSteps = _recurse(graph, currentSolution, bestSolution, alphaRatio)

                currentSolution.solvedCount -= 1
                currentSolution.vertexToColour[vertexToColour] = -1
            if increasedColourCount:
                currentSolution.colourCount -= 1
    
    else:
        # no more vertices to colour
        # if the solution is indeed better...
        if currentSolution.colourCount >= bestSolution.colourCount:
            raise Exception("Proposed solution is not better")
        # warning! there may be vertices with negative colourings!
        bestSolution = currentSolution.DeepClone()

    return bestSolution, upperBoundOnNumberOfSteps

    # may return -1 if there is no suitable vertex
def _choose_suitable_vertex(graph, currentSolution, bestSolution):
    minColourPossibilities = custom_infinity
    maxNeighbourCount = -1
    maxVertex = -1
    bestColouring = None

    for i in range(graph.nodes):
        if currentSolution.vertexToColour[i] == -1:
            colouringsNeighbour = _get_possible_colorings(graph, i, currentSolution, bestSolution)
            if colouringsNeighbour.Count == 0:
                bestColouring = colouringsNeighbour
                return i
            score = colouringsNeighbour.Count
            if colouringsNeighbour[colouringsNeighbour.Count - 1] == currentSolution.colourCount:
                score += custom_infinity / 2
            if score < minColourPossibilities or (score == minColourPossibilities and len(graph[i]) > maxNeighbourCount):
                maxNeighbourCount = len(graph[i])
                minColourPossibilities = score
                maxVertex = i
                bestColouring = colouringsNeighbour

    return maxVertex


def _choose_suitable_vertex_fast(graph, currentSolution, bestSolution):
    maxNeighbourCount = -1
    maxVertex = -1

    for i in range(len(graph.nodes)):
        if (currentSolution.vertexToColour[i] == -1):
            score = len(graph[i])
            if score > maxNeighbourCount:
                maxNeighbourCount = score
                maxVertex = i

    bestColouring = _get_possible_colorings(graph, maxVertex, currentSolution, bestSolution)
    return maxVertex, bestColouring

def _get_possible_colorings(neighbor_count, vertex, current_solution, best_solution):
    possibilities = []
    maximumInclusivePermissibleColour = min(currentSolution.colourCount, bestSolution.colourCount - 2)
    numberOfUnknownVertices = 0
    occupiedColours = [False] * (len(graph[vertex]) + 1)
    for neighbour in graph[vertex]:
        colour = currentSolution.vertexToColour[neighbour]
        if (colour == -1):
            numberOfUnknownVertices += 1
        elif (colour < len(occupiedColours)):
            occupiedColours[colour] = True

    colourCandidate = 0;
    while colourCandidate <= maximumInclusivePermissibleColour \
        and possibilities.Count <= numberOfUnknownVertices:
        if not occupiedColours[colourCandidate]:
            possibilities.Add(colourCandidate)
        colourCandidate += 1

    return possibilities;