.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   edge
      Edges are either two-tuples of nodes (u,v) or three tuples
      of nodes with an edge attribute dictionary (u,v,dict).
     
   ebunch
      An iteratable container of edge tuples like a list, iterator,
      or file.

   edge attribute
      Edges can have arbitrary Python objects assigned as attributes
      by using keyword/value pairs when adding an edge
      assigning to the G.edge[u][v] attribute dictionary for the
      specified edge u-v.

   hashable
      An object is hashable if it has a hash value which never changes
      during its lifetime (it needs a __hash__() method), and can be
      compared to other objects (it needs an __eq__() or __cmp__()
      method). Hashable objects which compare equal must have the same
      hash value.

      Hashability makes an object usable as a dictionary key and a set
      member, because these data structures use the hash value internally.

      All of Python's immutable built-in objects are hashable, while no
      mutable containers (such as lists or dictionaries) are. Objects
      which are instances of user-defined classes are hashable by
      default; they all compare unequal, and their hash value is their
      id().
    
      Definition from http://docs.python.org/glossary.html

   nbunch
      An nbunch is any iterable container of nodes that is not itself
      a node in the graph. It can be an iterable or an iterator,
      e.g. a list, set, graph, file, etc..

   node attribute
     Nodes can have arbitrary Python objects assigned as attributes
     by using keyword/value pairs when adding a node or
     assigning to the G.node[n] attribute dictionary for the
     specified node n.
      
   node
      A node can be any hashable Python object except None.
      
   dictionary
      A Python dictionary maps keys to values.  Also known as "hashes",
      or "associative arrays".
      See http://docs.python.org/tutorial/datastructures.html#dictionaries


