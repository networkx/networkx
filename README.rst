NetworkX
========


.. image::
    https://github.com/networkx/networkx/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/networkx/networkx/actions/workflows/test.yml

.. image::
    https://img.shields.io/pypi/v/networkx.svg?
    :target: https://pypi.python.org/pypi/networkx

.. image::
    https://img.shields.io/pypi/l/networkx.svg?
    :target: https://github.com/networkx/networkx/blob/main/LICENSE.txt

.. image::
    https://img.shields.io/pypi/pyversions/networkx.svg?
    :target: https://pypi.python.org/pypi/networkx

.. image::
    https://img.shields.io/github/labels/networkx/networkx/good%20first%20issue?color=green&label=contribute
    :target: https://github.com/networkx/networkx/contribute

.. image::
    https://insights.linuxfoundation.org/api/badge/health-score?project=networkx
    :target: https://insights.linuxfoundation.org/project/networkx


NetworkX is a Python package for the creation, manipulation,
and study of the structure, dynamics, and functions
of complex networks.

- **Website (including documentation):** https://networkx.org
- **Mailing list:** https://groups.google.com/forum/#!forum/networkx-discuss
- **Source:** https://github.com/networkx/networkx
- **Bug reports:** https://github.com/networkx/networkx/issues
- **Report a security vulnerability:** https://tidelift.com/security
- **Tutorial:** https://networkx.org/documentation/latest/tutorial.html
- **GitHub Discussions:** https://github.com/networkx/networkx/discussions
- **Discord (Scientific Python) invite link:** https://discord.com/invite/vur45CbwMz
- **NetworkX meetings calendar (open to all):** https://scientific-python.org/calendars/networkx.ics

Simple example
--------------

Find the shortest path between two nodes in an undirected graph:

.. code:: pycon

    >>> import networkx as nx
    >>> G = nx.Graph()
    >>> G.add_edge("A", "B", weight=4)
    >>> G.add_edge("B", "D", weight=2)
    >>> G.add_edge("A", "C", weight=3)
    >>> G.add_edge("C", "D", weight=4)
    >>> nx.shortest_path(G, "A", "D", weight="weight")
    ['A', 'B', 'D']

Install
-------

Install the latest released version of NetworkX:

.. code:: shell

    $ pip install networkx

Install with all optional dependencies:

.. code:: shell

    $ pip install networkx[default]

For additional details,
please see the `installation guide <https://networkx.org/documentation/stable/install.html>`_.

Bugs
----

Please report any bugs that you find `here <https://github.com/networkx/networkx/issues>`_.
Or, even better, fork the repository on `GitHub <https://github.com/networkx/networkx>`_
and create a pull request (PR). We welcome all changes, big or small, and we
will help you make the PR if you are new to `git` (just ask on the issue and/or
see the `contributor guide <https://networkx.org/documentation/latest/developer/contribute.html>`_).

License
-------

Released under the `3-clause BSD license <https://github.com/networkx/networkx/blob/main/LICENSE.txt>`_::

    Copyright (c) 2004-2025, NetworkX Developers
    Aric Hagberg <hagberg@lanl.gov>
    Dan Schult <dschult@colgate.edu>
    Pieter Swart <swart@lanl.gov>
