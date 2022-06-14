NetworkX 2.8.4
==============

Release date: 13 June 2022

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
- Clean up maximal_independent_set tests (#5567)
- MAINT: Cleanup centrality module, remove unused variables (#5308)
- importorskip scipy instead of numpy for total spanning tree (#5693)
- Add initial_graph parameter to scale_free_graph and deprecate create_using (#5697)
- Add docstring example for attr transfer to linegraph. (#5698)
- Update ISMAGS.analyze_symmetry docstring. (#5696)
- Add default value p=2 for minkowski distance metric. (#5700)
- Update inline code to inline math in docstring (#5701)
- Update multigraph docstrings to reflect `remove_edges_from` behavior. (#5699)
- Update simple_cycles docstring w/ yields and examples (#5709)
- Chromatic polynomial (#5675)
- Catch ':' explicitly while working with pydot (#5710)
- Revert "Add workaround for pytest failures on 3.11b2" (#5717)
- Default to lightmode for documentation (#5715)
- Dont compute all biconnected components in `is_biconnected()` (#5688)
- Some more changes to make pytest-randomly happy (#5719)
- Add durations flag to coverage run on CI. (#5718)
- Recover order of layers in multipartite_layout when layers are sortable (#5705)
- Update doc requirements (#5711)
- Touchups to MG and MDG edges docstrings. (#5708)
- Add PendingDeprecation for pydot (#5721)
- Add example of topo_order kwarg to dag_longest_path (#5728)
- CI: add pytest-randomly workflow. (#4553)

Contributors
------------

- Ross Barnowski
- Szabolcs Horvát
- Lucas H. McCabe
- Jarrod Millman
- Mridul Seth
- Matus Valo
