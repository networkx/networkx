.. _tree:

Tree
====

.. toctree::
   :maxdepth: 2

Recognition
-----------
.. automodule:: networkx.algorithms.tree.recognition
.. autosummary::
   :toctree: generated/

   is_tree
   is_forest
   is_arborescence
   is_branching

Branchings and Spanning Arborescences
-------------------------------------
.. automodule:: networkx.algorithms.tree.branchings
.. autosummary::
   :toctree: generated/

   branching_weight
   greedy_branching
   maximum_branching
   minimum_branching
   maximum_spanning_arborescence
   minimum_spanning_arborescence
   Edmonds

Encoding and decoding
---------------------
.. automodule:: networkx.algorithms.tree.coding
.. autosummary::
   :toctree: generated/

   from_nested_tuple
   to_nested_tuple
   from_prufer_sequence
   to_prufer_sequence

Operations
----------
.. automodule:: networkx.algorithms.tree.operations
.. autosummary::
   :toctree: generated/

   join

Spanning Trees
--------------
.. automodule:: networkx.algorithms.tree.mst
.. autosummary::
   :toctree: generated/

   minimum_spanning_tree
   maximum_spanning_tree
   minimum_spanning_edges
   maximum_spanning_edges

Exceptions
----------
.. automodule:: networkx.algorithms.tree.coding
   :noindex:
.. autosummary::
   :toctree: generated/

   NotATree
