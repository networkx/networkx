# -*- coding: utf-8 -*-
"""Functions for computing treewidth decomposition.
   
   Treewidth of an undirected graph is a number associated with the graph. It can be defined as the size of the largest vertex set (bag) in a tree decomposition of the graph minus one. 

`Wikipedia: Treewidth <https://en.wikipedia.org/wiki/Treewidth>`_

   The notions of treewidth and tree decomposition have gained their attractiveness partly because many graph and network problems that are intractable (e.g., NP-hard) on arbitrary graphs become efficiently solvable (e.g., with a linear time algorithm) when the treewidth of the input graphs is bounded by a constant.

    Hans L. Bodlaender and Arie M. C. A. Koster. 2010. "Treewidth computations I.Upper bounds". Inf. Comput. 208, 3 (March 2010),259-275. DOI=http://dx.doi.org/10.1016/j.ic.2009.03.008 

    Hand L. Bodlaender. "Discovering Treewidth". institute of information and computing sciences, utrecht university. technical report UU-CS-2005-018. www.cs.uu.nl

"""
import sys

import networkx as nx
from networkx.utils import not_implemented_for
from heapq import heappush, heappop, heapify

__all__ = ["treewidth_decomposition1_min_fill_in",
            "treewidth_decomposition1_min_degree",
            "treewidth_decomposition2_min_degree",
            "treewidth_decomposition2_min_fill_in",
            "treewidth_decomposition3_min_degree",
            "treewidth_decomposition3_min_fill_in",
            "treewidth_decomposition4_min_degree",
            "treewidth_decomposition4_min_fill_in",
            "treewidth_decomposition5",
            "min_fill_in_heuristic",
            "min_degree_heuristic"]


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def treewidth_min_degree(G):
    """ Returns a treewidth decomposition using the Minimum Degree heuristic.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    Treewidth decomposition : (int, Graph) tuple
          2-tuple with treewidth and the corresponding decomposed tree (NetworkX graph).
    """
    return treewidth_decomp(G, MinDegreeHeuristic)


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def treewidth_min_fill_in(G):
    """ Returns a treewidth decomposition using the Minimum Fill-in heuristic.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    Treewidth decomposition : (int, Graph) tuple
        2-tuple with treewidth and the corresponding decomposed tree (NetworkX graph).
    """
    return treewidth_decomp(G, MinFillInHeuristic)


class MinDegreeHeuristic:
    # TODO: Update documentation
    def __init__(self, graph):
        self._graph = graph

        # A collection of nodes that have to be updated in the heap before each iteration
        self._update_nodes = []

        # self._degreeq is heapq with 2-tuples (degree,node)
        self._degreeq = []
        # build heap with initial degrees
        for n in graph:
            self._degreeq.append((len(graph[n]), n))
        heapify(self._degreeq)

    def __iter__(self):
        return self

    def next(self):
        """Implement next method for backwards compatibility with python 2"""
        return self.__next__()

    def __next__(self):
        # Update nodes in self._update_nodes
        for n in self._update_nodes:
            # insert changed degrees into degreeq
            heappush(self._degreeq, (len(self._graph[n]), n))

        while self._degreeq:
            # get the next (minimum degree) node
            (min_degree, elim_node) = heappop(self._degreeq)
            if elim_node not in self._graph or len(self._graph[elim_node]) != min_degree:
                # Outdated entry in degreeq
                continue
            elif min_degree == len(self._graph) - 1:
                # Fully connected: Abort condition
                raise StopIteration

            # Remember to update nodes in the heap before getting the next node
            self._update_nodes = self._graph[elim_node]
            return elim_node

        # The heap is empty: Abort
        raise StopIteration


class MinFillInHeuristic:
    """Returns the node from the graph, where the number of edges added  when
    turning the neighbourhood of the chosen node into clique is small as possible.
    Parameters
    ----------
    G : Graph
    Returns
    -------
    min_fill_node : string, integers or hashable Python object (except None)
        The node from the graph, for which, when it is deleted from the graph and
        its neighbourhood is turned into clique, the number of edges added is
        small as possible.
    Notes
    -----
    This algorithm computes the node with 'min fill in' in the graph 'G'.
    The running time of the algorithm is O(V*V*V) and it uses constant
    additional memory.
    References
    ----------
    .. [1] K. Wang, Z. Lu, and J. Hicks
           *Treewidth*.
           http://web.eecs.utk.edu/~cphillip/cs594_spring2015_projects/treewidth.pdf
    """
    #TODO: Update documentation
    def __init__(self, graph):
        self._graph = graph

    def __iter__(self):
        return self

    def next(self):
        """Implement next method for backwards compatibility with python 2"""
        return self.__next__()

    def __next__(self):
        if len(self._graph) == 0:
            raise StopIteration

        min_fill_in_node = None

        min_fill_in = sys.maxsize

        # create sorted list of (degree, node)
        degree_list = [(len(self._graph[node]), node) for node in self._graph]
        degree_list.sort()

        # abort condition
        min_degree = degree_list[0][0]
        if min_degree == len(self._graph) - 1:
            raise StopIteration

        for (degree, node) in degree_list:
            num_fill_in = 0
            # Convert to list in order to access by index
            nbrs = list(self._graph[node])
            for i in range(len(nbrs) - 1):
                for j in range(i + 1, len(nbrs)):
                    if nbrs[j] not in self._graph[nbrs[i]]:
                        num_fill_in += 1
                        # break inner loop if this can't be min-fill-in node anymore
                        if num_fill_in >= min_fill_in:
                            break

                if num_fill_in >= min_fill_in: # break outer loop
                    break

            if num_fill_in < min_fill_in: # Update min-fill-in node
                if num_fill_in == 0:
                    return node
                min_fill_in = num_fill_in
                min_fill_in_node = node

        return min_fill_in_node

def min_fill_in_heuristic1(G):
    """Returns the node from the graph, where the number of edges added  when
    turning the neighbourhood of the chosen node into clique is small as possible.
    Parameters
    ----------
    G : Graph
    Returns
    -------
    min_fill_node : string, integers or hashable Python object (except None)
        The node from the graph, for which, when it is deleted from the graph and
        its neighbourhood is turned into clique, the number of edges added is
        small as possible.
    Notes
    -----
    This algorithm computes the node with 'min fill in' in the graph 'G'.
    The running time of the algorithm is O(V*V*V) and it uses constant
    additional memory.
    References
    ----------
    .. [1] K. Wang, Z. Lu, and J. Hicks
           *Treewidth*.
           http://web.eecs.utk.edu/~cphillip/cs594_spring2015_projects/treewidth.pdf
    """

    if len(G) == 0:
        return None

    min_fill_in_node = None

    min_fill_in = sys.maxsize

    # create sorted list of (degree, node)
    degree_list = [(len(G[node]), node) for node in G]
    degree_list.sort()

    # abort condition
    min_degree = degree_list[0][0]
    if min_degree == len(G) - 1:
        return None

    for (degree, node) in degree_list:
        min_degree = min(min_degree, degree)
        num_fill_in = 0
        # Convert to list in order to access by index
        neighbors = list(G[node])
        for i in range(len(neighbors) - 1):
            for j in range(i + 1, len(neighbors)):
                if not neighbors[j] in G[neighbors[i]]:
                    num_fill_in += 1
                    # prune if this can't be min-fill-in node anymore
                    if num_fill_in >= min_fill_in:
                        break
            else:
                continue # executed if no break
            break

        if num_fill_in < min_fill_in:
            if num_fill_in == 0:
                return node
            min_fill_in = num_fill_in
            min_fill_in_node = node

    return min_fill_in_node


def treewidth_decomposition1_min_fill_in(G):
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v: # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # Maps a node n to a lists of nodes l
    # Later when bag(n) is created every bag(node in l) might need to connect to bag(n)
    old_bag_notify = {}

    elim_node = min_fill_in_heuristic1(graph)
    while elim_node is not None:
        # Connect all neighbours with each other
        neighbors = graph[elim_node]
        for n in neighbors:
            for m in neighbors:
                if n != m and not m in graph[n]:
                    graph[n].add(m)
                    graph[m].add(n)

        node_stack.append((elim_node, neighbors))

        # BAGSEARCH: Some neighbor will create the bag that elim_node later needs to connect to
        for node in neighbors:
            if node in old_bag_notify:
                old_bag_notify[node].append(elim_node)
            else:
                old_bag_notify[node] = [elim_node]

        # remove node from graph and push on stack (including its neighbors)
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        graph.pop(elim_node, None)

        # get next node to be removed according to heuristic
        elim_node = min_fill_in_heuristic1(graph)

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    # Maps node n to the bag to which bag(n) needs to connect
    old_bag_connection = {}
    for node in G.nodes:
        old_bag_connection[node] = first_bag

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in (or default to the first created bag)
        if curr_node in old_bag_connection:
            old_bag = old_bag_connection[curr_node]
        else:
            old_bag = first_bag

        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)

        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # If this node was the first in a created clique to get deleted the created bag is the old_bag from this node
        if curr_node in old_bag_notify:
            for old_neighbor_node in old_bag_notify[curr_node]:
                # set (possibly override) the bag of old_neighbor_node should connect to
                old_bag_connection[old_neighbor_node] = new_bag

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)
    
    return treewidth, decomp

def treewidth_decomposition1_min_degree(G):
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v: # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # Maps a node n to a lists of nodes l
    # Later when bag(n) is created every bag(node in l) might need to connect to bag(n)
    old_bag_notify = {}

    push = heappush
    pop = heappop
    # degreeq is heapq with 2-tuples (degree,node)
    degreeq = []

    # build heap with initial degrees
    for n in graph:
        degreeq.append((len(graph[n]), n))
    heapify(degreeq)

    while degreeq:
        # get the next (minimum degree) node
        (min_degree, elim_node) = pop(degreeq)
        if not elim_node in graph or len(graph[elim_node]) != min_degree:
            # Outdated entry in degreeq
            continue
        elif min_degree == len(graph) - 1:
            # Fully connected: Abort condition
            break

        # Connect all neighbours with each other
        neighbors = graph[elim_node]
        changed_degree = neighbors
        for n in neighbors:
            for m in neighbors:
                if n != m and not m in graph[n]:
                    graph[n].add(m)
                    graph[m].add(n)

        # remove node from graph and push on stack (including its neighbors)
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        graph.pop(elim_node, None)

        node_stack.append((elim_node, neighbors))

        # BAGSEARCH: Some neighbor will create the bag that elim_node later needs to connect to
        for node in neighbors:
            if node in old_bag_notify:
                old_bag_notify[node].append(elim_node)
            else:
                old_bag_notify[node] = [elim_node]

        # insert changed degrees into degreeq
        for n in changed_degree:
            push(degreeq, (len(graph[n]), n))

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    # Maps node n to the bag to which bag(n) needs to connect
    old_bag_connection = {}
    for node in G.nodes:
        old_bag_connection[node] = first_bag

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in (or default to the first created bag)
        if curr_node in old_bag_connection:
            old_bag = old_bag_connection[curr_node]
        else:
            old_bag = first_bag

        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # If this node was the first in a created clique to get deleted the created bag is the old_bag from this node
        if curr_node in old_bag_notify:
            for old_neighbor_node in old_bag_notify[curr_node]:
                # set (possibly override) the bag of old_neighbor_node should connect to
                old_bag_connection[old_neighbor_node] = new_bag

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)

    return treewidth, decomp


def treewidth_decomposition2_min_degree(G):
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v:  # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    push = heappush
    pop = heappop
    # degreeq is heapq with 2-tuples (degree,node)
    degreeq = []

    # build heap with initial degrees
    for n in graph:
        degreeq.append((len(graph[n]), n))
    heapify(degreeq)

    while degreeq:
        # get the next (minimum degree) node
        (min_degree, elim_node) = pop(degreeq)
        if not elim_node in graph or len(graph[elim_node]) != min_degree:
            # Outdated entry in degreeq
            continue
        elif min_degree == len(graph) - 1:
            # Fully connected: Abort condition
            break

        # Connect all neighbours with each other
        neighbors = graph[elim_node]
        changed_degree = neighbors
        for n in neighbors:
            for m in neighbors:
                if n != m and not m in graph[n]:
                    graph[n].add(m)
                    graph[m].add(n)

        # remove node from graph and push on stack (including its neighbors)
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        graph.pop(elim_node, None)

        node_stack.append((elim_node, neighbors))

        # insert changed degrees into degreeq
        for n in changed_degree:
            push(degreeq, (len(graph[n]), n))

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in
        old_bag = None
        for bag in decomp.nodes:
            if neighbors <= bag:
                old_bag = bag
                break

        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)
    
    return treewidth, decomp

def treewidth_decomposition2_min_fill_in(G):
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v:  # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    elim_node = min_fill_in_heuristic1(graph)
    while elim_node is not None:

        # Connect all neighbours with each other
        neighbors = graph[elim_node]
        for n in neighbors:
            for m in neighbors:
                if n != m and not m in graph[n]:
                    graph[n].add(m)
                    graph[m].add(n)

        # remove node from graph and push on stack (including its neighbors)
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        graph.pop(elim_node, None)

        node_stack.append((elim_node, neighbors))

        # get next node to be removed according to heuristic
        elim_node = min_fill_in_heuristic1(graph)

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1


    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()
        # find a bag the neighbors are in
        old_bag = None
        for bag in decomp.nodes:
            if neighbors <= bag:
                old_bag = bag
                break
        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)
    
    return treewidth, decomp

def min_degree_heuristic3(G):
    min_degree = sys.maxsize
    min_node = None
    for node in G:
        degree = len(G[node])
        if degree < min_degree:
            if degree <= 1:
                # Return early
                return node
            min_node = node
            min_degree = degree

    if min_degree == len(G) - 1:
        # Fully connected: Abort condition
        return None
    else:
        return min_node

def treewidth_decomposition3_min_degree(G):
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v: # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # Maps a node n to a lists of nodes l
    # Later when bag(n) is created every bag(node in l) might need to connect to bag(n)
    old_bag_notify = {}


    elim_node = min_degree_heuristic3(graph)
    while elim_node is not None:

        # Connect all neighbours with each other
        neighbors = graph[elim_node]
        for n in neighbors:
            for m in neighbors:
                if n != m and not m in graph[n]:
                    graph[n].add(m)
                    graph[m].add(n)

        # remove node from graph and push on stack (including its neighbors)
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        graph.pop(elim_node, None)

        node_stack.append((elim_node, neighbors))

        # BAGSEARCH: Some neighbor will create the bag that elim_node later needs to connect to
        for node in neighbors:
            if node in old_bag_notify:
                old_bag_notify[node].append(elim_node)
            else:
                old_bag_notify[node] = [elim_node]

        # get next node to be removed according to heuristic
        elim_node = min_degree_heuristic3(graph)


    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    # Maps node n to the bag to which bag(n) needs to connect
    old_bag_connection = {}
    for node in graph:
        old_bag_connection[node] = first_bag

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in (or default to the first created bag)
        if curr_node in old_bag_connection:
            old_bag = old_bag_connection[curr_node]
        else:
            old_bag = first_bag

        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # If this node was the first in a created clique to get deleted the created bag is the old_bag from this node
        if curr_node in old_bag_notify:
            for old_neighbor_node in old_bag_notify[curr_node]:
                # set (possibly override) the bag of old_neighbor_node should connect to
                old_bag_connection[old_neighbor_node] = new_bag

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)

    return treewidth, decomp

    

def min_fill_in_heuristic3(G):
    """Returns the node from the graph, where the number of edges added  when
    turning the neighbourhood of the chosen node into clique is small as possible.
    Parameters
    ----------
    G : Graph
    Returns
    -------
    min_fill_node : string, integers or hashable Python object (except None)
        The node from the graph, for which, when it is deleted from the graph and
        its neighbourhood is turned into clique, the number of edges added is
        small as possible.
    Notes
    -----
    This algorithm computes the node with 'min fill in' in the graph 'G'.
    The running time of the algorithm is O(V*V*V) and it uses constant
    additional memory.
    References
    ----------
    .. [1] K. Wang, Z. Lu, and J. Hicks
           *Treewidth*.
           http://web.eecs.utk.edu/~cphillip/cs594_spring2015_projects/treewidth.pdf
    """

    candidate_node = None
    # Still keep track of min_degree to abort earlier
    min_degree = sys.maxsize
    min_fill_in = sys.maxsize

    for node in G:
        degree = len(G[node])
        min_degree = min(min_degree, degree)
        num_fill_in = 0
        # Convert to list in order to access by index
        neighbors = list(G[node])
        for i in range(len(neighbors) - 1):
            for j in range(i + 1, len(neighbors)):
                if neighbors[j] not in G[neighbors[i]]:
                    num_fill_in += 1

        if num_fill_in < min_fill_in:
            if num_fill_in == 0:
                return node
            min_fill_in = num_fill_in
            candidate_node = node

    if min_degree == len(G) - 1:
        # Fully connected: Abort condition
        return None
    else:
        return candidate_node

def treewidth_decomposition3_min_fill_in(G):
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v: # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # Maps a node n to a lists of nodes l
    # Later when bag(n) is created every bag(node in l) might need to connect to bag(n)
    old_bag_notify = {}

    elim_node = min_fill_in_heuristic3(graph)
    while elim_node is not None:

        # Connect all neighbours with each other
        neighbors = graph[elim_node]
        for n in neighbors:
            for m in neighbors:
                if n != m and not m in graph[n]:
                    graph[n].add(m)
                    graph[m].add(n)


        node_stack.append((elim_node, neighbors))

        # BAGSEARCH: Some neighbor will create the bag that elim_node later needs to connect to
        for node in neighbors:
            if node in old_bag_notify:
                old_bag_notify[node].append(elim_node)
            else:
                old_bag_notify[node] = [elim_node]

        # remove node from graph and push on stack (including its neighbors)
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        graph.pop(elim_node, None)

        # get next node to be removed according to heuristic
        elim_node = min_fill_in_heuristic3(graph)

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    # Maps node n to the bag to which bag(n) needs to connect
    old_bag_connection = {}
    for node in G.nodes:
        old_bag_connection[node] = first_bag

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in (or default to the first created bag)
        if curr_node in old_bag_connection:
            old_bag = old_bag_connection[curr_node]
        else:
            old_bag = first_bag

        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # If this node was the first in a created clique to get deleted the created bag is the old_bag from this node
        if curr_node in old_bag_notify:
            for old_neighbor_node in old_bag_notify[curr_node]:
                # set (possibly override) the bag of old_neighbor_node should connect to
                old_bag_connection[old_neighbor_node] = new_bag

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)
    
    return treewidth, decomp

def treewidth_decomposition4_min_degree(G):
    # Johannes Bagsearch / Priority queue (min_deg) / Normal Graph
    G = G.copy()

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # Maps a node n to a lists of nodes l
    # Later when bag(n) is created every bag(node in l) might need to connect to bag(n)
    old_bag_notify = {}

    push = heappush
    pop = heappop
    # degreeq is heapq with 2-tuples (degree,node)
    degreeq = []

    # build heap with initial degrees
    for (n, degree) in G.degree:
        degreeq.append((degree, n))
    heapify(degreeq)

    while degreeq:
        # get the next (minimum degree) node
        (min_degree, elim_node) = pop(degreeq)
        if not G.has_node(elim_node) or G.degree[elim_node] != min_degree:
            # Outdated entry in degreeq
            continue
        elif min_degree == G.number_of_nodes() - 1:
            # Fully connected: Abort condition
            break

        # Connect all neighbours with each other
        neighbors = set(G.neighbors(elim_node))
        changed_degree = set(G.neighbors(elim_node))
        for n in neighbors:
            for m in neighbors:
                if (n != m) and not G.has_edge(n, m):
                    G.add_edge(n, m)

        # Some neighbor will create the bag that elim_node later needs to connect to
        for node in neighbors:
            if node in old_bag_notify:
                old_bag_notify[node].append(elim_node)
            else:
                old_bag_notify[node] = [elim_node]

        # remove node from graph and push on stack (including its neighbors)
        G.remove_node(elim_node)
        node_stack.append((elim_node, neighbors))

        # insert changed degrees into degreeq
        for n in changed_degree:
            push(degreeq, (G.degree[n], n))

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(G.nodes)
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    # Maps node n to the bag to which bag(n) needs to connect
    old_bag_connection = {}
    for node in G.nodes:
        old_bag_connection[node] = first_bag

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in (or default to the first created bag)
        if curr_node in old_bag_connection:
            old_bag = old_bag_connection[curr_node]
        else:
            old_bag = first_bag

        # Create new node for decomposition
        neighbors.add(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # If this node was the first in a created clique to get deleted the created bag is the old_bag from this node
        if curr_node in old_bag_notify:
            for old_neighbor_node in old_bag_notify[curr_node]:
                # set (possibly override) the bag of old_neighbor_node should connect to
                old_bag_connection[old_neighbor_node] = new_bag

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)

    return treewidth, decomp

def treewidth_decomposition4_min_fill_in(G):
    # Copy graph because the algorithm modifies it
    G = G.copy()
    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # Maps a node n to a lists of nodes l
    # Later when bag(n) is created every bag(node in l) might need to connect to bag(n)
    old_bag_notify = {}

    elim_node = min_fill_in_heuristic1(G)
    while elim_node is not None:

        # Connect all neighbours with each other
        neighbors = list(G[elim_node])
        for i, node_1 in enumerate(neighbors[:-1]):  # Iterate neighbors excluding last element
            for node_2 in neighbors[i + 1:]:  # Iterate neighbors after node_1
                if not G.has_edge(node_1, node_2):
                    G.add_edge(node_1, node_2)

        # Some neighbor will create the bag that elim_node later needs to connect to
        for node in neighbors:
            if node in old_bag_notify:
                old_bag_notify[node].append(elim_node)
            else:
                old_bag_notify[node] = [elim_node]

        # remove node from graph and push on stack (including its neighbors)
        G.remove_node(elim_node)
        node_stack.append((elim_node, neighbors))

        # get next node to be removed according to heuristic
        elim_node = min_fill_in_heuristic1(G)

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(G.nodes)
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    # Maps node n to the bag to which bag(n) needs to connect
    old_bag_connection = {}
    for node in G.nodes:
        old_bag_connection[node] = first_bag

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, neighbors) = node_stack.pop()

        # find a bag the neighbors are in (or default to the first created bag)
        if curr_node in old_bag_connection:
            old_bag = old_bag_connection[curr_node]
        else:
            old_bag = first_bag

        # Create new node for decomposition
        neighbors.append(curr_node)
        new_bag = frozenset(neighbors)
        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # If this node was the first in a created clique to get deleted the created bag is the old_bag from this node
        if curr_node in old_bag_notify:
            for old_neighbor_node in old_bag_notify[curr_node]:
                # set (possibly override) the bag of old_neighbor_node should connect to
                old_bag_connection[old_neighbor_node] = new_bag

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)
    
    return treewidth, decomp

def treewidth_decomp(G, heuristic_class):
    """Returns a treewidth decomposition using the passed heuristic.

    Parameters
    ----------
    G : NetworkX graph
    heuristic_class : iterator class

    Returns
    -------
    Treewidth decomposition : (int, Graph) tuple
        2-tuple with treewidth and the corresponding decomposed tree (NetworkX graph).
    """
    # TODO: Update documentation regarding heuristic_class
    # make dict-of-sets structure
    graph = {}
    for u in G:
        graph[u] = set()
        for v in G[u]:
            if u != v:  # ignore self-loop
                graph[u].add(v)

    # stack where nodes and their neighbors are pushed in the order they are selected by the heuristic
    node_stack = []

    # instantiate a heuristic_iterator
    heuristic_iterator = heuristic_class(graph)

    for elim_node in heuristic_iterator:
        # Connect all neighbours with each other
        nbrs = graph[elim_node]
        for u in nbrs:
            for v in nbrs:
                if u != v and v not in graph[u]:
                    graph[u].add(v)

        # push node and its current neighbors on stack
        node_stack.append((elim_node, nbrs))

        # remove node from graph
        for u in graph:
            if elim_node in graph[u]:
                graph[u].remove(elim_node)
        del graph[elim_node]

    # The abort condition is met. Put all nodes into one bag.
    decomp = nx.Graph()
    first_bag = frozenset(graph.keys())
    decomp.add_node(first_bag)

    treewidth = len(first_bag) - 1

    while node_stack:
        # get node and its neighbors from the stack
        (curr_node, nbrs) = node_stack.pop()

        # find a bag the neighbors are in
        old_bag = None
        for bag in decomp.nodes:
            if nbrs <= bag:
                old_bag = bag
                break
        if old_bag == None:
            # no old_bag was found: just connect to the first_bag
            old_bag = first_bag

        # Create new node for decomposition
        nbrs.add(curr_node)
        new_bag = frozenset(nbrs)

        # Update treewidth
        treewidth = max(treewidth, len(new_bag) - 1)

        # Add edge to decomposition (implicitly also adds the new node)
        decomp.add_edge(old_bag, new_bag)

    return treewidth, decomp
