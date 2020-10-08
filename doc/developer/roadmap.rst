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
Some of our dependencies (e.g., graphviz and gdal) can be tricky to install.
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

Performance
-----------

Speed improvements, lower memory usage, and the ability to parallelize
algorithms are beneficial to most science domains and use cases.

A first step may include implementing a benchmarking system using something
like airspeed velocity (https://asv.readthedocs.io/en/stable/).
It may also include review existing comparisons between NetworkX
and other packages.

Individual functions can be optimized for performance and memory use.
We are also interested in exploring new technologies to accelerate
code and reduce memory use.  Before adopting any new technologies
we will need to careful consider its impact on code readability
and difficulty of building and installating NetworkX.
For more information, see our :ref:`mission_and_values`.

Many functions can be trivially parallelized.
But, we need to decide on an API and perhaps implement some
helper code to make it consistent.

Documentation
-------------

We’d like to improve the content, structure, and presentation of the NetworkX
documentation. Some specific goals include:

- longer gallery examples
- domain-specific documentation (NetworkX for Geneticists,
  NetworkX for Neuroscientists, etc.)
- examples of how to use NetworkX with other packages

Linear Algebra
--------------

We would like to improve our linear algebra based algorithms.
The code is old and needs review and refactoring.
This would include investigating SciPy's csgraph.
It would also include deciding how to handle algorithms that
have multiple implementations (e.g., some algorithms are implemented in Python,
NumPy, and SciPy).

NumPy has split its API from its execution engine with ``__array_function__`` and
``__array_ufunc__``. This will enable parts of NumPy to accept distributed arrays
(e.g. dask.array.Array) and GPU arrays (e.g. cupy.ndarray) that implement the
ndarray interface. At the moment it is not yet clear which algorithms will work
out of the box, and if there are significant performance gains when they do.

Interoperability
----------------

We'd like to improve interoperability with the rest of the scientific Python
ecosystem.
This includes projects we depend on (e.g., NumPy, SciPy, Pandas, Matplotlib)
as well as ones we don't (e.g., Geopandas).

For example, we would also like to be able to seamlessly exchange graphs with
other network analysis software.
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

Visualization is not a focus on NetworkX, but it is a major feature for
many users.
We need to enhance the drawing tools for NetworkX.
