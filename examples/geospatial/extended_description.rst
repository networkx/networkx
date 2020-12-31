:orphan:

Geospatial Examples Description
-------------------------------

Functions for reading and writing shapefiles are provided in NetworkX versions <3.0.
However, we recommend that you use the following libraries when working
with geospatial data (including reading and writing shapefiles).

Geospatial Python Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`GeoPandas <https://geopandas.readthedocs.io/>`__ provides
interoperability between geospatial formats and storage mechanisms
(e.g., databases) and Pandas data frames for tabular-oriented processing
of spatial data, as well as a wide array of supporting functionality
including spatial indices, spatial predicates (e.g., test if geometries
intersect each other), spatial operations (e.g., the area of overlap
between intersecting polygons), and more.

See the following examples that use GeoPandas:

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a delaunay graph (plus its dual, the set of Voronoi polygons) f...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_delaunay_thumb.png
     :alt: Delaunay graphs from geographic points

     :ref:`sphx_glr_auto_examples_geospatial_plot_delaunay.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of geographic lines (sometimes called &quot;lines...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_lines_thumb.png
     :alt: Graphs from a set of lines

     :ref:`sphx_glr_auto_examples_geospatial_plot_lines.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of polygons using PySAL and geopandas. We&#x27;ll...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_polygons_thumb.png
     :alt: Graphs from Polygons

     :ref:`sphx_glr_auto_examples_geospatial_plot_polygons.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of points using PySAL and geopandas. In this...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_points_thumb.png
     :alt: Graphs from geographic points

     :ref:`sphx_glr_auto_examples_geospatial_plot_points.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use OSMnx to download and model a street network from OpenStreetMap, ...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_osmnx_thumb.png
     :alt: OpenStreetMap with OSMnx

     :ref:`sphx_glr_auto_examples_geospatial_plot_osmnx.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-clear"></div>

`PySAL <https://pysal.org/>`__ provides a rich suite of spatial analysis
algorithms. From a network analysis context, `spatial
weights <https://pysal.org/libpysal/api.html#spatial-weights>`__
provide… (Levi please add more here).

See the following examples that use PySAL:

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a delaunay graph (plus its dual, the set of Voronoi polygons) f...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_delaunay_thumb.png
     :alt: Delaunay graphs from geographic points

     :ref:`sphx_glr_auto_examples_geospatial_plot_delaunay.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of geographic lines (sometimes called &quot;lines...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_lines_thumb.png
     :alt: Graphs from a set of lines

     :ref:`sphx_glr_auto_examples_geospatial_plot_lines.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of polygons using PySAL and geopandas. We&#x27;ll...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_polygons_thumb.png
     :alt: Graphs from Polygons

     :ref:`sphx_glr_auto_examples_geospatial_plot_polygons.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of points using PySAL and geopandas. In this...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_points_thumb.png
     :alt: Graphs from geographic points

     :ref:`sphx_glr_auto_examples_geospatial_plot_points.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-clear"></div>

`momepy <http://docs.momepy.org/en/stable/>`__ builds on top of
GeoPandas and PySAL to provide a suite of algorithms focused on urban
morphology. From a network analysis context, momepy enables you to
convert your line geometry to `networkx.MultiGraph` and back to 
`geopandas.GeoDataFrame` and apply a range of analytical functions aiming at 
morphological description of (street) network configurations.

See the following examples that use momepy:

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to build a graph from a set of geographic lines (sometimes called &quot;lines...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_lines_thumb.png
     :alt: Graphs from a set of lines

     :ref:`sphx_glr_auto_examples_geospatial_plot_lines.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-clear"></div>

`OSMnx <https://osmnx.readthedocs.io/>`__ provides a set of tools to retrieve,
model, project, analyze, and visualize OpenStreetMap street networks (and any
other networked infrastructure) as `networkx.MultiDiGraph` objects, and convert
these MultiDiGraphs to/from `geopandas.GeoDataFrame`. It can automatically add
node/edge attributes for: elevation and grade (using the Google Maps Elevation
API), edge travel speed, edge traversal time, and edge bearing. It can also
retrieve any other spatial data from OSM (such as building footprints, public
parks, schools, transit stops, etc) as Geopandas GeoDataFrames.

See the following examples that use OSMnx:

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use OSMnx to download and model a street network from OpenStreetMap, ...">

.. only:: html

 .. figure:: /auto_examples/geospatial/images/thumb/sphx_glr_plot_osmnx_thumb.png
     :alt: OpenStreetMap with OSMnx

     :ref:`sphx_glr_auto_examples_geospatial_plot_osmnx.py`

.. raw:: html

    </div>

.. raw:: html

    <div class="sphx-glr-clear"></div>

Key Concepts
~~~~~~~~~~~~

One of the essential tasks in network analysis of geospatial data is
defining the spatial relationships between spatial features (points,
lines, or polygons).

``PySAL`` provides several ways of representing these spatial
relationships between features using the concept of spatial weights.
These include relationships such as ``Queen``, ``Rook``, ...
(Levi please add more here with a brief explanation of each).

``momepy`` allows representation of street networks as both primal
and dual graphs (in a street network analysis sense). The primal approach
turns intersections into Graph nodes and street segments into edges,
a format which is used for a majority of morphological studies. The dual 
approach uses street segments as nodes and intersection topology
as edges, which allows encoding of angular information (i.e an analysis
can be weighted by angles between street segments instead of their length).

``OSMnx`` represents street networks as primal, nonplanar, directed graphs with
possible self-loops and parallel edges to model real-world street network form
and flow. Nodes represent intersections and dead-ends, and edges represent the
street segments linking them. Details of OSMnx's modeling methodology are
available at https://doi.org/10.1016/j.compenvurbsys.2017.05.004

Learn More
~~~~~~~~~~

To learn more see `Geographic Data Science with PySAL and the PyData Stack
<https://geographicdata.science/book/intro.html>`_.
