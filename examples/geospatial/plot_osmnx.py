"""
========================
OpenStreetMap with OSMnx
========================

This example shows how to use OSMnx to download and model a street network
from OpenStreetMap, visualize centrality, then save the graph as a GeoPackage,
or GraphML file.

OSMnx is a Python package to download, model, analyze, and visualize street
networks and other geospatial features from OpenStreetMap. You can download
and model walking, driving, or biking networks with a single line of code then
easily analyze and visualize them. You can just as easily work with urban
amenities/points of interest, building footprints, transit stops, elevation
data, street orientations, speed/travel time, and routing.

See https://osmnx.readthedocs.io for the OSMnx documentation.
See https://github.com/gboeing/osmnx-examples for the OSMnx Examples gallery.
"""

import networkx as nx
import osmnx as ox

ox.settings.use_cache = True

# download street network data from OSM and construct a MultiDiGraph model
G = ox.graph.graph_from_point((37.79, -122.41), dist=750, network_type="drive")

# impute edge (driving) speeds and calculate edge travel times
G = ox.speed.add_edge_speeds(G)
G = ox.speed.add_edge_travel_times(G)

# you can convert MultiDiGraph to/from GeoPandas GeoDataFrames
gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
G = ox.utils_graph.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs=G.graph)

# convert MultiDiGraph to DiGraph to use nx.betweenness_centrality function
# choose between parallel edges by minimizing travel_time attribute value
D = ox.utils_graph.get_digraph(G, weight="travel_time")

# calculate node betweenness centrality, weighted by travel time
bc = nx.betweenness_centrality(D, weight="travel_time", normalized=True)
nx.set_node_attributes(G, values=bc, name="bc")

# plot the graph, coloring nodes by betweenness centrality
nc = ox.plot.get_node_colors_by_attr(G, "bc", cmap="plasma")
fig, ax = ox.plot.plot_graph(
    G, bgcolor="k", node_color=nc, node_size=50, edge_linewidth=2, edge_color="#333333"
)

# save graph as a geopackage or graphml file
ox.io.save_graph_geopackage(G, filepath="./graph.gpkg")
ox.io.save_graphml(G, filepath="./graph.graphml")
