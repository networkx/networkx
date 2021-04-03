NetworkX
========

.. image:: https://img.shields.io/pypi/v/networkx.svg
   :target: https://pypi.org/project/networkx/

.. image:: https://img.shields.io/pypi/pyversions/networkx.svg
   :target: https://pypi.org/project/networkx/

.. image:: https://github.com/networkx/networkx/workflows/test/badge.svg?branch=main
  :target: https://github.com/networkx/networkx/actions?query=workflow%3A%22test%22

.. image:: https://codecov.io/gh/networkx/networkx/branch/main/graph/badge.svg
   :target: https://app.codecov.io/gh/networkx/networkx/branch/main
   
.. image:: https://img.shields.io/github/labels/networkx/networkx/Good%20First%20Issue?color=green&label=Contribute%20&style=flat-square
   :target: https://github.com/networkx/networkx/issues?q=is%3Aopen+is%3Aissue+label%3A%22Good+First+Issue%22
   

NetworkX is a Python package for the creation, manipulation,
and study of the structure, dynamics, and functions
of complex networks.

- **Website (including documentation):** https://networkx.org
- **Mailing list:** https://groups.google.com/forum/#!forum/networkx-discuss
- **Source:** https://github.com/networkx/networkx
- **Bug reports:** https://github.com/networkx/networkx/issues
- **Tutorial:** https://networkx.org/documentation/latest/tutorial.html
- **GitHub Discussions:** https://github.com/networkx/networkx/discussions

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

   Copyright (C) 2004-2021 NetworkX Developers
   Aric Hagberg <hagberg@lanl.gov>
   Dan Schult <dschult@colgate.edu>
   Pieter Swart <swart@lanl.gov>
