NetworkX
--------

NetworkX is a Python package for the creation, manipulation, and
study of the structure, dynamics, and functions of complex networks.

Documentation
   http://networkx.github.io
Mailing List
   https://groups.google.com/forum/#!forum/networkx-discuss
Development
   https://github.com/networkx/networkx

   .. image:: https://travis-ci.org/networkx/networkx.png?branch=master
      :target: https://travis-ci.org/networkx/networkx

   .. image:: https://readthedocs.org/projects/networkx/badge/?version=latest
      :target: https://readthedocs.org/projects/networkx/?badge=latest
      :alt: Documentation Status

   .. image:: https://coveralls.io/repos/networkx/networkx/badge.png?branch=master
      :target: https://coveralls.io/r/networkx/networkx?branch=master


A quick example that finds the shortest path between two nodes in an undirected graph::

   >>> import networkx as nx
   >>> G = nx.Graph()
   >>> G.add_edge('A', 'B', weight=4)
   >>> G.add_edge('B', 'D', weight=2)
   >>> G.add_edge('A', 'C', weight=3)
   >>> G.add_edge('C', 'D', weight=4)
   >>> nx.shortest_path(G, 'A', 'D', weight='weight')
   ['A', 'B', 'D']

Distributed with a BSD license; see LICENSE.txt::

   Copyright (C) 2004-2016 NetworkX Developers
   Aric Hagberg <hagberg@lanl.gov>
   Dan Schult <dschult@colgate.edu>
   Pieter Swart <swart@lanl.gov>
