GEXF
====
.. automodule:: networkx.readwrite.gexf
.. autosummary::
   :toctree: generated/

   read_gexf
   write_gexf
   generate_gexf
   relabel_gexf_graph

List attributes
---------------

GEXF 1.3 supports typed list attributes on nodes and edges. To write a static
list, use a Python list of values of the same type and select ``version="1.3"``::

    >>> import io
    >>> G = nx.Graph()
    >>> G.add_node("alice", interests=["graph theory", "data, visualization"])
    >>> G.add_edge("alice", "bob", counts=[1, 2, 3])
    >>> stream = io.BytesIO()
    >>> nx.write_gexf(G, stream, version="1.3")
    >>> stream.seek(0)
    0
    >>> H = nx.read_gexf(stream)
    >>> H.nodes["alice"]["interests"]
    ['graph theory', 'data, visualization']
    >>> H.edges["alice", "bob"]["counts"]
    [1, 2, 3]

The writer supports lists of strings, booleans, integers, floating-point numbers
and :class:`decimal.Decimal` values. Strings are quoted and escaped to preserve
commas, quotes, backslashes and whitespace. Values within a list, and nonempty
lists assigned to the same attribute, must have consistent types. Empty lists
use the type of other values of that attribute or its default; if all values
are empty, the attribute is written as ``liststring``. The input graph is not
modified.

The reader converts GEXF 1.3 list types into Python lists, including attribute
defaults and time-varying list values. Integer list types become Python
integers, floating-point list types become Python floats, and ``listbigdecimal``
values become :class:`decimal.Decimal` instances.

Time-varying attributes retain the existing representation as a list of
``(value, start, end)`` triples. A time-varying list attribute therefore uses a
list as each triple's value, for example ``[([1, 2], 0, 1), ([3, 4], 1, 2)]``.
Lists of three-element lists or tuples are interpreted as time-varying
attributes, rather than as nested static lists.

The default output version is still ``1.2draft``. Static Python list support
requires explicitly selecting version 1.3. Reading ``liststring`` attributes
from GEXF 1.1 and 1.2 files continues to return the original string.

