DOT 
===
The DOT graph description language defines a file format that is most often
used in the context of graph visualization with the Graphviz package.
NetworkX provides interfaces to Graphviz through two different external
packages: `pydot` and `pygraphviz`, implemented in `nx_pydot` and `nx_agraph`
respectively. If these packages are installed, NetworkX can be used to
read and write files in DOT format.

pydot
-----
.. currentmodule:: networkx.drawing.nx_pydot
.. autosummary::

   read_dot
   write_dot

pygraphviz
----------
.. currentmodule:: networkx.drawing.nx_agraph
.. autosummary::

   read_dot
   write_dot
