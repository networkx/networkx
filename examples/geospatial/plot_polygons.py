"""
=====
Plotting a graph from a set of polygons using PySAL
=====

This example shows how to build a graph from a set of polygons
using PySAL and geopandas
"""

from libpysal import weights
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy

# read in example data online
filepath = "https://datahub.io/core/geo-nuts-administrative-boundaries/r/nuts_rg_60m_2013_lvl_1.geojson"
european_regions = gpd.read_file(filepath)

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
ax.axis([-10, 45, 39, 60])
nx.draw(graph, positions, ax=ax, node_size=5, node_color="r")
plt.show()
