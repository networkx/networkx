"""
===========
Knuth Miles
===========

`miles_graph()` returns an undirected graph over the 128 US cities from.  The
cities each have location and population data.  The edges are labeled with the
distance between the two cities.

This example is described in Section 1.1 of

    Donald E. Knuth, "The Stanford GraphBase: A Platform for Combinatorial
    Computing", ACM Press, New York, 1993.
    http://www-cs-faculty.stanford.edu/~knuth/sgb.html

The data file can be found at:

- https://github.com/networkx/networkx/blob/master/examples/drawing/knuth_miles.txt.gz
"""

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.pyplot as plt


central_lat = 37.5
central_lon = -96
extent = [-120, -70, 24, 50.5]
central_lon = np.mean(extent[:2])
central_lat = np.mean(extent[ 2  :])

plt.figure(figsize=(12, 6))
ax = plt.axes(projection = ccrs.AlbersEqualArea(central_lon, central_lat))
ax.set_extent(extent)

ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.LAND, edgecolor="black")
ax.add_feature(cartopy.feature.LAKES, edgecolor="black")
ax.add_feature(cartopy.feature.RIVERS)
ax.gridlines()

plt.show()
