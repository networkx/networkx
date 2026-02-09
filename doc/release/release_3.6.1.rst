networkx 3.6.1
==============

We're happy to announce the release of networkx 3.6.1!

API Changes
-----------

- Add spectral bipartition community finding and greedy bipartition using node swaps (`#8347 <https://github.com/networkx/networkx/pull/8347>`_).

Enhancements
------------

- Nodelists for ``from_biadjacency_matrix`` (`#7993 <https://github.com/networkx/networkx/pull/7993>`_).
- Add spectral bipartition community finding and greedy bipartition using node swaps (`#8347 <https://github.com/networkx/networkx/pull/8347>`_).
- Fix draw_networkx_nodes with list node_shape and add regression test (`#8363 <https://github.com/networkx/networkx/pull/8363>`_).

Bug Fixes
---------

- Fix: allow graph subclasses to have additional arguments (`#8369 <https://github.com/networkx/networkx/pull/8369>`_).

Documentation
-------------

- DOC: Improve benchmarking readme (`#8358 <https://github.com/networkx/networkx/pull/8358>`_).
- DOC: More details re: RC releases in the release process devdocs (`#8346 <https://github.com/networkx/networkx/pull/8346>`_).
- DOC: clarify difference between G.nodes/G.nodes() and G.edges/G.edges() in tutorial (`#8300 <https://github.com/networkx/networkx/pull/8300>`_).
- DOC: Add blurb to contributor guide about drawing tests (`#8370 <https://github.com/networkx/networkx/pull/8370>`_).
- DOC: Fix underline lens in docstrings (`#8371 <https://github.com/networkx/networkx/pull/8371>`_).
- Rolling back shortest paths links (`#8373 <https://github.com/networkx/networkx/pull/8373>`_).

Maintenance
-----------

- MAINT: Replace string literal with comment (`#8359 <https://github.com/networkx/networkx/pull/8359>`_).
- Bump actions/checkout from 5 to 6 in the actions group (`#8360 <https://github.com/networkx/networkx/pull/8360>`_).
- pin python 3.14 to be version 3.14.0 until dataclasses are fixed (`#8365 <https://github.com/networkx/networkx/pull/8365>`_).
- Blocklist Python 3.14.1 (`#8372 <https://github.com/networkx/networkx/pull/8372>`_).

Other
-----

- TST: add tests for unsupported graph types in MST algorithms (`#8353 <https://github.com/networkx/networkx/pull/8353>`_).
- TST: clean up isomorphism tests (`#8364 <https://github.com/networkx/networkx/pull/8364>`_).

Contributors
------------

10 authors added to this release (alphabetically):

- `@Aka2210 <https://github.com/Aka2210>`_
- `@jfinkels <https://github.com/jfinkels>`_
- `@NaorTIRAM <https://github.com/NaorTIRAM>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- Alejandro Candioti (`@amcandio <https://github.com/amcandio>`_)
- Colman Bouton (`@LorentzFactor <https://github.com/LorentzFactor>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)

9 reviewers added to this release (alphabetically):

- `@Aka2210 <https://github.com/Aka2210>`_
- Aditi Juneja (`@Schefflera-Arboricola <https://github.com/Schefflera-Arboricola>`_)
- Alejandro Candioti (`@amcandio <https://github.com/amcandio>`_)
- Colman Bouton (`@LorentzFactor <https://github.com/LorentzFactor>`_)
- Dan Schult (`@dschult <https://github.com/dschult>`_)
- Erik Welch (`@eriknw <https://github.com/eriknw>`_)
- Gilles Peiffer (`@Peiffap <https://github.com/Peiffap>`_)
- Mridul Seth (`@MridulS <https://github.com/MridulS>`_)
- Ross Barnowski (`@rossbar <https://github.com/rossbar>`_)

_These lists are automatically generated, and may not be complete or may contain
duplicates._

