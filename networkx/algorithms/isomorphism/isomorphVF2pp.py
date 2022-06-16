"""
***************
VF2++ Algorithm
***************

Implementation of the VF2++ algorithm for the Graph Isomorphism problem.
"""

import sys


class GraphMatcher:
    """Implementation of the VF2++ algorithm, for matching undirected graphs.
    """

    def __init__(self, G1, G2, check_labels=False):
        self.G1 = G1
        self.G2 = G2
        self.V1 = set(G1.nodes())
        self.V2 = set(G2.nodes())

        if not check_labels:
            self.G1_labels = None
            self.G2_labels = None
        else:
            self.G1_labels = dict()
            self.G2_labels = dict()
            # todo: create a dictionary to map every node to its label, in both Graphs.
