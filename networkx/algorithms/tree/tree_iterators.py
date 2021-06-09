from enum import Enum
from queue import PriorityQueue
from dataclasses import dataclass, field
import networkx as nx


class EdgePartition(Enum):
    OPEN = 0
    INCLUDED = 1
    EXCLUDED = 2


class ArborescenceIterator:
    """
    This iterator will successively return spanning arborescences of the input
    graph in order of minimum weight to maximum weight.
    This is an implementation of an algorithm published by Sörensen and Janssens
    and published in the 2005 paper An Algorithm to Generate all Spanning Trees
    of a Graph in Order of Increasing Cost which can be accessed at
    https://www.scielo.br/j/pope/a/XHswBwRwJyrfL88dmMwYNWp/?lang=en
    """

    def __init__(self, G, partition="partition"):
        """
        Initialize the iterator
        Parameters
        ----------
        G : nx.DiGraph
            The directed graph which we need to iterate arborescences over
        partition : String, default = "partition"
            The edge attribute used to store the partition data. This only needs
            to be changed if the graph already has data in the default key.
        """
        self.graph = G.copy()
        self.partition_key = partition

    def __iter__(self):
        """
        Returns
        -------
        ArborescenceIterator
            The iterator object for this graph
        """
        # TODO Create the first partition in the partition list
        # How do I want to represent the partitions?
        # If the partitions are represented as a tuple in an ordered list,
        # the tuple would have the format (MST cost, {partition}) where the
        # partition is represented as a dict with edge tuples from DiGraph.edges
        # mapped to a partition status, probably an ENUM.
        #
        # When we need to find the minimum spanning arborescence for the
        # partition we will update the partition stored in the graph and then
        # call Edmonds' algorithm on it.
        pass

    def __next__(self):
        """
        Returns
        -------
        (multi)DiGraph
            The spanning arborescence of next greatest weight, which ties broken
            arbitrarily.
        """
        pass

    def partition(self):
        """
        Create new partitions based of the minimum spanning arborescence of the
        current minimum partition.
        """
        pass

    def check_partition(self):
        """
        Check that the partition is not empty.
        An empty partition for a directed graph would be any partition in which
        their is at least one node which is disconnected or contains multiple
        included edges.
        Returns
        -------
        bool
            True if the partition is acceptable and false otherwise.
        """
        pass

    def write_partition(self, partition):
        """
        Writes the desired partition into the graph to calculate the minimum
        spanning arborescence.
        Parameters
        ----------
        partition : tuple
            A tuple describing a partition of the format partition. The first
            element is the cost of the minimum spanning arborescence for the
            partition followed by a dict in which edges are mapped to an enum
            describing how that edge is in the partition.
        """
        pass

    def clear_partition(self):
        """
        Removes partition data from the graph
        """
        for e in self.graph.edges:
            del e[self.partition()]

    def __del__(self):
        """
        Delete the copy of the graph
        """
        del self.graph


class SpanningTreeIterator:
    """
    This iterator will successively return spanning trees of the input
    graph in order of minimum weight to maximum weight.
    This is an implementation of an algorithm published by Sörensen and Janssens
    and published in the 2005 paper An Algorithm to Generate all Spanning Trees
    of a Graph in Order of Increasing Cost which can be accessed at
    https://www.scielo.br/j/pope/a/XHswBwRwJyrfL88dmMwYNWp/?lang=en
    """

    @dataclass(order=True)
    class Partition:
        """
        This dataclass represents a partition and stores a dict with the edge
        data and the weight of the minimum spanning tree with the partitions
        are stored using
        """

        mst_weight: int
        partition_dict: dict = field(compare=False)

        def __copy__(self):
            return SpanningTreeIterator.Partition(
                self.mst_weight, self.partition_dict.copy()
            )

    def __init__(self, G, weight="weight", partition="partition"):
        """
        Initialize the iterator
        Parameters
        ----------
        G : nx.Graph
            The directed graph which we need to iterate trees over
        weight : String, default = "weight"
            The edge attribute used to store the weight of the edge
        partition : String, default = "partition"
            The edge attribute used to store the partition data. This only needs
            to be changed if the graph already has data in the default key.
        """
        self.G = G.copy()
        self.weight = weight
        self.partition_key = partition

    def __iter__(self):
        """
        Returns
        -------
        TreeIterator
            The iterator object for this graph
        """
        # TODO Create the first partition in the partition list
        # How do I want to represent the partitions?
        # If the partitions are represented as a tuple in an ordered list,
        # the tuple would have the format (MST cost, {partition}) where the
        # partition is represented as a dict with edge tuples from DiGraph.edges
        # mapped to a partition status, probably an ENUM.
        #
        # When we need to find the minimum spanning tree for the
        # partition we will update the partition stored in the graph and then
        # call a modified Kruskal's algorithm on it.
        self.partition_queue = PriorityQueue()
        self.partition_queue.put(
            self.Partition(
                nx.minimum_spanning_tree(self.G).size(weight=self.weight), dict()
            )
        )

        return self

    def __next__(self):
        """
        Returns
        -------
        (multi)Graph
            The spanning tree of next greatest weight, which ties broken
            arbitrarily.
        """
        if self.partition_queue.empty():
            raise StopIteration

        partition = self.partition_queue.get()
        self.write_partition(partition)
        next_tree = nx.partition_minimum_spanning_tree(
            self.G, self.weight, self.partition_key
        )
        self.partition(partition, next_tree)

        self.clear_partition(next_tree)
        return next_tree

    def partition(self, partition, partition_tree):
        """
        Create new partitions based of the minimum spanning tree of the
        current minimum partition.

        Parameters
        ----------
        partition : Partition
        partition_tree : nx.Graph
        """
        # create two new partitions with the data from the input partition dict
        p1 = self.Partition(-1, partition.partition_dict.copy())
        p2 = self.Partition(-1, partition.partition_dict.copy())
        for e in partition_tree.edges:
            # determine if the edge was open or included
            if e not in partition.partition_dict:
                # This is an open edge
                p1.partition_dict[e] = EdgePartition.EXCLUDED
                p2.partition_dict[e] = EdgePartition.INCLUDED

                self.write_partition(p1)
                p1_mst = nx.partition_minimum_spanning_tree(
                    self.G, self.weight, self.partition_key
                )
                if nx.is_connected(p1_mst):
                    p1.mst_weight = p1_mst.size(weight=self.weight)
                    self.partition_queue.put(p1.__copy__())
                p1.partition_dict = p2.partition_dict.copy()

    def write_partition(self, partition):
        """
        Writes the desired partition into the graph to calculate the minimum
        spanning tree.

        Parameters
        ----------
        partition : Partition
            A Partition dataclass describing a partition on the edges of the
            graph.
        """
        for u, v, d in self.G.edges(data=True):
            if (u, v) in partition.partition_dict:
                d[self.partition_key] = partition.partition_dict[(u, v)]
            else:
                d[self.partition_key] = EdgePartition.OPEN

    def clear_partition(self, G):
        """
        Removes partition data from the graph
        """
        for u, v, d in G.edges(data=True):
            if self.partition_key in d:
                del d[self.partition_key]

    def __del__(self):
        """
        Delete the copy of the graph
        """
        del self.G
