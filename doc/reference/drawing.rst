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
`Graphviz <http://www.graphviz.org/>`_,
`Hiveplotlib <https://hiveplotlib.readthedocs.io/>`_,
`iplotx <https://iplotx.readthedocs.io/>`_ and, for
`LaTeX <http://www.latex-project.org/>`_ typesetting,
`PGF/TikZ <https://github.com/pgf-tikz/pgf/>`_.
To use these and other such tools, you should export your NetworkX graph into
a format that can be read by those tools. For example, Cytoscape can read the
GraphML format, and so, ``networkx.write_graphml(G, path)`` might be an appropriate
choice.

.. tip::

   ``iplotx`` and ``hiveplotlib`` accept NetworkX native data structures without
   exporting to a file. An example of each is provided below.

More information on the features provided here are available at
 - matplotlib:  http://matplotlib.org/
 - pygraphviz:  http://pygraphviz.github.io/
 - iplotx: https://iplotx.readthedocs.io/
 - hiveplotlib: https://hiveplotlib.readthedocs.io/

Matplotlib
==========
.. automodule:: networkx.drawing.nx_pylab
.. autosummary::
   :toctree: generated/

   display
   apply_matplotlib_colors
   draw
   draw_networkx
   draw_networkx_nodes
   draw_networkx_edges
   draw_networkx_labels
   draw_networkx_edge_labels
   draw_bipartite
   draw_circular
   draw_kamada_kawai
   draw_planar
   draw_random
   draw_spectral
   draw_spring
   draw_shell

Matplotlib with iplotx
======================
Draw networks with matplotlib, using ``iplotx`` for extended styling options.

Examples
--------
.. code-block:: python

  >>> import iplotx as ipx
  >>> G = nx.cycle_graph(5, create_using=nx.DiGraph)
  >>> layout = nx.circular_layout(G)
  >>> ipx.network(G, layout=layout, vertex_facecolor=["tomato", "gold"])

See Also
--------
- `iplotx <https://iplotx.readthedocs.io/>`_
- `iplotx.network <https://iplotx.readthedocs.io/en/latest/api/plotting.html#plotting-api>`_


Hive Plots with Hiveplotlib
===========================
``hiveplotlib`` draws hive plots, a layout that places nodes on a few radial axes
by a partition variable and orders them along each axis by a chosen sorting variable.
Positions are determined by the data rather than a layout algorithm, so the result is
reproducible and makes structural properties of the graph directly legible. A
NetworkX graph can be passed directly, and Networkx node and edge metrics
(such as node ``pagerank``) can be computed on the fly to drive the layout.

Examples
--------
.. code-block:: python

  >>> from hiveplotlib import HivePlot
  >>> p = [[0.3, 0.005, 0.0],
  ...      [0.005, 0.3, 0.03],
  ...      [0.0, 0.03, 0.3]]
  >>> G = nx.stochastic_block_model(sizes=[15, 15, 15], p=p, seed=0)
  >>> hp = HivePlot(
  ...     graph=G,
  ...     partition_variable="block",
  ...     sorting_variables="pagerank",
  ...     node_graph_metrics="pagerank",
  ...     repeat_axes=True,
  ... )
  >>> hp.plot()

By default, ``hiveplotlib`` uses Matplotlib for rendering, but hive plots can also be
easily rendered with Bokeh, Plotly, and HoloViews. They can also be rasterized with
Datashader for larger networks.

See Also
--------
- `Hiveplotlib <https://hiveplotlib.readthedocs.io/>`_
- `Creating hive plots from NetworkX <https://hiveplotlib.readthedocs.io/stable/notebooks/creating_hive_plots_from_networkx.html>`_
- `Computing graph metrics <https://hiveplotlib.readthedocs.io/stable/notebooks/computing_graph_metrics.html>`_
- `Visualizing with other backends <https://hiveplotlib.readthedocs.io/stable/notebooks/hive_plot_viz_outside_matplotlib.html>`_
- `Hive plots for large networks <https://hiveplotlib.readthedocs.io/stable/notebooks/hive_plots_for_large_networks.html>`_


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

   arf_layout
   bipartite_layout
   bfs_layout
   circular_layout
   forceatlas2_layout
   kamada_kawai_layout
   planar_layout
   random_layout
   rescale_layout
   rescale_layout_dict
   shell_layout
   spring_layout
   spectral_layout
   spiral_layout
   multipartite_layout


LaTeX Code
==========
.. automodule:: networkx.drawing.nx_latex
.. autosummary::
   :toctree: generated/

   to_latex_raw
   to_latex
   write_latex
