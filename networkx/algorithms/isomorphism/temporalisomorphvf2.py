# -*- coding: utf-8 -*-
"""
*****************************
Time-respecting VF2 Algorithm
*****************************

An extension of the VF2 algorithm for time-respecting graph ismorphism testing in temporal graphs.

A temporal graph is one in which edges contain a datetime attribute, denoting when interaction occurred between the incident nodes. A time-respecting subgraph of a temporal graph is a subgraph such that all interactions incident to a node occurred within a time threshold, delta, of each other. A directed time-respecting subgraph has the added constraint that incoming interactions to a node must precede outgoing interactions from the same node - this enforces a sense of directed flow.

Introduction
------------

The TimeRespectingGraphMatcher and TimeRespectingDiGraphMatcher extend the GraphMatcher and DiGraphMatcher classes, respectively, to include temporal constraints on matches. This is achieved through a semantic check, via the semantic_feasibility() function.

As well as including G1 (the graph in which to seek embeddings) and G2 (the subgraph structure of interest), the name of the temporal attribute on the edges and the time threshold, delta, must be supplied as arguments to the matching constructors.

A delta of zero is the strictest temporal constraint on the match - only embeddings in which all interactions occur at the same time will be returned. A delta of one day will allow embeddings in which adjacent interactions occur up to a day apart.

Examples
--------

Examples will be provided when the datetime type has been incorporated.


Temporal Subgraph Isomorphism
-----------------------------

A brief discussion of the somewhat diverse current literature will be included here.

References
----------

[1] Redmond, U. and Cunningham, P. Temporal subgraph isomorphism. In: The 2013 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining (ASONAM). Niagara Falls, Canada; 2013: pages 1451 - 1452. [65]

[2] Redmond, U. and Cunningham, P. A temporal network analysis reveals the unprofitability of arbitrage in The Prosper Marketplace. In: Expert Systems with Applications; Pergamon; 2013: 40(9): pages 3715 - 3721. [64]


Notes
-----

Handles directed and undirected graphs and graphs with parallel edges.

"""

#    This extension was originally coded by Ursula Redmond
#    during postgraduate research at the Clique Research Cluster.
#    Padraig Cunningham, principal investigator.
#    School of Computer Science and Informatics, University College Dublin.

from __future__ import absolute_import
import networkx as nx
from datetime import datetime, timedelta
from .isomorphvf2 import GraphMatcher, DiGraphMatcher

__all__ = ['TimeRespectingGraphMatcher',
           'TimeRespectingDiGraphMatcher']

def get_date(dictionary, temporal_attribute_name):
    '''
    A future refactor will remove this conversion step.
    Given the data dictionary of an edge, return the datetime.
    '''
    #if 'date' in dictionary:
        #date = dictionary['date']
        #return datetime.strptime(date, '%Y-%m-%d')
    #elif 'datetime' in dictionary:
        #dt = dictionary['datetime']
        #return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    
    date = dictionary[temporal_attribute_name]
    return datetime.strptime(date, '%Y-%m-%d')
    

class TimeRespectingGraphMatcher(GraphMatcher):

    def __init__(self, G1, G2, temporal_attribute_name, delta):
        """Initialize TimeRespectingGraphMatcher.

        G1 and G2 should be nx.Graph or nx.MultiGraph instances.

        Examples
        --------
        To create a TimeRespectingGraphMatcher which checks for syntactic and semantic feasibility:

        >>> from networkx.algorithms import isomorphism
        >>> G1 = nx.Graph(nx.path_graph(4, create_using=nx.Graph()))

        >>> G2 = nx.Graph(nx.path_graph(4, create_using=nx.Graph()))

        >>> GM = isomorphism.TimeRespectingGraphMatcher(G1, G2, 'date', timedelta(days=1))
        """
        self.temporal_attribute_name = temporal_attribute_name
        self.delta = delta
        super(TimeRespectingGraphMatcher, self).__init__(G1, G2)
    
    def one_hop(self, Gx, Gx_node, neighbors):
        '''
        Edges one hop out from a node in the mapping should be time-respecting w.r.t. each other.
        '''
        time_respecting = True
        dates = []
        for n in neighbors:
            if type(Gx) == type(nx.Graph()): # Graph G[u][v] returns the data dictionary.
                dates.append(get_date(Gx[Gx_node][n], self.temporal_attribute_name))
            else: # MultiGraph G[u][v] returns a dictionary of key -> data dictionary.
                for edge in Gx[Gx_node][n].values(): # Iterates all edges between node pair.
                    dates.append(get_date(edge, self.temporal_attribute_name))
        if any(x is None for x in dates):
            raise ValueError('Datetime not supplied for at least one edge.')
        dates.sort() # Small to large.
        if 0 < len(dates) and not (dates[-1] - dates[0] <= self.delta):
            time_respecting = False
        return time_respecting
    
    def two_hop(self, Gx, core_x, Gx_node, neighbors):
        '''
        Paths of length 2 from Gx_node should be time-respecting.
        '''
        time_respecting = True
        for neigh in neighbors:
            out_neighbors = [b for b in Gx[neigh] if b in core_x]
            out_neighbors.append(Gx_node) # Include Gx_node as a neighbor, since it's not in the mapping.
            if not self.one_hop(Gx, neigh, out_neighbors):
                time_respecting = False
                break
        return time_respecting

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if adding (G1_node, G2_node) is semantically feasible.

        Any subclass which redefines semantic_feasibility() must maintain
        the self.tests if needed, to keep the match() method functional. Implementations
        should consider multigraphs.
        """
        neighbors = [n for n in self.G1[G1_node] if n in self.core_1]
        if not self.one_hop(self.G1, G1_node, neighbors): # Fail fast on first node.
            return False
        if not self.two_hop(self.G1, self.core_1, G1_node, neighbors):
            return False
        # Otherwise, this node is sematically feasible!
        return True


class TimeRespectingDiGraphMatcher(DiGraphMatcher):

    def __init__(self, G1, G2, temporal_attribute_name, delta):
        """Initialize TimeRespectingDiGraphMatcher.

        G1 and G2 should be nx.DiGraph or nx.MultiDiGraph instances.

        Examples
        --------
        To create a TimeRespectingDiGraphMatcher which checks for syntactic and semantic feasibility:

        >>> from networkx.algorithms import isomorphism
        >>> G1 = nx.DiGraph(nx.path_graph(4, create_using=nx.DiGraph()))

        >>> G2 = nx.DiGraph(nx.path_graph(4, create_using=nx.DiGraph()))

        >>> GM = isomorphism.TimeRespectingDiGraphMatcher(G1, G2, 'date', timedelta(days=1))
        """
        self.temporal_attribute_name = temporal_attribute_name
        self.delta = delta
        super(TimeRespectingDiGraphMatcher, self).__init__(G1, G2)
    
    def get_pred_dates(self, Gx, Gx_node, core_x, pred):
        '''
        Get the dates of edges from predecessors.
        '''
        pred_dates = []
        if type(Gx) == type(nx.DiGraph()): # Graph G[u][v] returns the data dictionary.
            for n in pred:
                pred_dates.append(get_date(Gx[n][Gx_node], self.temporal_attribute_name))
        else: # MultiGraph G[u][v] returns a dictionary of key -> data dictionary.
            for n in pred:
                for data_dict in Gx[n][Gx_node].values(): # Iterates all edge data between node pair.
                    pred_dates.append(get_date(data_dict, self.temporal_attribute_name))
        return pred_dates
    
    def get_succ_dates(self, Gx, Gx_node, core_x, succ):
        '''
        Get the dates of edges to successors.
        '''
        succ_dates = []
        if type(Gx) == type(nx.DiGraph()): # Graph G[u][v] returns the data dictionary.
            for n in succ:
                succ_dates.append(get_date(Gx[Gx_node][n], self.temporal_attribute_name))
        else: # MultiGraph G[u][v] returns a dictionary of key -> data dictionary.
            for n in succ:
                for data_dict in Gx[Gx_node][n].values(): # Iterates all edge data between node pair.
                    succ_dates.append(get_date(data_dict, self.temporal_attribute_name))
        return succ_dates

    def one_hop(self, Gx, Gx_node, core_x, pred, succ):
        '''
        The ego node.
        '''
        time_respecting = True
        pred_dates = self.get_pred_dates(Gx, Gx_node, core_x, pred)
        succ_dates = self.get_succ_dates(Gx, Gx_node, core_x, succ)
        if not (self.test_one(pred_dates, succ_dates) and self.test_two(pred_dates, succ_dates)):
            time_respecting = False
        return time_respecting
    
    def two_hop_pred(self, Gx, Gx_node, core_x, pred, succ):
        '''
        The predeccessors of the ego node.
        '''
        time_respecting = True
        for p in pred:
            pred_p, succ_p = [n for n in Gx.predecessors(p) if n in core_x], [n for n in Gx.successors(p) if n in core_x]
            succ_p.append(Gx_node)
            if not self.one_hop(Gx, p, core_x, pred_p, succ_p):
                time_respecting = False
                break
        return time_respecting

    def two_hop_succ(self, Gx, Gx_node, core_x, pred, succ):
        '''
        The successors of the ego node.
        '''
        time_respecting = True
        for s in succ:
            pred_s, succ_s = [n for n in Gx.predecessors(s) if n in core_x], [n for n in Gx.successors(s) if n in core_x]
            pred_s.append(Gx_node)
            if not self.one_hop(Gx, s, core_x, pred_s, succ_s):
                time_respecting = False
                break
        return time_respecting
    
    def test_one(self, pred_dates, succ_dates):
        '''
        Edges one hop out from Gx_node in the mapping should be time-respecting w.r.t. each other, regardless of direction.
        '''
        time_respecting = True
        dates = pred_dates + succ_dates
        
        if any(x is None for x in dates):
            raise ValueError('Date or datetime not supplied for at least one edge.')
        
        dates.sort() # Small to large.
        if 0 < len(dates) and not (dates[-1] - dates[0] <= self.delta):
            time_respecting = False
        return time_respecting
    
    def test_two(self, pred_dates, succ_dates):
        '''
        Edges from a dual Gx_node in the mapping should be ordered in a time-respecting manner.
        '''
        time_respecting = True
        pred_dates.sort()
        succ_dates.sort()
        # First out before last in; negative of the necessary condition for time-respect.
        if 0 < len(succ_dates) and 0 < len(pred_dates) and succ_dates[0] < pred_dates[-1]:
            time_respecting = False
        return time_respecting

    def semantic_feasibility(self, G1_node, G2_node):
        """Returns True if adding (G1_node, G2_node) is semantically feasible.

        Any subclass which redefines semantic_feasibility() must maintain
        the self.tests if needed, to keep the match() method functional. Implementations
        should consider multigraphs.
        """
        pred, succ = [n for n in self.G1.predecessors(G1_node) if n in self.core_1], [n for n in self.G1.successors(G1_node) if n in self.core_1]
        if not self.one_hop(self.G1, G1_node, self.core_1, pred, succ): # Fail fast on first node.
            return False
        if not self.two_hop_pred(self.G1, G1_node, self.core_1, pred, succ):
            return False
        if not self.two_hop_succ(self.G1, G1_node, self.core_1, pred, succ):
            return False
        # Otherwise, this node is sematically feasible!
        return True

