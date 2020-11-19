"""
=====
Graphs from geographic points
=====

This example shows how to build a delaunay graph (plus its dual,
the set of Voronoi polygons) from a set of points.
For this, we will use the set of cholera cases at the Broad Street Pump, 
recorded by John Snow in 1853. The methods shown here can also work 
directly with polygonal data using their centroids as representative points. 
"""

from libpysal import weights, examples
from libpysal.cg import voronoi_frames
from contextily import add_basemap
import matplotlib.pyplot as plt
import networkx as nx
import numpy
import geopandas

# read in example data online
cases = geopandas.read_file('cholera_cases.gpkg')

# construct the array of coordinates for the centroid
coordinates = numpy.column_stack((cases.geometry.x, cases.geometry.y))

# construct the voronoi diagram
cells, generators = voronoi_frames(coordinates, clip='convex hull')

# the contiguity graph of voronoi cells is the delaunay triangulation
# clipping the extent of the voronoi diagram to the original pattern's
# convex hull may remove distant links on the edges, though!
delaunay = weights.Rook.from_dataframe(cells)

# convert the graphs to networkx
delaunay_graph = delaunay.to_networkx()

# merge the networkx nodes back to their positions
positions = dict(zip(delaunay_graph.nodes, coordinates))

# plot
ax = cells.plot(facecolor='lightblue', alpha=.50, edgecolor='cornsilk', linewidth=2)
add_basemap(ax)
ax.axis('off')
nx.draw(delaunay_graph, positions, ax=ax, node_size=2, node_color="k", edge_color='k', alpha=.8)
plt.show()
