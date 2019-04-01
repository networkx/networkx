**********************************
Version 1.11 notes and API changes
**********************************

This page includes more detailed release information and API changes from
NetworkX 1.10 to NetworkX 1.11.

Please send comments and questions to the networkx-discuss mailing list:
<http://groups.google.com/group/networkx-discuss>.

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
