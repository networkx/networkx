# -*- coding: utf-8 -*-
"""Functions for computing treewidth decomposition.
   
Treewidth of an undirected graph is a number associated with the graph.
It can be defined as the size of the largest vertex set (bag) in a tree
decomposition of the graph minus one.

`Wikipedia: Treewidth <https://en.wikipedia.org/wiki/Treewidth>`_

The notions of treewidth and tree decomposition have gained their
attractiveness partly because many graph and network problems that are
intractable (e.g., NP-hard) on arbitrary graphs become efficiently
solvable (e.g., with a linear time algorithm) when the treewidth of the
input graphs is bounded by a constant [1]_ [2]_.

There are two classes which contain implementations of different heuristics for
computing tree decomposition: :class:`MinDegreeHeuristic` and 
:class:`MinFillInHeuristic`.
   
:class:`MinDegreeHeuristic`
    Returns a treewidth decomposition using the Minimum Degree heuristic.
    The heuristic chooses the nodes according to their degree
    (number of neighours), i.e., first the node with the lowest degree is
    chosen, then the graph is updated and the correspondig node is
    removed. Next, a new node with the lowest degree is chosen,
    and so on.
   
        
:class:`MinFillInHeuristic`
    Returns the node from the graph, where the number of edges added  when
    turning the neighbourhood of the chosen node into clique is as small as
    possible. This algorithm chooses the nodes using the Minimum Fill-In
    heuristic. The running time of the algorithm is :math:`O(V^3)` and it uses
    additional constant memory [3]_.
       
   
.. [1] Hans L. Bodlaender and Arie M. C. A. Koster. 2010. "Treewidth computations
      I.Upper bounds". Inf. Comput. 208, 3 (March 2010),259-275.
      http://dx.doi.org/10.1016/j.ic.2009.03.008

.. [2] Hand L. Bodlaender. "Discovering Treewidth". Institute of Information and
      Computing Sciences, Utrecht University. Technical Report UU-CS-2005-018.
      http://www.cs.uu.nl
   
.. [3] K. Wang, Z. Lu, and J. Hicks *Treewidth*.
      http://web.eecs.utk.edu/~cphillip/cs594_spring2015_projects/treewidth.pdf

"""

import sys

import networkx as nx
from networkx.utils import not_implemented_for
from heapq import heappush, heappop, heapify

__all__ = ["treewidth_min_degree", "treewidth_min_fill_in"]


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def treewidth_min_degree(G):
    """ Returns a treewidth decomposition using the Minimum Degree heuristic. The
        heuristic chooses the nodes according to their degree, i.e., first the node
        with the lowest degree is chosen, then the graph is updated and the correspondig
        node is removed. Next, a new node with the lowest degree is chosen, and so on.

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
    """ Returns a treewidth decomposition using the Minimum Fill-in heuristic. The
    heuristic chooses a node from the graph, where the number of edges added when
    turning the neighbourhood of the chosen node into clique is small as possible.

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
        #Implement next method for backwards compatibility with python 2.
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

    def __init__(self, graph):
        self._graph = graph

    def __iter__(self):
        return self

    def next(self):
        #Implement next method for backwards compatibility with python 2.
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

        for (_, node) in degree_list:
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
