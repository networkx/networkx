Next Release
============

Release date: TBD

Supports Python ...

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

Warning: Hash values observed in outputs of `weisfeiler_lehman_graph_hash` 
have changed from version 2.6 -> 2.7 onwards, due to bug fixes 
[discussed here](https://github.com/networkx/networkx/pull/4946#issuecomment-914623654). 
This means that comparing graph hashes of hashes before and after version 2.7 
could wrongly fail an isomorphism test (isomorphicgraphs always have matching 
Weisfeiler-Lehman hashes). Users are advised to recalculate any stored graph 
hashes they may have on upgrading.

Improvements
------------


API Changes
-----------


Deprecations
------------


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
