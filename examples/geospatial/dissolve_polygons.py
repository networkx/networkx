"""
=====
Dissolve adjacent polygons
=====

This example shows how to dissolve adjacent polygons by erasing the boundaries
between them.

Using a geometric union alone can be quite slow depending on the nature of the
geometry, so there is sometimes an advantage to only performing a union on those
geometries that interact spatially, especially if those relationships can be
determined using a spatial index such as in this example.  Furthermore, it may
be important to retain a connection back to some of the original attributes of
the dissolved geometries, whereas performing a union without a grouping step
first will lose this information.

Dissolve in GeoPandas requires an attribute to dissolve by.  This example uses
networkx to identify all groups of polygons that intersect each other, and then
dissolves by that group.

More information on dissolve at:
https://geopandas.org/aggregation_with_dissolve.html

Note: this example requires either rtree or pygeos optional dependency for
GeoPandas.

See also
--------
plot_polygons.py: provides an example using PySAL to identify contiguous
    groups of polygons, which could then be unioned together to create
    the same results as this example.
"""

import matplotlib.pyplot as plt
import networkx as nx
import geopandas
import pandas
import numpy

### Read in example data.
# Input file format could be any format supported by GeoPandas.
filepath = "nuts1.geojson"
european_regions = geopandas.read_file(filepath)

### Spatially join regions to themselves using the spatial index.
# This finds all regions that spatially intersect other regions.
pairs = pandas.DataFrame(geopandas.sjoin(european_regions, european_regions))[
    ["index_right"]
]

### Drop self-intersections (a region that intersects itself).
# Both index and index_right are based on the original index of european_regions.
pairs = pairs.loc[pairs.index != pairs.index_right]

### construct network from pairs.
# reset_index() is used to convert index into a column.
network = nx.from_pandas_edgelist(
    pairs.reset_index(),
    "index",
    "index_right",
)

### Use components from the network to identify all connected subgraphs.
components = pandas.Series(nx.connected_components(network)).apply(list)

### Flatten components to individual pairs of group (index) to original region
groups = pandas.DataFrame(components.explode().rename("index_right"))

### Create a column to hold the group identifier
groups["group"] = groups.index.copy()

### Index on index_right to join back to pairs.
groups = groups.set_index("index_right")

### Join to regions and only keep those that are grouped
grouped = european_regions[["NUTS_ID", "geometry"]].join(groups, how="inner")

### Dissolve geometries within each group
# Polygons are dissolved by taking the unary union of polygons within each group,
# which dissolves interior edges.
dissolved = grouped[["group", "geometry"]].dissolve(by="group")

### Join back to list of NUTS_ID
dissolved = dissolved.join(grouped.groupby("group").NUTS_ID.unique())

### Merge in regions that were not dissolved together
not_dissolved = european_regions.loc[~european_regions.index.isin(groups.index)][
        ["NUTS_ID", "geometry"]
    ]
# convert NUTS_ID to a list similar to those that are dissolved
not_dissolved.NUTS_ID = not_dissolved.NUTS_ID.apply(lambda x: [x])

grouped_regions = dissolved.append(
    not_dissolved,
    ignore_index=True,
).reset_index(drop=True)

### plot
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.axis([-12, 45, 33, 66])
ax1.axis("off")
european_regions.plot(linewidth=1, edgecolor="grey", facecolor="lightblue", ax=ax1)

ax2.axis([-12, 45, 33, 66])
ax2.axis("off")
grouped_regions.plot(linewidth=1, edgecolor="grey", facecolor="lightblue", ax=ax2)
plt.show()