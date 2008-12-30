"""
    VF2 implementations for weighted graphs.
"""

from copy import copy

import networkx as nx
import networkx.algorithms.isomorphism.isomorphvf2 as vf2

def is_weighted_isomorphic(G1, G2, rtol, atol):
    """Returns True if the weighted graphs G1 and G2 are isomorphic.

    Parameters
    ----------
    G1, G2 : NetworkX graph instances
       The two graphs G1 and G2 must be the same type.
    rtol : float, optional
        The relative tolerance used to compare weights.
    atol : float, optional
        The absolute tolerance used to compare weights.
       
    Notes
    -----
    Uses the vf2 algorithm.
    Works for Graph, DiGraph, MultiGraph, and MultiDiGraph

    See Also
    --------
    isomorphvf2

    """

    # The thought was that is_isomorphic() could check if the graphs
    # were weighted and if so, call this function.  So the assertions
    # below are not meant to be useful to the user.  If this function
    # is being called as it is intended, these additional one-time checks
    # will pass unnoticed.

    assert(G1.weighted and G2.weighted)
    
    if not G1.directed and not G1.multigraph:
        assert(not G2.directed and not G2.multigraph)
        gm = WeightedGraphMatcher(G1,G2,rtol,atol)
    elif not G1.directed and G1.multigraph:
        assert(not G2.directed and G2.multigraph)
        gm = WeightedMultiGraphMatcher(G1,G2,rtol,atol)
    elif G1.directed and not G1.multigraph:
        assert(G2.directed and not G2.multigraph)
        gm = WeightedDiGraphMatcher(G1,G2,rtol,atol)
    else:
        assert(G2.directed and G2.multigraph)
        gm = WeightedMultiDiGraphMatcher(G1,G2,rtol,atol)

    return gm.is_isomorphic()  

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


class WeightedGraphMatcher(nx.GraphMatcher):
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
        nx.GraphMatcher.__init__(self, G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""
        G1_adj = self.G1.adj
        G2_adj = self.G2.adj
        core_1 = vf2.GMState.core_1
        rtol, atol = self.rtol, self.atol
        for neighbor in G1_adj[G1_node]:
            if neighbor is G1_node:
                if not close(G1_adj[G1_node][G1_node],
                             G2_adj[G2_node][G2_node],  
                             rtol, atol):
                    return False
            elif neighbor in core_1:
                if not close(G1_adj[G1_node][neighbor], 
                             G2_adj[G2_node][core_1[neighbor]],
                             rtol, atol):
                    return False
        # syntactic check has already verified that neighbors are symmetric

        return True
           

class WeightedDiGraphMatcher(nx.DiGraphMatcher):
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
        nx.DiGraphMatcher.__init__(self, G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""
        G1_succ = self.G1.succ
        G1_pred = self.G1.pred
        G2_succ = self.G2.succ
        G2_pred = self.G2.pred
        core_1 = vf2.DiGMState.core_1
        rtol, atol = self.rtol, self.atol

        for successor in G1_succ[G1_node]:
            if successor is G1_node:
                if not close(G1_succ[G1_node][G1_node],
                             G2_succ[G2_node][G2_node],  
                             rtol, atol):
                    return False
            elif successor in core_1:
                if not close(G1_succ[G1_node][successor], 
                             G2_succ[G2_node][core_1[successor]],
                             rtol, atol):
                    return False
        # syntactic check has already verified that successors are symmetric

        for predecessor in G1_pred[G1_node]:
            if predecessor is G1_node:
                if not close(G1_pred[G1_node][G1_node],
                             G2_pred[G2_node][G2_node],  
                             rtol, atol):
                    return False
            elif predecessor in core_1:
                if not close(G1_pred[G1_node][predecessor], 
                             G2_pred[G2_node][core_1[predecessor]],
                             rtol, atol):
                  return False
        # syntactic check has already verified that predecessors are symmetric

        return True


class WeightedMultiGraphMatcher(nx.GraphMatcher):
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
        nx.GraphMatcher.__init__(self, G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        G1_adj = self.G1.adj
        G2_adj = self.G2.adj
        core_1 = vf2.GMState.core_1
        rtol, atol = self.rtol, self.atol

        for neighbor in G1_adj[G1_node]:
            if neighbor is G1_node:
                data1 = copy(G1_adj[G1_node][G1_node])
                data2 = copy(G2_adj[G2_node][G2_node])
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
            elif neighbor in core_1:
                data1 = copy(G1_adj[G1_node][neighbor])
                data2 = copy(G2_adj[G2_node][core_1[neighbor]])
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
        # syntactic check has already verified that neighbors are symmetric

        return True

class WeightedMultiDiGraphMatcher(nx.DiGraphMatcher):
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
        nx.DiGraphMatcher.__init__(self, G1, G2)

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if mapping G1_node to G2_node is semantically feasible."""
        G1_succ = self.G1.succ
        G1_pred = self.G1.pred
        G2_succ = self.G2.succ
        G2_pred = self.G2.pred
        core_1 = vf2.DiGMState.core_1
        rtol, atol = self.rtol, self.atol

        for successor in G1_succ[G1_node]:
            if successor is G1_node:
                data1 = copy(G1_succ[G1_node][G1_node])
                data2 = copy(G2_succ[G2_node][G2_node])
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
            elif successor in core_1:
                data1 = copy(G1_succ[G1_node][successor])
                data2 = copy(G2_succ[G2_node][core_1[successor]])
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
        # syntactic check has already verified that successors are symmetric

        for predecessor in G1_pred[G1_node]:
            if predecessor is G1_node:
                data1 = copy(G1_pred[G1_node][G1_node])
                data2 = copy(G2_pred[G2_node][G2_node])
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
            elif predecessor in core_1:
                data1 = copy(G1_pred[G1_node][predecessor])
                data2 = copy(G2_pred[G2_node][core_1[predecessor]])
                data1.sort()
                data2.sort()
                for x,y in zip(data1,data2):
                    if not close(x,y,rtol,atol): return False
        # syntactic check has already verified that predecessors are symmetric

        return True

