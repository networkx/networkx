NetworkX
========

NetworkX is a Python package for the creation, manipulation, and
study of the structure, dynamics, and functions of complex networks.

Documentation
   http://networkx.github.io
Mailing List
   https://groups.google.com/forum/#!forum/networkx-discuss
Development
   https://github.com/networkx/networkx

   .. image:: https://travis-ci.org/networkx/networkx.svg?branch=master
      :target: https://travis-ci.org/networkx/networkx

   .. image:: https://readthedocs.org/projects/networkx/badge/?version=latest
      :target: https://readthedocs.org/projects/networkx/?badge=latest
      :alt: Documentation Status

   .. image:: https://coveralls.io/repos/networkx/networkx/badge.svg?branch=master
      :target: https://coveralls.io/r/networkx/networkx?branch=master


Download
--------

Get the latest version of NetworkX from
https://pypi.python.org/pypi/networkx/

::

    $ pip install networkx

To get the git version do

::

    $ git clone git://github.com/networkx/networkx.git

Decorator package is required for NetworkX.

::

    $ pip install decorator

Install networkx with optional dependencies

::

    $ pip install networkx[all]

Usage
-----

A quick example that finds the shortest path between two nodes in an undirected graph::

   >>> import networkx as nx
   >>> G = nx.Graph()
   >>> G.add_edge('A', 'B', weight=4)
   >>> G.add_edge('B', 'D', weight=2)
   >>> G.add_edge('A', 'C', weight=3)
   >>> G.add_edge('C', 'D', weight=4)
   >>> nx.shortest_path(G, 'A', 'D', weight='weight')
   ['A', 'B', 'D']


Bugs
----

Our issue tracker is at https://github.com/networkx/networkx/issues.
Please report any bugs that you find.  Or, even better, fork the repository on
GitHub and create a pull request.  We welcome all changes, big or small, and we
will help you make the pull request if you are new to git
(just ask on the issue).

License
-------

Distributed with a BSD license; see LICENSE.txt::

   Copyright (C) 2004-2016 NetworkX Developers
   Aric Hagberg <hagberg@lanl.gov>
   Dan Schult <dschult@colgate.edu>
   Pieter Swart <swart@lanl.gov>

.. _here: http://webchat.freenode.net?channels=%23networkx
