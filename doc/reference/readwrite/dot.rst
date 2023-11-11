DOT 
===

The `DOT graph description language <https://graphviz.org/doc/info/lang.html>`__
defines a file format that is most often used in the context of graph
visualization with `Graphviz <https://graphviz.org>`__.
NetworkX provides an interface to Graphviz via :doc:`pygraphviz <pygraphviz:index>`,
implemented in `~networkx.drawing.nx_agraph`.
If ``pygraphviz`` is installed, `~networkx.drawing.nx_agraph` can be used to
read and write files in DOT format.

pygraphviz
----------
.. currentmodule:: networkx.drawing.nx_agraph
.. autosummary::

   read_dot
   write_dot
