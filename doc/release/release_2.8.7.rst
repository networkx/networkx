NetworkX 2.8.7
==============

Release date: 2 October 2022

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

A total of 12 changes have been committed.

- Further improvements to strategy_saturation_largest_first (#5935)
- Arf layout (#5910)
- [ENH] Find and verify a minimal D-separating set in DAG (#5898)
- Add Mehlhorn Steiner approximations (#5629)
- Updated networkx/classes/function.py . Solves Issue #5463 (#5474)
- Improved documentation for all_simple_paths (#5944)
- Change is_path to return False when node not in G instead of raising exception (#5943)
- Preliminary VF2++ Implementation (#5788)
- Minor docstring touchups and test refactor for `is_path` (#5967)
- Update documentation header links for latest pydata-sphinx-theme (#5966)
- Switch to relative import for vf2pp_helpers. (#5973)
- Add vf2pp_helpers subpackage to wheel (#5975)
- Enhance biconnected components to avoid indexing (#5974)
- Update mentored projects list (#5985)
- Add concurrency hook to cancel jobs on new push. (#5986)
- Make all.py generator friendly (#5984)
- Fix failing example due to mpl 3.6 colorbar. (#5994)
- Only run scheduled pytest-randomly job in main repo. (#5993)
- Fix steiner tree test (#5999)
- Add Tidelift security vulnerability link (#6001)
- Update linters (#6006)

Contributors
------------

- 0ddoe_s
- Guy Aglionby
- Ross Barnowski
- Casper van Elteren
- Adam Li
- Jarrod Millman
- Konstantinos Petridis
- Dan Schult
- Morrison Turnansky
- George Watkins
- ddelange
- pmlpm1986
