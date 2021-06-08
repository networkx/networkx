from enum import Enum
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

    def __init__(self, G, partition="partition"):
        """
        Initialize the iterator
        Parameters
        ----------
        G : nx.Graph
            The directed graph which we need to iterate trees over
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
        # When we need to find the minimum spanning arborescence for the
        # partition we will update the partition stored in the graph and then
        # call Edmonds' algorithm on it.
        pass

    def __next__(self):
        """
        Returns
        -------
        (multi)Graph
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
        An empty partition for an undirected graph would be any partition in
        which their is at least one node which is disconnected.
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
            element is the cost of the minimum spanning tree for the partition
            followed by a dict in which edges are mapped to an enum describing
            how that edge is in the partition.
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
