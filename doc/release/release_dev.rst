Next Release
============

Release date: TBD

Supports Python 3.8, 3.9, and ...

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:

.. warning::
   Hash values observed in outputs of 
   `~networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash`
   have changed in version 2.7 due to bug fixes. See gh-4946_ for details.
   This means that comparing hashes of the same graph computed with different
   versions of NetworkX (i.e. before and after version 2.7)
   could wrongly fail an isomorphism test (isomorphic graphs always have matching
   Weisfeiler-Lehman hashes). Users are advised to recalculate any stored graph
   hashes they may have on upgrading.

.. _gh-4946: https://github.com/networkx/networkx/pull/4946#issuecomment-914623654

- Dropped support for Python 3.7.

Improvements
------------


API Changes
-----------

- The values in the dictionary returned by
  `~networkx.drawing.layout.rescale_layout_dict` are now `numpy.ndarray` objects
  instead of tuples. This makes the return type of ``rescale_layout_dict``
  consistent with that of all of the other layout functions.

Deprecations
------------

- [`#5055 <https://github.com/networkx/networkx/pull/5055>`_]
  Deprecate the ``random_state`` alias in favor of ``np_random_state``
- [`#5114 <https://github.com/networkx/networkx/pull/5114>`_]
  Deprecate the ``name`` kwarg from ``union`` as it isn't used.
- [`#5143 <https://github.com/networkx/networkx/pull/5143>`_]
  Deprecate ``euclidean`` in favor of ``math.dist``.


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
