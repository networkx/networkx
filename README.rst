NetworkX
========

.. image:: https://img.shields.io/pypi/v/networkx.svg
   :target: https://pypi.org/project/networkx/

.. image:: https://img.shields.io/pypi/pyversions/networkx.svg
   :target: https://pypi.org/project/networkx/

.. image:: https://travis-ci.org/networkx/networkx.svg?branch=master
   :target: https://travis-ci.org/networkx/networkx

.. image:: https://ci.appveyor.com/api/projects/status/github/networkx/networkx?branch=master&svg=true
   :target: https://ci.appveyor.com/project/dschult/networkx-pqott

.. image:: https://codecov.io/gh/networkx/networkx/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/networkx/networkx

NetworkX is a Python package for the creation, manipulation,
and study of the structure, dynamics, and functions
of complex networks.

- **Website (including documentation):** http://networkx.github.io
- **Mailing list:** https://groups.google.com/forum/#!forum/networkx-discuss
- **Source:** https://github.com/networkx/networkx
- **Bug reports:** https://github.com/networkx/networkx/issues

Simple example
--------------

Find the shortest path between two nodes in an undirected graph:

.. code:: python

    >>> import networkx as nx
    >>> G = nx.Graph()
    >>> G.add_edge('A', 'B', weight=4)
    >>> G.add_edge('B', 'D', weight=2)
    >>> G.add_edge('A', 'C', weight=3)
    >>> G.add_edge('C', 'D', weight=4)
    >>> nx.shortest_path(G, 'A', 'D', weight='weight')
    ['A', 'B', 'D']

Install
-------

Install the latest version of NetworkX::

    $ pip install networkx

Install with all optional dependencies::

    $ pip install networkx[all]

For additional details, please see `INSTALL.rst`.

Bugs
----

Please report any bugs that you find `here <https://github.com/networkx/networkx/issues>`_.
Or, even better, fork the repository on `GitHub <https://github.com/networkx/networkx>`_
and create a pull request (PR). We welcome all changes, big or small, and we
will help you make the PR if you are new to `git` (just ask on the issue and/or
see `CONTRIBUTING.rst`).

License
-------

Released under the 3-Clause BSD license (see `LICENSE.txt`)::

   Copyright (C) 2004-2019 NetworkX Developers
   Aric Hagberg <hagberg@lanl.gov>
   Dan Schult <dschult@colgate.edu>
   Pieter Swart <swart@lanl.gov>
