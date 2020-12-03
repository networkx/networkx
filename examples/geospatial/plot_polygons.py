"""
====================
Graphs from Polygons
====================

This example shows how to build a graph from a set of polygons
using PySAL and geopandas. We'll focus on the Queen contiguity 
graph, but constructors are also provided for Rook contiguity, 
as well as other kinds of graphs from the polygon centroids. 
"""

from libpysal import weights
import matplotlib.pyplot as plt
import networkx as nx
import geopandas
import numpy as np

# read in example data from geojson. GeoJSON is a file format
# for encoding geographic data based on JSON. It is useful for
# presenting geographic data on the web, and is increasingly
# used as a file format for geographic data.
filepath = "nuts1.geojson"
european_regions = geopandas.read_file(filepath)

# extract the centroids for connecting the regions, which is
# the average of the coordinates that define the polygon's boundary
centroids = np.column_stack(
    (european_regions.centroid.x, european_regions.centroid.y)
)

# construct the "Queen" adjacency graph. In geographical applications,
# the "Queen" adjacency graph considers two polygons as connected if
# they share a single point on their boundary. This is an analogue to
# the "Moore" neighborhood nine surrounding cells in a regular grid.
queen = weights.Queen.from_dataframe(european_regions)

# Then, we can convert the graph to networkx object using the
# .to_networkx() method.
graph = queen.to_networkx()

# To plot with networkx, we need to merge the nodes back to
# their positions in order to plot in networkx
positions = dict(zip(graph.nodes, centroids))

# plot with a nice basemap
ax = european_regions.plot(linewidth=1, edgecolor="grey", facecolor="lightblue")
ax.axis([-12, 45, 33, 66])
ax.axis("off")
nx.draw(graph, positions, ax=ax, node_size=5, node_color="r")
plt.show()

# An alternative method to construct graphs from polygons may use
# pygeos. This package is a high-performance interface to the GEOS C
# library, used in computing geographical relationships. These let us
# describe the relationships between "point sets," like polygons whether
# or not a line "crosses" a polygon, or whether two polygons "touch."
# These relationships, called "predicates", are extensive, and are documented
# by the pygeos package.
# The underlying algorithms for this are slightly different from that used
# in the contiguity graph, and so we document this here for clarity.

import pygeos

# In order to do this, we need to convert the default geometry object set
# into the representation required by pygeos
pygeos_polygons = pygeos.from_shapely(european_regions.geometry)

# Then, we need to build a spatial index that allows us to efficiently
# identify polygons that may satisfy our geographic predicate. This is
# an ST-R-Tree, a variant of an R-Tree with efficient storage and construction.
rtree = pygeos.STRtree(pygeos_polygons)

# Then, to make a bunch of queries at the same time, we can
# use the query_bulk() method to obtain head "head" and "tail" of
# each edge in the adjacency graph. We'll use the "touches" graph here
# for clarity.
heads, tails = rtree.query_bulk(pygeos_polygons, predicate="touches")

# With the heads and tails for each edge in the graph of touching polygons,
# we can use networkx's Graph.add_edges_from() method to build our networkx
# graph.
graph = nx.Graph()
graph.add_edges_from(zip(heads, tails))

# finally, we can make a plot in the same fashion as we did before:
ax = european_regions.plot(linewidth=1, edgecolor="grey", facecolor="lightblue")
ax.axis([-12, 45, 33, 66])
ax.axis("off")
nx.draw(graph, positions, ax=ax, node_size=5, node_color="r")
plt.show()
