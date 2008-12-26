"""
An implementation of VF2 algorithm for graph ismorphism testing.
"""

#    Copyright (C) 2007-2009 by the NetworkX maintainers
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

#    This work was originally coded by Christopher Ellison
#    as part of the Computational Mechanics Python (CMPy) project.
#    James P. Crutchfield, principal investigator.
#    Complexity Sciences Center and Physics Department, UC Davis.

indent = 4 * ' '

sources = \
"""
[1]   Luigi P. Cordella, Pasquale Foggia, Carlo Sansone, Mario Vento,
      "A (Sub)Graph Isomorphism Algorithm for Matching Large Graphs",
      IEEE Transactions on Pattern Analysis and Machine Intelligence,
      vol. 26,  no. 10,  pp. 1367-1372,  Oct.,  2004.
      http://ieeexplore.ieee.org/iel5/34/29305/01323804.pdf

[2]   L. P. Cordella, P. Foggia, C. Sansone, M. Vento, "An Improved 
      Algorithm for Matching Large Graphs", 3rd IAPR-TC15 Workshop 
      on Graph-based Representations in Pattern Recognition, Cuen, 
      pp. 149-159, 2001.
      http://amalfi.dis.unina.it/graph/db/papers/vf-algorithm.pdf
        
Modified to handle undirected graphs.
Modified to handle multiple edges.
"""

subgraph = \
"""
Graph theory literature can be ambiguious about the meaning of the
above statement, and we seek to clarify it now.

In the VF2 literature, a mapping M is said to be a graph-subgraph
isomorphism iff M is an isomorphism between G2 and a subgraph of G1.
Thus, to say that G1 and G2 are graph-subgraph isomorphic is to say
that a subgraph of G1 is isomorphic to G2.

Other literature uses the phrase 'subgraph isomorphic' as in 'G1 does
not have a subgraph isomorphic to G2'.  Another use is as an in adverb 
for isomorphic.  Thus, to say that G1 and G2 are subgraph isomorphic 
is to say that a subgraph of G1 is isomorphic to G2.

Finally, the term 'subgraph' can have multiple meanings. In this 
context, 'subgraph' always means a 'node-induced subgraph'. Edge-induced
subgraph isomorphisms are not directly supported, but one should be
able to perform the check by making use of nx.line_graph(). For 
subgraphs which are not induced, the term 'monomorphism' is preferred 
over 'isomorphism'. Currently, it is not possible to check for 
monomorphisms.
"""

subgraph_definitions = \
"""
Let G=(N,E) be a graph with a set of nodes N and set of edges E.

If G'=(N',E') is a subgraph, then:
    N' is a subset of N
    E' is a subset of E

If G'=(N',E') is a node-induced subgraph, then:
    N' is a subset of N
    E' is the subset of edges in E relating nodes in N'

If G'=(N',E') is an edge-induced subgrpah, then:
    N' is the subset of nodes in N related by edges in E'
    E' is a subset of E
"""


import sys

__date__ = "$Date$"

__doc__ += sources.replace('\n', '\n'+indent)

__all__ = ['GraphMatcher',
           'DiGraphMatcher']

class GraphMatcher(object):
    """Implementation of VF2 algorithm for matching undirected graphs.

    Suitable for nx.Graph and nx.MultiGraph instances.

    A GraphMatcher is responsible for matching undirected graphs in a 
    predetermined manner.  For graphs or multigraphs G1 and G2, this usually
    means a check for an isomorphism between them, though other checks are 
    also possible.  For example, the GraphMatcher class can check if a 
    subgraph of G1 is isomorphic to G2.
    
    Matching is done via syntactic feasibility. It is also possible to check
    for semantic feasibility. Feasibility, then, is defined as the logical AND 
    of the two functions.  
    
    To include a semantic check, the GraphMatcher class should be subclassed,
    and the semantic_feasibility() function should be redefined.  By default, 
    the semantic feasibility function always returns True.  The effect of this
    is that semantics are not considered in the matching of G1 and G2. 
    
    For more information, see the docmentation for:
      syntactic_feasibliity()
      semantic_feasibility()
    
    In general, this problem is NP-Complete.

    Examples
    --------
    Suppose G1 and G2 are isomorphic graphs. Verification is as follows:
    
    >>> G1 = nx.path_graph(4)
    >>> G2 = nx.path_graph(4)
    >>> GM = nx.GraphMatcher(G1,G2)
    >>> GM.is_isomorphic()
    True

    GM.mapping stores the isomorphism mapping from G1 to G2.

    >>> GM.mapping
    {0: 0, 1: 1, 2: 2, 3: 3}

    """
    __doc__ += "Notes\n%s-----" % (indent,) + sources.replace('\n','\n'+indent)

    def __init__(self, G1, G2):
        """Initialize GraphMatcher.
        
        G1 and G2 should be nx.Graph or nx.MultiGraph instances.

        Examples
        --------
        To create a GraphMatcher which checks for syntactic feasibility:

        >>> G1 = nx.path_graph(4)
        >>> G2 = nx.path_graph(4)
        >>> GM = nx.GraphMatcher(G1,G2)
        
        """
        self.G1 = G1
        self.G2 = G2
 
        # Set recursion limit.
        self.old_recursion_limit = sys.getrecursionlimit()
        expected_max_recursion_level = len(self.G2)
        if self.old_recursion_limit < 1.5 * expected_max_recursion_level:
            # Give some breathing room.
            sys.setrecursionlimit(int(1.5 * expected_max_recursion_level))
        
        # Declare that we will be searching for a graph-graph isomorphism.
        self.test = 'graph'

        # Initialize the isomorphism mapping.
        self.state = GMState(self)

    def __del__(self):
        # Restore the recursion limit
        sys.setrecursionlimit(self.old_recursion_limit)
                
    def candidate_pairs_iter(self):
        """Iterator over candidate pairs of nodes in G1 and G2."""

        # All computations are done using the current state!
        
        # First we compute the inout-terminal sets.
        T1_inout = [node for node in self.G1 if (node in GMState.inout_1) and (node not in GMState.core_1)]
        T2_inout = [node for node in self.G2 if (node in GMState.inout_2) and (node not in GMState.core_2)]
        
        # If T1_inout and T2_inout are both nonempty.
        # P(s) = T1_inout x {min T2_inout}
        if T1_inout and T2_inout:
            for node in T1_inout:
                yield node, min(T2_inout)
            
        else:
            # If T1_inout and T2_inout were both empty....
            # P(s) = (N_1 - M_1) x {min (N_2 - M_2)}
            if not (T1_inout or T2_inout):
                # First we determine the candidate node for G2
                other_node = min(set(self.G2) - set(GMState.core_2))
                for node in self.G1:
                    if node not in GMState.core_1:
                        yield node, other_node

        # For all other cases, we don't have any candidate pairs.        

    def is_isomorphic(self):
        """Returns True if G1 and G2 are isomorphic graphs."""

        # Declare that we are looking for a graph-graph isomorphism.
        self.test = 'graph'

        # Let's do two very quick checks!
        # QUESTION: Should we call faster_graph_could_be_isomorphic(G1,G2)?
        # For now, I just copy the code.
        
        # Check global properties
        if self.G1.order() != self.G2.order(): return False
    
        # Check local properties
        d1=self.G1.degree()
        d1.sort()
        d2=self.G2.degree()
        d2.sort()
        if d1 != d2: return False
        
        # Recall, self.match() will not return False.
        # It raises an exception or returns None
        try:
            self.match(self.state)
            return False
        except StopIteration:
            return True
        
    def match(self, state):
        """Extends the isomorphism mapping.

        This function is called recursively to determine if a complete
        isomorphism can be found between G1 and G2.  It cleans up the class
        variables after each recursive call. If an isomorphism is found,
        we raise a StopIteration and jump immediately out of the recursion.

        """
        if len(GMState.core_1) == len(self.G2):
            # Save the final mapping, otherwise garbage collection deletes it.
            self.mapping = GMState.core_1.copy()
            # The mapping is complete.
            raise StopIteration
        else:
            for G1_node, G2_node in self.candidate_pairs_iter():
                if self.syntactic_feasibility(G1_node, G2_node):
                    if self.semantic_feasibility(G1_node, G2_node):
                        # Recursive call, adding the feasible state.
                        self.match(GMState(self, G1_node, G2_node))
            # Garbage collection for GMState() will 'restore data structures'.
    
    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if adding (G1_node, G2_node) is symantically feasible.

        The semantic feasibility function should return True if it is 
        acceptable to add the candidate pair (G1_node, G2_node) to the current 
        partial isomorphism mapping.   The logic should focus on semantic
        information contained in the edge data or a formalized node class.
        
        By acceptable, we mean that the subsequent mapping can still become a 
        complete isomorphism mapping.  Thus, if adding the candidate pair 
        definitely makes it so that the subsequent mapping cannot become a 
        complete isomorphism mapping, then this function must return False.
    
        The default semantic feasibility function always returns True. The 
        effect is that semantics are not considered in the matching of G1 
        and G2.

        The semantic checks might differ based on the what type of test is 
        being performed.  A keyword description of the test is stored in
        self.test.  Here is a quick description of the currently implemented
        tests:
        
          test='graph'    
            Indicates that the graph matcher is looking for a graph-graph
            isomorphism.
          test='subgraph'
            Indicates that the graph matcher is looking for a subgraph-graph
            isomorphism such that a subgraph of G1 is isomorphic to G2.
        
        Any subclass of GraphMatcher which redefines semantic_feasibility()
        must maintain the above form to keep the match() method functional.
        Implementations should consider multigraphs.

        """
        return True
                    
    def subgraph_is_isomorphic(self):
        """Returns True if a subgraph of G1 is isomorphic to G2."""
        
        # Declare that we are looking for graph-subgraph isomorphism.
        self.test = 'subgraph'
        
        # Recall, self.match() will not return False.
        # It raises an exception or returns None
        try:
            self.match(self.state)
            return False
        except StopIteration:
            return True
    subgraph_is_isomorphic.__doc__ += "\n" + subgraph.replace('\n','\n'+indent)
        
    def syntactic_feasibility(self, G1_node, G2_node):
        """Returns True if adding (G1_node, G2_node) is syntactically feasible.

        This function returns True if it is adding the candidate pair
        to the current partial isomorphism mapping is allowable.  The addition
        is allowable if the inclusion of the candidate pair does not make it
        impossible for an isomorphism to be found.

        """
        
        # The VF2 algorithm was designed to work with graphs having, at most,
        # one edge connecting any two nodes.  This is not the case when
        # dealing with an MultiGraphs.
        # 
        # Basically, when we test the look-ahead rules R_neighbor, we will 
        # make sure that the number of edges are checked. We also add
        # a R_self check to verify that the number of selfloops is acceptable.
        #
        # Users might be comparing Graph instances with MultiGraph instances.
        # So the generic GraphMatcher class must work with MultiGraphs.
        # Care must be taken since the value in the innermost dictionary is a 
        # singlet for Graph instances.  For MultiGraphs, the value in the 
        # innermost dictionary is a list.     
        
        
        ###
        ### Test at each step to get a return value as soon as possible.
        ###
                
        
        ### Look ahead 0
        
        # R_self

        # The number of selfloops for G1_node must equal the number of 
        # self-loops for G2_node. Without this check, we would fail on 
        # R_neighbor at the next recursion level. But it is good to prune the
        # search tree now.
        if self.G1.number_of_edges(G1_node,G1_node) != self.G2.number_of_edges(G2_node,G2_node):
            return False
                
        
        # R_neighbor
        
        # For each neighbor n' of n in the partial mapping, the corresponding
        # node m' is a neighbor of m, and vice versa. Also, the number of
        # edges must be equal.
        for neighbor in self.G1[G1_node]:
            if neighbor in GMState.core_1:
                if not (GMState.core_1[neighbor] in self.G2[G2_node]):
                    return False
                elif self.G1.number_of_edges(neighbor, G1_node) != self.G2.number_of_edges(GMState.core_1[neighbor], G2_node):
                    return False
        for neighbor in self.G2[G2_node]:
            if neighbor in GMState.core_2:
                if not (GMState.core_2[neighbor] in self.G1[G1_node]):
                    return False
                elif self.G1.number_of_edges(GMState.core_2[neighbor], G1_node) != self.G2.number_of_edges(neighbor, G2_node):
                    return False
        
        ### Look ahead 1
        
        # R_terminout
        # The number of neighbors of n that are in T_1^{inout} is equal to the
        # number of neighbors of m that are in T_2^{inout}, and vice versa.
        num1 = 0
        for neighbor in self.G1[G1_node]:
            if (neighbor in GMState.inout_1) and (neighbor not in GMState.core_1):
                num1 += 1
        num2 = 0
        for neighbor in self.G2[G2_node]:
            if (neighbor in GMState.inout_2) and (neighbor not in GMState.core_2):
                num2 += 1
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False


        ### Look ahead 2

        # R_new
        
        # The number of neighbors of n that are neither in the core_1 nor
        # T_1^{inout} is equal to the number of neighbors of m 
        # that are neither in core_2 nor T_2^{inout}.
        num1 = 0
        for neighbor in self.G1[G1_node]:
            if neighbor not in GMState.inout_1:
                num1 += 1
        num2 = 0
        for neighbor in self.G2[G2_node]:
            if neighbor not in GMState.inout_2:
                num2 += 1
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False
            
        # Otherwise, this node pair is syntactically feasible!
        return True
    
    
class DiGraphMatcher(object):
    """Implementation of VF2 algorithm for matching directed graphs.

    Suitable for nx.DiGraph and nx.MultiDiGraph instances.

    A DiGraphMatcher is responsible for matching directed graphs in a 
    predetermined manner.  For directed graphs G1 and G2, this usually
    means a check for an isomorphism between them, though other checks 
    are also possible.  For example, the DiGraphMatcher class can check 
    if a subgraph of G1 is isomorphic to G2.
   
    Matching is done via syntactic feasibility. It is also possible 
    to check for semantic feasibility. Feasibility, then, is defined 
    as the logical AND of the two functions.

    To include a semantic check, the DiGraphMatcher class should be 
    subclassed, and the semantic_feasibility() function should be 
    redefined.  By default, the semantic feasibility function always 
    returns True.  The effect of this is that semantics are not 
    considered in the matching of G1 and G2. 
    
    For more information, see the docmentation for:
      syntactic_feasibliity()
      semantic_feasibility()
    
    In general, this problem is NP-Complete.

    Examples
    --------
    Suppose G1 and G2 are isomorphic graphs. Verification is as follows:
    
    >>> G1 = nx.path_graph(4, create_using=nx.DiGraph)
    >>> G2 = nx.path_graph(4, create_using=nx.DiGraph)
    >>> DiGM = nx.DiGraphMatcher(G1,G2)
    >>> DiGM.is_isomorphic()
    True

    DiGM.mapping stores the isomorphism mapping from G1 to G2.

    >>> DiGM.mapping
    {0: 0, 1: 1, 2: 2, 3: 3}
    
    """
    __doc__ += "Notes\n%s-----" % (indent,) + sources.replace('\n','\n'+indent)
              
        
    def __init__(self, G1, G2):
        """Initialize DiGraphMatcher.
        
        Examples
        --------
        To create a GraphMatcher which checks for syntactic feasibility:

        >>> G1 = nx.DiGraph(nx.path_graph(4, create_using=nx.DiGraph)
        >>> G2 = nx.DiGraph(nx.path_graph(4, create_using=nx.DiGraph)
        >>> DiGM = nx.DiGraphMatcher(G1,G2)
                
        """
        self.G1 = G1
        self.G2 = G2
 
        # Set recursion limit.
        self.old_recursion_limit = sys.getrecursionlimit()
        expected_max_recursion_level = len(self.G2)
        if self.old_recursion_limit < 1.5 * expected_max_recursion_level:
            # Give some breathing room.
            sys.setrecursionlimit(int(1.5 * expected_max_recursion_level))
        
        # Declare that we will be searching for a graph-graph isomorphism.
        self.test = 'graph'
        
        # Initialize the isomorphism mapping.
        self.state = DiGMState(self)
        
        # Provide a convienient was to access the isomorphism mapping.
        self.mapping = DiGMState.core_1
               
    def __del__(self):
        # Restore the recursion limit
        sys.setrecursionlimit(self.old_recursion_limit)
        
    def candidate_pairs_iter(self):
        """Iterator over candidate pairs of nodes in G1 and G2."""
        
        # All computations are done using the current state!
        
        # First we compute the out-terminal sets.
        T1_out = [node for node in self.G1 if (node in DiGMState.out_1) and (node not in DiGMState.core_1)]
        T2_out = [node for node in self.G2 if (node in DiGMState.out_2) and (node not in DiGMState.core_2)]
        
        # If T1_out and T2_out are both nonempty.
        # P(s) = T1_out x {min T2_out}
        if T1_out and T2_out:
            node_2 = min(T2_out)
            for node_1 in T1_out:
                yield node_1, node_2
            
        else:
            # If T1_out and T2_out were both empty....
            # We compute the in-terminal sets.
            if not (T1_out or T2_out):
                T1_in = [node for node in self.G1 if (node in DiGMState.in_1) and (node not in DiGMState.core_1)]
                T2_in = [node for node in self.G2 if (node in DiGMState.in_2) and (node not in DiGMState.core_2)]
                
                # If T1_in and T2_in are both nonempty.
                # P(s) = T1_out x {min T2_out}
                if T1_in and T2_in:
                    node_2 = min(T2_in)
                    for node_1 in T1_in:
                        yield node_1, node_2
                else:
                    # If all terminal sets are empty...
                    # P(s) = (N_1 - M_1) x {min (N_2 - M_2)}
                    if not (T1_out or T2_out or T1_in or T2_in):
                        # First we determine the candidate node for G2
                        node_2 = min(set(self.G2) - set(DiGMState.core_2))
                        for node_1 in self.G1:
                            if node_1 not in DiGMState.core_1:
                                yield node_1, node_2

        # For all other cases, we don't have any candidate pairs.        
        
    def is_isomorphic(self):
        """Returns True if G1 and G2 are isomorphic directed graphs."""

        # Declare that we are looking for a graph-graph isomorphism.
        self.test = 'graph'

        # Let's do two very quick checks!
        # QUESTION: Should we call faster_graph_could_be_isomorphic(G1,G2)?
        # For now, I just copy the code.
        
        # Check global properties
        if self.G1.order() != self.G2.order(): return False
    
        # Check local properties
        d1=self.G1.degree()
        d1.sort()
        d2=self.G2.degree()
        d2.sort()
        if d1 != d2: return False
        
        # Recall, self.match() will not return False.
        # It raises an exception or returns None
        try:
            self.match(self.state)
            return False
        except StopIteration:
            return True
        
    def match(self, state):
        """Extends the isomorphism mapping.

        This function is called recursively to determine if a complete
        isomorphism can be found between G1 and G2.  It cleans up the class
        variables after each recursive call. If an isomorphism is found,
        we raise a StopIteration and jump immediately out of the recursion.

        """
        if len(DiGMState.core_1) == len(self.G2):
            # Save the final mapping, otherwise garbage collection deletes it.
            self.mapping = DiGMState.core_1.copy()
            # The mapping is complete.
            raise StopIteration
        else:
            for G1_node, G2_node in self.candidate_pairs_iter():
                if self.syntactic_feasibility(G1_node, G2_node):
                    if self.semantic_feasibility(G1_node, G2_node):
                        # Recursive call, adding the feasible state.
                        self.match(DiGMState(self, G1_node,G2_node))
            # Garbage collection for DiGMState() will 'restore data structures'.


    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if adding (G1_node, G2_node) is symantically feasible.

        The semantic feasibility function should return True if it is 
        acceptable to add the candidate pair (G1_node, G2_node) to the current 
        partial isomorphism mapping.   The logic should focus on semantic
        information contained in the edge data or a formalized node class.
        
        By acceptable, we mean that the subsequent mapping can still become a 
        complete isomorphism mapping.  Thus, if adding the candidate pair 
        definitely makes it so that the subsequent mapping cannot become a 
        complete isomorphism mapping, then this function must return False.
    
        The default semantic feasibility function always returns True. The 
        effect is that semantics are not considered in the matching of G1 
        and G2.

        The semantic checks might differ based on the what type of test is 
        being performed.  A keyword description of the test is stored in
        self.test.  Here is a quick description of the currently implemented
        tests:
        
          test='graph'    
            Indicates that the graph matcher is looking for a graph-graph
            isomorphism.
          test='subgraph'
            Indicates that the graph matcher is looking for a subgraph-graph
            isomorphism such that a subgraph of G1 is isomorphic to G2.
        
        Any subclass of DiGraphMatcher which redefines semantic_feasibility()
        must maintain the above form to keep the match() method functional.
        Implementations should consider multigraphs.

        """
        return True
                    
    def subgraph_is_isomorphic(self):
        """Returns True if a subgraph of G1 is isomorphic to G2."""
        
        # Declare that we are looking for graph-subgraph isomorphism.
        self.test = 'subgraph'
        
        # Recall, self.match() will not return False.
        # It raises an exception or returns None
        try:
            self.match(self.state)
            return False
        except StopIteration:
            return True
    subgraph_is_isomorphic.__doc__ += "\n" + subgraph.replace('\n','\n'+indent)

    def syntactic_feasibility(self, G1_node, G2_node):
        """Returns True if adding (G1_node, G2_node) is syntactically feasible.

        This function returns True if it is adding the candidate pair
        to the current partial isomorphism mapping is allowable.  The addition
        is allowable if the inclusion of the candidate pair does not make it
        impossible for an isomorphism to be found.

        """
        
        # The VF2 algorithm was designed to work with graphs having, at most,
        # one edge connecting any two nodes.  This is not the case when
        # dealing with an MultiGraphs.
        # 
        # Basically, when we test the look-ahead rules R_pred and R_succ, we 
        # will make sure that the number of edges are checked.  We also add
        # a R_self check to verify that the number of selfloops is acceptable.
        
        # Users might be comparing DiGraph instances with MultiDiGraph 
        # instances. So the generic DiGraphMatcher class must work with 
        # MultiDiGraphs. Care must be taken since the value in the innermost 
        # dictionary is a singlet for DiGraph instances.  For MultiDiGraphs, 
        # the value in the innermost dictionary is a list.     
        
        
        ###
        ### Test at each step to get a return value as soon as possible.
        ###
        
        
        
        ### Look ahead 0
        
        # R_self
        
        # The number of selfloops for G1_node must equal the number of
        # self-loops for G2_node. Without this check, we would fail on R_pred
        # at the next recursion level. This should prune the tree even further.
        
        if self.G1.number_of_edges(G1_node,G1_node) != self.G2.number_of_edges(G2_node,G2_node):
            return False

        ### predecessors_iter, successors_iter and neighbors_iter does not 
        ### behave how we need it to. With multiedges, it returns the same
        ### node multiple times.  The result is that we do the same check
        ### repeatedly.  If NetworkX changes this behavior, we can go back to
        ### predecessors_iter (etc), but for now, we must access the underlying
        ### structure. For example, 
        ###   self.G1.pred[G1_node] 
        ### vs 
        ###   self.G1.predecessors_iter(G1_node)


        # R_pred
        
        # For each predecessor n' of n in the partial mapping, the
        # corresponding node m' is a predecessor of m, and vice versa. Also,
        # the number of edges must be equal
        for predecessor in self.G1.pred[G1_node]:
            if predecessor in DiGMState.core_1:
                if not (DiGMState.core_1[predecessor] in self.G2.pred[G2_node]):
                    return False
                elif self.G1.number_of_edges(predecessor, G1_node) != self.G2.number_of_edges(DiGMState.core_1[predecessor], G2_node):
                    return False
                
        for predecessor in self.G2.pred[G2_node]:
            if predecessor in DiGMState.core_2:
                if not (DiGMState.core_2[predecessor] in self.G1.pred[G1_node]):
                    return False
                elif self.G1.number_of_edges(DiGMState.core_2[predecessor], G1_node) != self.G2.number_of_edges(predecessor, G2_node):
                    return False


        # R_succ

        # For each successor n' of n in the partial mapping, the corresponding 
        # node m' is a successor of m, and vice versa. Also, the number of
        # edges must be equal.
        for successor in self.G1[G1_node]:
            if successor in DiGMState.core_1:
                if not (DiGMState.core_1[successor] in self.G2[G2_node]):
                    return False
                elif self.G1.number_of_edges(G1_node, successor) != self.G2.number_of_edges(G2_node, DiGMState.core_1[successor]):
                    return False
                                
        for successor in self.G2[G2_node]:
            if successor in DiGMState.core_2:
                if not (DiGMState.core_2[successor] in self.G1[G1_node]):
                    return False
                elif self.G1.number_of_edges(G1_node, DiGMState.core_2[successor]) != self.G2.number_of_edges(G2_node, successor):
                    return False

        
        ### Look ahead 1
        
        # R_termin
        # The number of predecessors of n that are in T_1^{in} is equal to the
        # number of predecessors of m that are in T_2^{in}.
        num1 = 0
        for predecessor in self.G1.pred[G1_node]:
            if (predecessor in DiGMState.in_1) and (predecessor not in DiGMState.core_1):
                num1 += 1
        num2 = 0
        for predecessor in self.G2.pred[G2_node]:
            if (predecessor in DiGMState.in_2) and (predecessor not in DiGMState.core_2):
                num2 += 1
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False

        # The number of successors of n that are in T_1^{in} is equal to the
        # number of successors of m that are in T_2^{in}.
        num1 = 0
        for successor in self.G1[G1_node]:
            if (successor in DiGMState.in_1) and (successor not in DiGMState.core_1):
                num1 += 1
        num2 = 0
        for successor in self.G2[G2_node]:
            if (successor in DiGMState.in_2) and (successor not in DiGMState.core_2):
                num2 += 1                
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False

        # R_termout
        
        # The number of predecessors of n that are in T_1^{out} is equal to the
        # number of predecessors of m that are in T_2^{out}.
        num1 = 0
        for predecessor in self.G1.pred[G1_node]:
            if (predecessor in DiGMState.out_1) and (predecessor not in DiGMState.core_1):
                num1 += 1
        num2 = 0
        for predecessor in self.G2.pred[G2_node]:
            if (predecessor in DiGMState.out_2) and (predecessor not in DiGMState.core_2):
                num2 += 1
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False

        # The number of successors of n that are in T_1^{out} is equal to the
        # number of successors of m that are in T_2^{out}.
        num1 = 0
        for successor in self.G1[G1_node]:
            if (successor in DiGMState.out_1) and (successor not in DiGMState.core_1):
                num1 += 1
        num2 = 0
        for successor in self.G2[G2_node]:
            if (successor in DiGMState.out_2) and (successor not in DiGMState.core_2):
                num2 += 1                                
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False
        
        ### Look ahead 2

        # R_new
        
        # The number of predecessors of n that are neither in the core_1 nor
        # T_1^{in} nor T_1^{out} is equal to the number of predecessors of m 
        # that are neither in core_2 nor T_2^{in} nor T_2^{out}.
        num1 = 0
        for predecessor in self.G1.pred[G1_node]:
            if (predecessor not in DiGMState.in_1) and (predecessor not in DiGMState.out_1):
                num1 += 1
        num2 = 0
        for predecessor in self.G2.pred[G2_node]:
            if (predecessor not in DiGMState.in_2) and (predecessor not in DiGMState.out_2):
                num2 += 1
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False
            
        # The number of successors of n that are neither in the core_1 nor
        # T_1^{in} nor T_1^{out} is equal to the number of successors of m 
        # that are neither in core_2 nor T_2^{in} nor T_2^{out}.
        num1 = 0
        for successor in self.G1[G1_node]:
            if (successor not in DiGMState.in_1) and (successor not in DiGMState.out_1):
                num1 += 1
        num2 = 0
        for successor in self.G2[G2_node]:
            if (successor not in DiGMState.in_2) and (successor not in DiGMState.out_2):
                num2 += 1
        if self.test == 'graph':
            if not (num1 == num2):
                return False
        else: # self.test == 'subgraph'
            if not (num1 >= num2):
                return False
        
        # Otherwise, this node pair is syntactically feasible!
        return True
    
        
class GMState(object):
    """Internal representation of state for the GraphMatcher class.

    This class is used internally by the GraphMatcher class.  It is used
    only to store state specific data. There will be at most G2.order() of
    these objects in memory at a time, due to the depth-first search
    strategy employed by the VF2 algorithm.

    """
    
    ###
    ### The following variables are class variables.
    ### So they will be shared by all instances of the GMState class.
    ### This is the improvement of the VF2 algorithm over the VF algorithm.
    ###
    
    # core_1[n] contains the index of the node paired with n, which is m,
    #           provided n is in the mapping.
    # core_2[m] contains the index of the node paired with m, which is n,
    #           provided m is in the mapping.
    core_1 = {}
    core_2 = {}
    
    # See the paper for definitions of M_x and T_x^{y}
    
    # inout_1[n]  is non-zero if n is in M_1 or in T_1^{inout}
    # inout_2[m]  is non-zero if m is in M_2 or in T_2^{inout}
    #
    # The value stored is the depth of the SSR tree when the node became
    # part of the corresponding set.
    inout_1 = {}
    inout_2 = {}
    # Practically, these sets simply store the nodes in the subgraph.
    
    def __init__(self, GM, G1_node=None, G2_node=None):
        """Initializes GMState object.
        
        Pass in the GraphMatcher to which this GMState belongs and the
        new node pair that will be added to the GraphMatcher's current
        isomorphism mapping.
        """
        # Initialize the last stored node pair.
        self.G1_node = None
        self.G2_node = None
        self.depth = len(GMState.core_1)
      
        # Watch out! G1_node == 0 should evaluate to True.
        if G1_node is not None and G2_node is not None:
            # Add the node pair to the isomorphism mapping.
            GMState.core_1[G1_node] = G2_node
            GMState.core_2[G2_node] = G1_node

            # Store the node that was added last.
            self.G1_node = G1_node
            self.G2_node = G2_node
            
            # Now we must update the other two vectors.
            # We will add only if it is not in there already!
            self.depth = len(GMState.core_1)
            
            # First we add the new nodes...
            if G1_node not in GMState.inout_1:
                GMState.inout_1[G1_node] = self.depth
            if G2_node not in GMState.inout_2:
                    GMState.inout_2[G2_node] = self.depth
                    
            # Now we add every other node...
            
            # Updates for T_1^{inout}
            new_nodes = set([])
            for node in GMState.core_1:
                new_nodes.update([neighbor for neighbor in GM.G1[node] if neighbor not in GMState.core_1])
            for node in new_nodes:
                if node not in GMState.inout_1:
                    GMState.inout_1[node] = self.depth

            # Updates for T_2^{inout}
            new_nodes = set([])
            for node in GMState.core_2:
                new_nodes.update([neighbor for neighbor in GM.G2[node] if neighbor not in GMState.core_2])
            for node in new_nodes:
                if node not in GMState.inout_2:
                    GMState.inout_2[node] = self.depth
                
    def __del__(self):
        """Deletes the GMState object and restores the class variables."""
        
        # First we remove the node that was added from the core vectors.
        # Watch out! G1_node == 0 should evaluate to True.
        if self.G1_node is not None and self.G2_node is not None:
            del GMState.core_1[self.G1_node]
            del GMState.core_2[self.G2_node]

        # Now we revert the other two vectors.        
        # Thus, we delete all entries which have this depth level.
        for vector in (GMState.inout_1, GMState.inout_2):
            for node in vector.keys():
                if vector[node] == self.depth:
                    del vector[node]
                    
    

class DiGMState(object):
    """Internal representation of state for the DiGraphMatcher class.

    This class is used internally by the DiGraphMatcher class.  It is used
    only to store state specific data. There will be at most G2.order() of
    these objects in memory at a time, due to the depth-first search
    strategy employed by the VF2 algorithm.

    """
    
    ###
    ### The following variables are class variables.
    ### So they will be shared by all instances of the DiGMState class.
    ### This is the improvement of the VF2 algorithm over the VF algorithm.
    ###
    
    # core_1[n] contains the index of the node paired with n, which is m,
    #           provided n is in the mapping.
    # core_2[m] contains the index of the node paired with m, which is n,
    #           provided m is in the mapping.
    core_1 = {}
    core_2 = {}
    
    # See the paper for definitions of M_x and T_x^{y}
    
    # in_1[n]  is non-zero if n is in M_1 or in T_1^{in}
    # out_1[n] is non-zero if n is in M_1 or in T_1^{out}
    #
    # in_2[m]  is non-zero if m is in M_2 or in T_2^{in}
    # out_2[m] is non-zero if m is in M_2 or in T_2^{out}
    #
    # The value stored is the depth of the search tree when the node became
    # part of the corresponding set.
    in_1 = {}
    in_2 = {}
    out_1 = {}
    out_2 = {}
    
    def __init__(self, DiGM, G1_node=None, G2_node=None):
        """Initializes DiGMState object.
        
        Pass in the DiGraphMatcher to which this DiGMState belongs and the
        new node pair that will be added to the GraphMatcher's current
        isomorphism mapping.
        """
        # Initialize the last stored node pair.
        self.G1_node = None
        self.G2_node = None
        self.depth = len(DiGMState.core_1)
      
        # Watch out! G1_node == 0 should evaluate to True.
        if G1_node is not None and G2_node is not None:
            # Add the node pair to the isomorphism mapping.
            DiGMState.core_1[G1_node] = G2_node
            DiGMState.core_2[G2_node] = G1_node
            
            # Store the node that was added last.
            self.G1_node = G1_node
            self.G2_node = G2_node
            
            # Now we must update the other four vectors.
            # We will add only if it is not in there already!
            self.depth = len(DiGMState.core_1)
            
            # First we add the new nodes...
            for vector in (DiGMState.in_1, DiGMState.out_1):
                if G1_node not in vector:
                    vector[G1_node] = self.depth
            for vector in (DiGMState.in_2, DiGMState.out_2):
                if G2_node not in vector:
                    vector[G2_node] = self.depth
                    
            # Now we add every other node...
            
            # Updates for T_1^{in}
            new_nodes = set([])
            for node in DiGMState.core_1:
                new_nodes.update([predecessor for predecessor in DiGM.G1.predecessors(node) if predecessor not in DiGMState.core_1])
            for node in new_nodes:
                if node not in DiGMState.in_1:
                    DiGMState.in_1[node] = self.depth
                
            # Updates for T_2^{in}
            new_nodes = set([])
            for node in DiGMState.core_2:
                new_nodes.update([predecessor for predecessor in DiGM.G2.predecessors(node) if predecessor not in DiGMState.core_2])
            for node in new_nodes:
                if node not in DiGMState.in_2:
                    DiGMState.in_2[node] = self.depth
                
            # Updates for T_1^{out}
            new_nodes = set([])        
            for node in DiGMState.core_1:
                new_nodes.update([successor for successor in DiGM.G1.successors(node) if successor not in DiGMState.core_1])
            for node in new_nodes:
                if node not in DiGMState.out_1:                
                    DiGMState.out_1[node] = self.depth
    
            # Updates for T_2^{out}
            new_nodes = set([])        
            for node in DiGMState.core_2:
                new_nodes.update([successor for successor in DiGM.G2.successors(node) if successor not in DiGMState.core_2])
            for node in new_nodes:
                if node not in DiGMState.out_2:
                    DiGMState.out_2[node] = self.depth

    def __del__(self):
        """Deletes the DiGMState object and restores the class variables."""
        
        # First we remove the node that was added from the core vectors.
        # Watch out! G1_node == 0 should evaluate to True.
        if self.G1_node is not None and self.G2_node is not None:
            del DiGMState.core_1[self.G1_node]
            del DiGMState.core_2[self.G2_node]

        # Now we revert the other four vectors.        
        # Thus, we delete all entries which have this depth level.
        for vector in (DiGMState.in_1, DiGMState.in_2, DiGMState.out_1, DiGMState.out_2):
            for node in vector.keys():
                if vector[node] == self.depth:
                    del vector[node]
                    
