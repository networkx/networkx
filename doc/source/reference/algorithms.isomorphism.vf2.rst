.. _vf2:

*************
VF2 Algorithm 
*************

.. automodule:: networkx.algorithms.isomorphism.isomorphvf2

Graph Matcher
-------------
.. currentmodule:: networkx.algorithms.isomorphism

.. autosummary::
   :toctree: generated/
   
    GraphMatcher.__init__
    GraphMatcher.initialize
    GraphMatcher.is_isomorphic
    GraphMatcher.subgraph_is_isomorphic
    GraphMatcher.isomorphisms_iter
    GraphMatcher.subgraph_isomorphisms_iter
    GraphMatcher.candidate_pairs_iter
    GraphMatcher.match
    GraphMatcher.semantic_feasibility
    GraphMatcher.syntactic_feasibility


DiGraph Matcher
---------------
.. currentmodule:: networkx.algorithms.isomorphism

.. autosummary::
   :toctree: generated/

    DiGraphMatcher.__init__
    DiGraphMatcher.initialize
    DiGraphMatcher.is_isomorphic
    DiGraphMatcher.subgraph_is_isomorphic
    DiGraphMatcher.isomorphisms_iter
    DiGraphMatcher.subgraph_isomorphisms_iter
    DiGraphMatcher.candidate_pairs_iter
    DiGraphMatcher.match
    DiGraphMatcher.semantic_feasibility
    DiGraphMatcher.syntactic_feasibility


Match helpers
-------------
.. currentmodule:: networkx.algorithms.isomorphism

.. autosummary::
   :toctree: generated/

   categorical_node_match
   categorical_edge_match
   categorical_multiedge_match
   numerical_node_match
   numerical_edge_match
   numerical_multiedge_match
   generic_node_match
   generic_edge_match
   generic_multiedge_match

