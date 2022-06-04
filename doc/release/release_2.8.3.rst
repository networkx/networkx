NetworkX 2.8.3
==============

Release date: 4 June 2022

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
- Update release process
- added example to closeness.py (#5645)
- Extract valid kwds from the function signature for draw_networkx_* (#5660)
- Error out when pydot fails to correctly parse node names (#5667)
- Remove redundant py2 numeric conversions (#5661)
- Correcting a typo in the references (#5677)
- Add workaround for pytest failures on 3.11-beta2 (#5680)
- Moved random_spanning_tree to public API (#5656)
- More tests for clustering (upstreaming from graphblas-algorithms) (#5673)
- Remove unused logic in nonisomorphic_trees (#5682)
- equitable_coloring: Get lazily first item instead of creating whole list (#5668)
- Update subgraph views tests to pass with out of order execution (#5683)
- Use isort with pre-commit to enforce import guidelines (#5659)
- ignore isort commit from git blame (#5684)
- Another catch by pytest-randomly (#5685)
- Remove unused file from utils.test (#5687)
- Update release requirements (#5690)
- Update developer requirements (#5689)
- Fix old release notes

Contributors
------------

- Ross Barnowski
- Jon Crall
- Lukong123
- Jarrod Millman
- RATCOinc
- Matt Schwennesen
- Mridul Seth
- Matus Valo
- Erik Welch
