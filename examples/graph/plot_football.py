"""
========
Football
========

Load football network in GML format and compute some network statistics.
Data provided by authors of [1]_

Shows how to unpack a zipped GML file and load it into a NetworkX graph.
This example uses the pathlib library for filename manipulation.

The data file can be found at:

- https://public.websites.umich.edu/~mejn/netdata/football.zip

.. [1] M. Girvan and M. E. J. Newman,
       Community structure in social and biological networks,
       Proc. Natl. Acad. Sci. USA 99, 7821-7826 (2002).
       https://arxiv.org/abs/cond-mat/0112110
"""

import pathlib
import zipfile

import matplotlib.pyplot as plt
import networkx as nx

doc_current = pathlib.Path.cwd()
football_zip = doc_current / "football.zip"

zf = zipfile.ZipFile(football_zip)  # zipfile object
txt = zf.read("football.txt").decode()  # read info file
gml = zf.read("football.gml").decode()  # read gml data
# throw away bogus first line with # from mejn files
gml = gml.split("\n")[1:]
G = nx.parse_gml(gml)  # parse gml data

print(txt)
# print degree for each team - number of games
for n, d in G.degree():
    print(f"{n:20} {d:2}")

options = {"node_color": "black", "node_size": 50, "linewidths": 0, "width": 0.1}

pos = nx.spring_layout(G, seed=1969)  # Seed for reproducible layout
nx.draw(G, pos, **options)
plt.show()
