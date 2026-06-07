=======
Roadmap
=======

The roadmap is intended for larger, fundamental changes to
the project that are likely to take months or years of developer time.
Smaller-scoped items will continue to be tracked on our issue tracker.

The scope of these improvements means that these changes may be
controversial, are likely to involve significant discussion
among the core development team, and may require the creation
of one or more :ref:`nxep`.

Installation
------------

We aim to make NetworkX as easy to install as possible.
Some of our dependencies (e.g., graphviz) can be tricky to install.
Other of our dependencies are easy to install on the CPython platform, but
may be more involved on other platforms such as PyPy.
Addressing these installation issues may involve working with the external projects.

Sustainability
--------------

We aim to reduce barriers to contribution, speed up pull request (PR) review,
onboard new maintainers, and attract new developers to ensure the long-term
sustainability of NetworkX.

This includes:

- improving continuous integration
- making code base more approachable
- creating new pathways beyond volunteer effort
- growing maintainers and leadership
- increasing diversity of developer community

Benchmarks
----------

Speed improvements, lower memory usage, and the ability to parallelize
algorithms are beneficial to most science domains and use cases.
Toward that goal we want a benchmarking system using something
like airspeed velocity (https://asv.readthedocs.io/en/stable/).
See a fairly extensive version of this in ``benchmarks/benchmarks``.

Performance
-----------

Individual functions can be optimized for performance and memory use.
We are also interested in exploring new technologies to accelerate
code and reduce memory use. Before adopting any new technologies
we will need to carefully consider its impact on code readability
and difficulty of building and installing NetworkX.
For more information, see our :ref:`mission_and_values`.

Many functions can be trivially parallelized. ``nx-parallel``
(https://github.com/networkx/nx-parallel) is one possible approach
using backends. Python's new freethreading feature is a powerful
possibility.

Documentation
-------------

We’d like to improve the content, structure, and presentation of the NetworkX
documentation. Some specific goals include:

- examples that include short workflows for specific domains
- summary doc pages for suites of functions e.g. community with comparisons of
  functions and why you might pick one over another
- longer gallery examples or nx-guides, including complete life science workflows
- domain-specific documentation (NetworkX for Geneticists,
  NetworkX for Neuroscientists, etc.) probably as nx-guides
- examples of how to use NetworkX with other packages, e.g. Cytoscape

Linear Algebra
--------------

We would like to improve our linear algebra based algorithms.
This includes investigating SciPy's csgraph and possibly getting SciPy to support
a new sparse array format that uses a NX Graph as storage.
We should also decide how to handle algorithms with multiple implementations
(e.g., some algorithms are implemented in Python, NumPy, and SciPy).
Perhaps we can build off of NumPy's array-api to get e.g. PyTorch in our linalg.

Interoperability
----------------

We'd like to improve interoperability with the rest of the scientific Python
ecosystem.
This includes projects we depend on (e.g., NumPy, SciPy, Pandas, Matplotlib)
as well as ones we don't (e.g., Geopandas).

For example, we would also like to be able to seamlessly exchange graphs with
other network analysis software. Perhaps SciPy can support a sparse array format
that uses a NX Graph data structure.  Perhaps we can store all node and edge
attributes in a DataFrame without copy.

Another way to integrate with other scientific python ecosystem tools is to
take on features from the other tools that are useful. And we should develop
tools to ease use of NetworkX from within these other tools.
Additional examples of interoperability improvements may include providing a more
pandas-like interface for the ```__getitem__``` dunder function of node and
edge views (:ref:`NXEP2`).
Also developing a universal method to represent a graph as a single sequence of
```nodes_and_edges``` objects that allow attribute dicts, nodes and edges as
`discussed for graph generators
<https://github.com/networkx/networkx/issues/3036>`_.

Visualization
-------------

Visualization is not a primary focus on NetworkX, but it is a major feature for
many users. We need to enhance the drawing tools for NetworkX. We intend to
evolve to a new ``display`` function that enhances both api and performance relative
to the draw functions. We should also enhance docs to make connections with
iplotx and GraphViz.
