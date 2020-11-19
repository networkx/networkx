"""
=====
Graphs from geographic points
=====

This example shows how to build a graph from a set of points
using PySAL and geopandas. In this example, we'll use the famous
set of cholera cases at the Broad Street Pump, recorded by John Snow in 1853.
The methods shown here can also work directly with polygonal data using their
centroids as representative points. 
"""

from libpysal import weights, examples
from contextily import add_basemap
import matplotlib.pyplot as plt
import networkx as nx
import numpy
import geopandas

# read in example data online
cases = geopandas.read_file('cholera_cases.gpkg')

# construct the array of coordinates for the centroid
coordinates = numpy.column_stack((cases.geometry.x, cases.geometry.y))

# construct two different kinds of graphs:

## 3-nearest neighbor graph
knn3 = weights.KNN.from_dataframe(cases, k=3)

## all pairs within 50 meters 
dist = weights.DistanceBand.from_array(coordinates, threshold=50)

# convert the graphs to networkx
knn_graph = knn3.to_networkx()
dist_graph = dist.to_networkx()

# merge the networkx nodes back to their positions
positions = dict(zip(knn_graph.nodes, coordinates))

# plot
f, ax = plt.subplots(1, 2, figsize=(8, 4))
for i, facet in enumerate(ax):
    cases.plot(marker=".", color="orangered", ax=facet)
    add_basemap(facet)
    facet.set_title(("KNN-3", "50-meter Distance Band")[i])
nx.draw(knn_graph, positions, ax=ax[0], node_size=5, node_color="b")
nx.draw(dist_graph, positions, ax=ax[1], node_size=5, node_color="b")
plt.show()
