Mentored Projects
==================

This page maintains a list of mentored project ideas that contributors can work
on if they are interested in contributing to the NetworkX project. Feel free to
suggest any other idea if you are interested on the
`NetworkX GitHub discussions page <https://github.com/networkx/networkx/discussions>`__

These ideas can be used as projects for Google Summer of Code, Outreachy,
NumFOCUS Small Development Grants and university course/project credits (if
your university allows contribution to open source for credit).


Community Detection Algorithms
--------------------------------

- Abstract: Community detection involves a set of algorithms in network science which
  deal with grouping nodes from a network according to their similar properties
  such as belonging to dense clusters. NetworkX already contains a
  :mod:`variety of community detection algorithms <networkx.algorithms.community>`
  dealing with computing the community structure of a network. There are also
  multiple PRs/issues which deal with adding the Louvain community detection
  algorithm to NetworkX, e.g. `#1090`_, `#1092`_ `#951`_. Users who want to work with
  NetworkX and Louvain Community Detection often use
  https://github.com/taynaud/python-louvain. This project would focus on getting
  Louvain community detection algorithms implemented into NetworkX.

- Recommended Skills: Python, graph algorithms

- Expected Outcome: We would like to see Louvain community detection
  implemented inside NetworkX, or construct code and documented examples
  in NetworkX that would interface with other Louvain projects.

- Complexity: Moderate

- Interested Mentors: `@dschult <https://github.com/dschult/>`__,
  `@MridulS <https://github.com/MridulS/>`__,

.. _#1090: https://github.com/networkx/networkx/pull/1090
.. _#1092: https://github.com/networkx/networkx/pull/1092
.. _#951: https://github.com/networkx/networkx/issues/951


Pedagogical Interactive Notebooks for Algorithms Implemented in NetworkX
------------------------------------------------------------------------

- Abstract: NetworkX has a :ref:`wide variety of algorithms <Algorithms>`
  implemented. Even though the algorithms are well documented, explanations of
  the ideas behind the algorithms are often missing and we would like to
  collect these, write Jupyter notebooks to elucidate these ideas and explore
  the algorithms experimentally, and publish the notebooks at
  https://github.com/networkx/notebooks. The goal is to gives readers a
  deeper outlook behind standard network science and graph theory algorithms
  and encourage them to delve further into the topic.

- Recommended Skills: Python, Jupyter notebooks, graph algorithms.

- Expected Outcome: A collection of Interactive Jupyter notebooks which
  explain and explore network algorithms to readers and users of NetworkX.
  For example, see this notebook on
  :doc:`Random Geometric Graphs <content/generators/geometric>`

- Complexity: Depending on the algorithms you are interested to work on.

- Interested Mentors: `@dschult <https://github.com/dschult/>`__,
  `@MridulS <https://github.com/MridulS/>`__,
  `@rossbar <https://github.com/rossbar/>`__

Directed Version of Traveling Salesman Problem
----------------------------------------------

- Abstract: NetworkX has recently added a couple methods for solving
  the Traveling Salesman Problem (see `#4607`_). The best approximation
  for undirected graphs is the Christofides method. But the best algorithm
  for directed graphs is by `Asapour`_ et.al. and has not yet been implemented.
  The goal of this project is to learn the API used for implemented methods
  and then implement the Asadpour method for directed graphs with similar API.
  Other even more recent papers discussing algorithm improvements for directed
  TSP (also called Asymmetric TSP or ATSP) include `Svensson`_ and `Traub`_.
  The Traub paper may be most useful for implementing the algorithm as all three
  are focused on proving asymptotic computation requirements rather than coding.

- Recommended Skills: Python, graph algorithms

- Expected Outcome: A new function in NetworkX which implements the Asapour algorithm.

- Complexity: Moderate

- Interested Mentors: `@dschult <https://github.com/dschult/>`__,
  `@MridulS <https://github.com/MridulS/>`__, `@boothby <https://github.com/boothby/>`__,

.. _#4607: https://github.com/networkx/networkx/pull/4607
.. _Asapour: https://pubsonline.informs.org/doi/pdf/10.1287/opre.2017.1603
.. _Svensson: https://doi.org/10.1109/FOCS.2015.10  (https://arxiv.org/abs/1502.02051)
.. _Traub: https://doi.org/10.1145/3357713.3384233 (https://arxiv.org/abs/1912.00670)


Implement the VF2++ Graph Isomorphism Algorithm
-----------------------------------------------

- Abstract: The `Graph Isomorphism Problem`_ is a famous difficult network problem at
  the boundary between P and NP-Complete. The VF2 algorithm is included with NetworkX
  in a recursive formulation. There is an improved version of this algorithm called
  `VF2++`_ which we intend to implement. We have early attempts at a nonrecursive version
  of the main algorithm that also address subgraph isomorphism and subgraph monomorphism.
  This project involves fully implementing them and extending to directed and multigraph
  settings.

- Recommended Skills: Python, graph algorithms

- Expected Outcome: A new set of functions in NetworkX that implement the VF2++
  algorithm for all problem and graph types in a nonrecursive manner.

- Complexity: Moderate

- Interested Mentors: `@dschult <https://github.com/dschult/>`__,
  `@MridulS <https://github.com/MridulS/>`__, `@boothby <https://github.com/boothby/>`__,

.. _`Graph Isomorphism Problem`: https://en.wikipedia.org/wiki/Graph_isomorphism_problem
.. _VF2++: https://doi.org/10.1016/j.dam.2018.02.018


Project Idea Template
---------------------

- Abstract:

- Recommended Skills:

- Expected Outcome:

- Complexity;

- Interested Mentors:

