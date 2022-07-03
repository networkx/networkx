Mentored Projects
==================

This page maintains a list of mentored project ideas that contributors can work
on if they are interested in contributing to the NetworkX project. Feel free to
suggest any other idea if you are interested on the
`NetworkX GitHub discussions page <https://github.com/networkx/networkx/discussions>`__

These ideas can be used as projects for Google Summer of Code, Outreachy,
NumFOCUS Small Development Grants and university course/project credits (if
your university allows contribution to open source for credit).


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
  
- Expected time commitment: This project can be either a medium project (~175 hours)
  or a large project (~350 hours). The contributor is expected to contribute 2-3
  pedagogical interactive notebooks for the medium duration project and 4-5 notebooks
  for the long duration project.

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

- Expected time commitment: Long project (~350 hours)

Completed Projects
==================

- `Louvain community detection algorithm`_ 
    - Program: Google Summer of Code 2021
    - Contributor: `@z3y50n <https://github.com/z3y50n/>`__
    - Link to Proposal:  `GSoC 2021: Community Detection Algorithms <https://github.com/networkx/archive/blob/main/proposals-gsoc/GSoC-2021-Community-Detection-Algorithms.pdf>`__ 

- `Asadpour algorithm for directed travelling salesman problem`_
    - Program: Google Summer of Code 2021
    - Contributor: `@mjschwenne <https://github.com/mjschwenne/>`__
    - Link to Proposal:  `GSoC 2021: Asadpour algorithm <https://github.com/networkx/archive/blob/main/proposals-gsoc/GSoC-2021-Asadpour-Asymmetric-Traveling%20Salesman-Problem.pdf>`__ 

- Pedagogical notebook: `Directed acyclic graphs and topological sort`_
    - Program: Google Summer of Code 2021
    - Contributor:  `@vdshk <https://github.com/vdshk>`__

- Pedagogical notebooks: `Graph assortativity`_ & `Network flow analysis and Dinitz algorithm`_
    - Program: Google Summer of Code 2021
    - Contributor: `@harshal-dupare <https://github.com/harshal-dupare/>`__

- Add On system for NetworkX: `NetworkX-Metis`_
    - Program: Google Summer of Code 2015
    - Contributor: `@OrkoHunter <https://github.com/OrkoHunter/>`__
    - Link to Proposal:  `GSoC 2015: Add On System for NetworkX <https://github.com/networkx/archive/blob/main/proposals-gsoc/GSoC-2015-Add-on-system-for-NetworkX.md>`__

- `NetworkX 2.0 API`_
    - Program: Google Summer of Code 2015
    - Contributor: `@MridulS <https://github.com/MridulS/>`__
    - Link to Proposal: `GSoC 2015: NetworkX 2.0 API <https://github.com/networkx/archive/blob/main/proposals-gsoc/GSoC-2015-NetworkX-2.0-api.md>`__

.. _`Louvain community detection algorithm`: https://github.com/networkx/networkx/pull/4929
.. _`Asadpour algorithm for directed travelling salesman problem`: https://github.com/networkx/networkx/pull/4740
.. _`Directed acyclic graphs and topological sort`: https://github.com/networkx/nx-guides/pull/44
.. _`Graph assortativity`: https://github.com/networkx/nx-guides/pull/42
.. _`Network flow analysis and Dinitz algorithm`: https://github.com/networkx/nx-guides/pull/46
.. _`NetworkX-Metis`: https://github.com/networkx/networkx-metis
.. _`NetworkX 2.0 API`: https://networkx.org/documentation/latest/release/migration_guide_from_1.x_to_2.0.html

..
   Project Idea Template
   ---------------------
   
   - Abstract:
   
   - Recommended Skills:
   
   - Expected Outcome:
   
   - Complexity;
   
   - Interested Mentors:
   
