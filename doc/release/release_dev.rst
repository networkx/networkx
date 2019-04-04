Announcement: NetworkX 2.3
==========================

We're happy to announce the release of NetworkX 2.3!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<https://networkx.github.io/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 5 months of work with over 92 pull requests by
30 contributors. Highlights include:

- Dropped support for Python 2. Most of the code will still work in the short term,
  but we are no longer supporting Python 2.7 and we will start changing code to take
  advantage of Python 3 features we couldn't before.
- Added some Moral Graph analysis functions.
- Enable matplotlib drawing using curved arrows via connectionstyle parameter.
- Remove ticks and axes labels from matplotlib plots.
- Two new generators of Harary Graphs.
- Added Dual Barabasi-Albert model
- Added VoteRank algorithm
- Added Equitable coloring algorithms
- Added planar layout algorithms
- Les Miserables network example
- Javascript example update

Improvements
------------

- change default colors to be color-blind friendly
- Many bug fixes and documentation improvements
- speed up of simple_cycles
- improvements for reading various formats like GML, GEXF, Graphml
- allow subclassing to access node_attr_dict_factory


API Changes
-----------
- The G.fresh_copy() mechanism for creating an empty_graph of the same
  type (introduced in v2.0) does not playing nicely with pickle and others.
  So, we have removed the code that caused a need for that. Instead you
  should use the more natural G.__class__() syntax to get an empty_graph
  of the same type as G.

Deprecations
------------
- The Graph.fresh_copy() method should now use Graph.__class__()
- ReverseView class removed in favor of reverse_view() function.

Contributors to this release
----------------------------

- Mike Babst
- Jonathan Barnoud
- Scott Chow
- Jon Crall
- Clayton A Davis
- Michaël Defferrard
- Fredrik Erlandsson
- Eyal
- Tanay Gahlot
- Matthew Gilbert
- Øyvind Heddeland Instefjord
- Hongwei Jin
- Kieran
- Dongkwan Kim
- Julien Klaus
- Warren W. Kretzschmar
- Elias Kuthe
- Eric Ma
- Christoph Martin
- Jarrod Millman
- Issa Moradnejad
- Moradnejad
- Niema Moshiri
- Ramil Nugmanov
- Jens P
- Benjamin Peterson
- Edward L Platt
- Matteo Pozza
- Antoine Prouvost
- Mickaël Schoentgen
- Dan Schult
- Johannes Schulte
- Mridul Seth
- Weisheng Si
- Utkarsh Upadhyay
- damianos
- guidoeco
- jeanfrancois8512
- komo-fr
- last2sword
