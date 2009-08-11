"""
    VF2 implementations for weighted graphs.
"""

from copy import copy

import networkx as nx
from networkx.algorithms.isomorphism.isomorphvf2 \
    import GraphMatcher,DiGraphMatcher,GMState,DiGMState


__all__ = ['WeightedGraphMatcher',
           'WeightedDiGraphMatcher',
           'WeightedMultiGraphMatcher',
           'WeightedMultiDiGraphMatcher']

## VF2 is a recursive algorithm, so the call/lookup overhead is already high.
## Each implementation needs to be as fast as possible.
##
## Within the semantic feasibility function, we provide local variables
## Also, we don't want the function checking if the graph is a multigraph 
## or if it is directed each time it is called. So we provide separate
## implementations.


def close(x, y, rtol, atol):
    """Returns True if x and y are sufficiently close.

    Parameters
    ----------
    rtol
        The relative tolerance.
    atol
        The absolute tolerance.
    
    """
    # assumes finite weights
    return abs(x-y) <= atol + rtol * abs(y)


class WeightedGraphMatcher(GraphMatcher):
    """Implementation of VF2 algorithm for undirected, weighted graphs."""
    def __init__(self, G1, G2, rtol=1e-6, atol=1e-9):
        """Initialize WeightedGraphMatcher.

        Parameters
        ----------
        G1, G2 : nx.Graph instances
            G1 and G2 must be weighted graphs.
        rtol : float, optional
            The relative tolerance used to compare weights.
        atol : float, optional
            The absolute tolerance used to compare weights.

        """
        self.rtol = rtol
        self.atol = atol
        super(WeightedGraphMatcher, self).__init__(G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""
        G1_adj = self.G1.adj
        G2_adj = self.G2.adj
        core_1 = self.core_1
        rtol, atol = self.rtol, self.atol
        for neighbor in G1_adj[G1_node]:
            if neighbor is G1_node:
                if not close(G1_adj[G1_node][G1_node].get('weight',1),
                             G2_adj[G2_node][G2_node].get('weight',1),  
                             rtol, atol):
                    return False
            elif neighbor in core_1:
                if not close(G1_adj[G1_node][neighbor].get('weight',1), 
                             G2_adj[G2_node][core_1[neighbor]].get('weight',1),
                             rtol, atol):
                    return False
        # syntactic check has already verified that neighbors are symmetric

        return True
           

class WeightedDiGraphMatcher(DiGraphMatcher):
    """Implementation of VF2 algorithm for directed, weighted graphs."""
    def __init__(self, G1, G2, rtol=1e-6, atol=1e-9):
        """Initialize WeightedGraphMatcher.

        Parameters
        ----------
        G1, G2 : nx.DiGraph instances
            G1 and G2 must be weighted graphs.
        rtol : float, optional
            The relative tolerance used to compare weights.
        atol : float, optional
            The absolute tolerance used to compare weights.

        """
        self.rtol = rtol
        self.atol = atol
        super(WeightedDiGraphMatcher, self).__init__(G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""
        G1_succ = self.G1.succ
        G1_pred = self.G1.pred
        G2_succ = self.G2.succ
        G2_pred = self.G2.pred
        core_1 = self.core_1
        rtol, atol = self.rtol, self.atol

        for successor in G1_succ[G1_node]:
            if successor is G1_node:
                if not close(G1_succ[G1_node][G1_node].get('weight',1),
                             G2_succ[G2_node][G2_node].get('weight',1),  
                             rtol, atol):
                    return False
            elif successor in core_1:
                if not close(G1_succ[G1_node][successor].get('weight',1), 
                             G2_succ[G2_node][core_1[successor]].get('weight',1),
                             rtol, atol):
                    return False
        # syntactic check has already verified that successors are symmetric

        for predecessor in G1_pred[G1_node]:
            if predecessor is G1_node:
                if not close(G1_pred[G1_node][G1_node].get('weight',1),
                             G2_pred[G2_node][G2_node].get('weight',1),  
                             rtol, atol):
                    return False
            elif predecessor in core_1:
                if not close(G1_pred[G1_node][predecessor].get('weight',1), 
                             G2_pred[G2_node][core_1[predecessor]].get('weight',1),
                             rtol, atol):
                  return False
        # syntactic check has already verified that predecessors are symmetric

        return True


class WeightedMultiGraphMatcher(GraphMatcher):
    """Implementation of VF2 algorithm for undirected, weighted multigraphs."""
    def __init__(self, G1, G2, rtol=1e-6, atol=1e-9):
        """Initialize WeightedGraphMatcher.

        Parameters
        ----------
        G1, G2 : nx.MultiGraph instances
            G1 and G2 must be weighted graphs.
        rtol : float, optional
            The relative tolerance used to compare weights.
        atol : float, optional
            The absolute tolerance used to compare weights.

        """
        self.rtol = rtol
        self.atol = atol
        super(WeightedMultiGraphMatcher, self).__init__(G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        G1_adj = self.G1.adj
        G2_adj = self.G2.adj
        core_1 = self.core_1
        rtol, atol = self.rtol, self.atol

        for neighbor in G1_adj[G1_node]:
            if neighbor is G1_node:
                data1 = [d.get('weight',1) 
                         for k,d in G1_adj[G1_node][G1_node].items()]
                data2 = [d.get('weight',1) 
                         for k,d in G2_adj[G2_node][G2_node].items()]
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
            elif neighbor in core_1:
                data1 = [d.get('weight',1) 
                         for k,d in G1_adj[G1_node][neighbor].items()]
                data2 = [d.get('weight',1) 
                         for k,d in G2_adj[G2_node][core_1[neighbor]].items()]
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
        # syntactic check has already verified that neighbors are symmetric

        return True

class WeightedMultiDiGraphMatcher(DiGraphMatcher):
    """Implementation of VF2 algorithm for directed, weighted multigraphs."""
    def __init__(self, G1, G2, rtol=1e-6, atol=1e-9):
        """Initialize WeightedGraphMatcher.

        Parameters
        ----------
        G1, G2 : nx.MultiDiGraph instances
            G1 and G2 must be weighted graphs.
        rtol : float, optional
            The relative tolerance used to compare weights.
        atol : float, optional
            The absolute tolerance used to compare weights.

        """
        self.rtol = rtol
        self.atol = atol
        super(WeightedMultiDiGraphMatcher, self).__init__(G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""
        G1_succ = self.G1.succ
        G1_pred = self.G1.pred
        G2_succ = self.G2.succ
        G2_pred = self.G2.pred
        core_1 = self.core_1
        rtol, atol = self.rtol, self.atol

        for successor in G1_succ[G1_node]:
            if successor is G1_node:
                data1 = [d.get('weight',1) 
                         for k,d in G1_succ[G1_node][G1_node].items()]
                data2 = [d.get('weight',1) 
                         for k,d in G2_succ[G2_node][G2_node].items()]

                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
            elif successor in core_1:
                data1 = [d.get('weight',1) 
                         for k,d in G1_succ[G1_node][successor].items()]
                data2 = [d.get('weight',1) 
                         for k,d in G2_succ[G2_node][core_1[successor]].items()]

                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
        # syntactic check has already verified that successors are symmetric

        for predecessor in G1_pred[G1_node]:
            if predecessor is G1_node:
                data1 = [d.get('weight',1) 
                         for k,d in G1_pred[G1_node][G1_node].items()]
                data2 = [d.get('weight',1) 
                         for k,d in G2_pred[G2_node][G2_node].items()]

                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
            elif predecessor in core_1:
                data1 = [d.get('weight',1) 
                         for k,d in G1_pred[G1_node][predecessor].items()]
                data2 = [d.get('weight',1) 
                         for k,d in G2_pred[G2_node][core_1[predecessor]].items()]

                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
        # syntactic check has already verified that predecessors are symmetric

        return True

