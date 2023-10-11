NetworkX 2.8.7
==============

Release date: 1 October 2022

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
- Fixed unused root argument in has_bridges (#5846)
- docstring updates for `union`, `disjoint_union`, and `compose` (#5892)
- Updated networkx/classes/function.py . Solves Issue #5463 (#5474)
- Improved documentation for all_simple_paths (#5944)
- Change is_path to return False when node not in G instead of raising exception (#5943)
- Minor docstring touchups and test refactor for `is_path` (#5967)
- Update documentation header links for latest pydata-sphinx-theme (#5966)
- Fix failing example due to mpl 3.6 colorbar. (#5994)
- Add Tidelift security vulnerability link (#6001)
- Update linters (#6006)

Improvements
------------

- [`#5943 <https://github.com/networkx/networkx/pull/5943>`_]
  ``is_path`` used to raise a `KeyError` when the ``path`` argument contained
  a node that was not in the Graph. The behavior has been updated so that
  ``is_path`` returns `False` in this case rather than raising the exception.

Contributors
------------

- Juanita Gomez
- Kevin Brown
- 0ddoes
- pmlpm1986
- Dan Schult
- Jarrod Millman
