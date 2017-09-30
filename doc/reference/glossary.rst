.. _glossary:

Glossary
========

.. glossary::

   dictionary
      A Python dictionary maps keys to values. Also known as "hashes",
      or "associative arrays" in other programming languages.
      See https://docs.python.org/2/tutorial/datastructures.html#dictionaries

   edge
      Edges are either two-tuples of nodes `(u, v)` or three tuples of nodes
      with an edge attribute dictionary `(u, v, dict)`.

   ebunch
      An iteratable container of edge tuples like a list, iterator,
      or file.

   edge attribute
      Edges can have arbitrary Python objects assigned as attributes
      by using keyword/value pairs when adding an edge
      assigning to the `G.edges[u][v]` attribute dictionary for the
      specified edge *u*-*v*.

   hashable
      An object is hashable if it has a hash value which never changes
      during its lifetime (it needs a :meth:`__hash__` method), and can be
      compared to other objects (it needs an :meth:`__eq__` or :meth:`__cmp__`
      method). Hashable objects which compare equal must have the same
      hash value.

      Hashability makes an object usable as a dictionary key and a set
      member, because these data structures use the hash value internally.

      All of Python's immutable built-in objects are hashable, while no
      mutable containers (such as lists or dictionaries) are. Objects
      which are instances of user-defined classes are hashable by
      default; they all compare unequal, and their hash value is their
      :func:`id`.

      Definition from https://docs.python.org/2/glossary.html

   nbunch
      An nbunch is a single node, container of nodes or None (representing
      all nodes). It can be a list, set, graph, etc.. To filter an nbunch
      so that only nodes actually in `G` appear, use `G.nbunch_iter(nbunch)`.

   node
      A node can be any hashable Python object except None.

   node attribute
     Nodes can have arbitrary Python objects assigned as attributes
     by using keyword/value pairs when adding a node or
     assigning to the `G.nodes[n]` attribute dictionary for the
     specified node `n`.
