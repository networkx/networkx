NetworkX 2.8.5
==============

Release date: 18 July 2022

Supports Python 3.8, 3.9, and 3.10.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

Minor documentation and bug fixes.

Merged PRs
----------

- Bump release version
- Check that nodes have "pos" attribute in geometric_edges (#5707)
- Correct louvain formula, solve infinite loops (#5713)
- Add more comprehensive tests for pydot (#5792)
- Compute `is_strongly_connected` lazily (#5793)
- Compute `is_weakly_connected` lazily (#5795)
- Updated astar docstring (#5797)
- Fix typo in bipartite closeness_centrality and thought-o in tests (#5800)
- Fix pydot colon check node-to-str conversion (#5809)
- Temporary fix for failing tests w/ scipy1.9. (#5816)
- Update distance parameter description. (#5819)
- Fix #5817 (#5822)
- Attempt to reverse slowdown from hasattr  needed for cached_property (#5836)
- Update tests in base class and simple rename in convert.py (#5848)
- Move factory attributes to the class instead of instance. (#5850)
- Point to the latest URL for the description. (#5852)
- Gallery example: Morse code alphabet as a prefix tree (#5867)
- make lazy_import private and remove its internal use (#5878)
- Run CI against v2.8 branch
- CI: add explicit path while installing pygraphviz wheels on macOS in GHA (#5805)
- Deploy docs on v2.8 branch

Contributors
------------

- Ross Barnowski
- Shaked Brody
- Lior
- Jarrod Millman
- Tomoya Nishide
- Dimitrios Papageorgiou
- Dan Schult
- Matt Schwennesen
- Mridul Seth
- Matus Valo
