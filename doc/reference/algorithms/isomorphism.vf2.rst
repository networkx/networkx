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

    GraphMatcher
    GraphMatcher.__init__
    GraphMatcher.initialize
    GraphMatcher.is_isomorphic
    GraphMatcher.subgraph_is_isomorphic
    GraphMatcher.subgraph_is_monomorphic
    GraphMatcher.isomorphisms_iter
    GraphMatcher.subgraph_isomorphisms_iter
    GraphMatcher.subgraph_monomorphisms_iter
    GraphMatcher.candidate_pairs_iter
    GraphMatcher.match
    GraphMatcher.semantic_feasibility
    GraphMatcher.syntactic_feasibility


DiGraph Matcher
---------------
.. currentmodule:: networkx.algorithms.isomorphism

.. autosummary::
   :toctree: generated/

    DiGraphMatcher
    DiGraphMatcher.__init__
    DiGraphMatcher.initialize
    DiGraphMatcher.is_isomorphic
    DiGraphMatcher.subgraph_is_isomorphic
    DiGraphMatcher.subgraph_is_monomorphic
    DiGraphMatcher.isomorphisms_iter
    DiGraphMatcher.subgraph_isomorphisms_iter
    DiGraphMatcher.subgraph_monomorphisms_iter
    DiGraphMatcher.candidate_pairs_iter
    DiGraphMatcher.match
    DiGraphMatcher.semantic_feasibility
    DiGraphMatcher.syntactic_feasibility


MultiGraph Matcher
------------------
.. currentmodule:: networkx.algorithms.isomorphism

.. autosummary::
   :toctree: generated/

    MultiGraphMatcher
    MultiGraphMatcher.__init__
    MultiGraphMatcher.initialize
    MultiGraphMatcher.is_isomorphic
    MultiGraphMatcher.subgraph_is_isomorphic
    MultiGraphMatcher.subgraph_is_monomorphic
    MultiGraphMatcher.isomorphisms_iter
    MultiGraphMatcher.subgraph_isomorphisms_iter
    MultiGraphMatcher.subgraph_monomorphisms_iter
    MultiGraphMatcher.candidate_pairs_iter
    MultiGraphMatcher.match
    MultiGraphMatcher.semantic_feasibility
    MultiGraphMatcher.syntactic_feasibility


MultiDiGraph Matcher
--------------------
.. currentmodule:: networkx.algorithms.isomorphism

.. autosummary::
   :toctree: generated/

    MultiDiGraphMatcher
    MultiDiGraphMatcher.__init__
    MultiDiGraphMatcher.initialize
    MultiDiGraphMatcher.is_isomorphic
    MultiDiGraphMatcher.subgraph_is_isomorphic
    MultiDiGraphMatcher.subgraph_is_monomorphic
    MultiDiGraphMatcher.isomorphisms_iter
    MultiDiGraphMatcher.subgraph_isomorphisms_iter
    MultiDiGraphMatcher.subgraph_monomorphisms_iter
    MultiDiGraphMatcher.candidate_pairs_iter
    MultiDiGraphMatcher.match
    MultiDiGraphMatcher.semantic_feasibility
    MultiDiGraphMatcher.syntactic_feasibility


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

