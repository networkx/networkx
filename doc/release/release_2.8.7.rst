NetworkX 2.8.7
==============

Release date: TBD

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


Improvements
------------

- [`#5943 <https://github.com/networkx/networkx/pull/5943>`_]
  ``is_path`` used to raise a `KeyError` when the ``path`` argument contained
  a node that was not in the Graph. The behavior has been updated so that
  ``is_path`` returns `False` in this case rather than raising the exception.

Contributors
------------

