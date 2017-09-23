SparseGraph6
============

Functions for reading and writing graphs in the *graph6* or *sparse6* file
formats.

According to the author of these formats,

    *graph6* and *sparse6* are formats for storing undirected graphs in a
    compact manner, using only printable ASCII characters. Files in these
    formats have text type and contain one line per graph.

    *graph6* is suitable for small graphs, or large dense graphs. *sparse6* is
    more space-efficient for large sparse graphs.

    -- `graph6 and sparse6 homepage`_

.. _graph6 and sparse6 homepage: http://users.cecs.anu.edu.au/~bdm/data/formats.html

Graph6
------
.. automodule:: networkx.readwrite.graph6
.. autosummary::
   :toctree: generated/

   parse_graph6
   read_graph6
   generate_graph6
   write_graph6

Sparse6
-------
.. automodule:: networkx.readwrite.sparse6
.. autosummary::
   :toctree: generated/

   parse_sparse6
   read_sparse6
   generate_sparse6
   write_sparse6

