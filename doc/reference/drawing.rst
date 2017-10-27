.. _drawing:

*******
Drawing
*******

NetworkX provides basic functionality for visualizing graphs, but its main goal
is to enable graph analysis rather than perform graph visualization. In the
future, graph visualization functionality may be removed from NetworkX or only
available as an add-on package.

Proper graph visualization is hard, and we highly recommend that people
visualize their graphs with tools dedicated to that task. Notable examples of
dedicated and fully-featured graph visualization tools are
`Cytoscape <http://www.cytoscape.org/>`_,
`Gephi <https://gephi.org/>`_,
`Graphviz <http://www.graphviz.org/>`_ and, for
`LaTeX <http://www.latex-project.org/>`_ typesetting,
`PGF/TikZ <https://sourceforge.net/projects/pgf/>`_.
To use these and other such tools, you should export your NetworkX graph into
a format that can be read by those tools. For example, Cytoscape can read the
GraphML format, and so, ``networkx.write_graphml(G)`` might be an appropriate
choice.

Matplotlib
==========
.. automodule:: networkx.drawing.nx_pylab
.. autosummary::
   :toctree: generated/

   draw
   draw_networkx
   draw_networkx_nodes
   draw_networkx_edges
   draw_networkx_labels
   draw_networkx_edge_labels
   draw_circular
   draw_kamada_kawai
   draw_random
   draw_spectral
   draw_spring
   draw_shell



Graphviz AGraph (dot)
=====================
.. automodule:: networkx.drawing.nx_agraph
.. autosummary::
   :toctree: generated/

   from_agraph
   to_agraph
   write_dot
   read_dot
   graphviz_layout
   pygraphviz_layout


Graphviz with pydot
===================
.. automodule:: networkx.drawing.nx_pydot
.. autosummary::
   :toctree: generated/

   from_pydot
   to_pydot
   write_dot
   read_dot
   graphviz_layout
   pydot_layout


Graph Layout
============
.. automodule:: networkx.drawing.layout
.. autosummary::
   :toctree: generated/

   circular_layout
   kamada_kawai_layout
   random_layout
   rescale_layout
   shell_layout
   spring_layout
   spectral_layout

