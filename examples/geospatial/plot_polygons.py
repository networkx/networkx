"""
=====
Graphs from Polygons
=====

This example shows how to build a graph from a set of polygons
using PySAL and geopandas. We'll focus on the Queen contiguity 
graph, but constructors are also provided for Rook contiguity, 
as well as other kinds of graphs from the polygon centroids. 
"""

from libpysal import weights
import matplotlib.pyplot as plt
import networkx as nx
import geopandas
import numpy

# read in example data online
filepath = "nuts1.geojson"
european_regions = geopandas.read_file(filepath)

# extract the centroids for connecting the regions
centroids = numpy.column_stack(
    (european_regions.centroid.x, european_regions.centroid.y)
)

# construct the graph
queen = weights.Queen.from_dataframe(european_regions)

# convert the graph to networkx
graph = queen.to_networkx()

# merge the nodes back to their positions
positions = dict(zip(graph.nodes, centroids))

# plot
ax = european_regions.plot(linewidth=1, edgecolor="grey", facecolor="lightblue")
ax.axis([-12, 45, 33, 66])
ax.axis('off')
nx.draw(graph, positions, ax=ax, node_size=5, node_color="r")
plt.show()
