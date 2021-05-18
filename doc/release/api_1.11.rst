NetworkX 1.11
=============

Release date: 30 January 2016

Support for Python 3.5 added, drop support for Python 3.2.

Highlights
~~~~~~~~~~

Pydot features now use pydotplus.
Fixes installation on some machines and test with appveyor.
Restores default center and scale of layout routines.
Fixes various docs including no symbolic links in examples.
Docs can now build using autosummary on readthedocs.org.

API changes
-----------
* [`#1930 <https://github.com/networkx/networkx/pull/1930>`_]
  No longer import nx_agraph and nx_pydot into the top-level namespace.
  They can be accessed within networkx as e.g. ``nx.nx_agraph.write_dot``
  or imported as ``from networkx.drawing.nx_agraph import write_dot``.

* [`#1750 <https://github.com/networkx/networkx/pull/1750>`_]
  Arguments center and scale are now available for all layout functions.
  The defaul values revert to the v1.9 values (center is the origin
  for circular layouts and domain is [0, scale) for others.

* [`#1924 <https://github.com/networkx/networkx/pull/1924>`_]
  Replace pydot with pydotplus for drawing with the pydot interface.

* [`#1888 <https://github.com/networkx/networkx/pull/1888>`_]
  Replace support for Python3.2 with support for Python 3.5.

Miscellaneous changes
---------------------

* [`#1763 <https://github.com/networkx/networkx/pull/1763>`_]
  Set up appveyor to automatically test installation on Windows machines.
  Remove symbolic links in examples to help such istallation.

Change many doc_string typos to allow sphinx
to build the docs without errors or warnings.

Enable the docs to be automatically built on
readthedocs.org by changing requirements.txt
