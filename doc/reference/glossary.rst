.. _glossary:

Glossary
========

.. glossary::

   dictionary
      A Python dictionary maps keys to values. Also known as "hashes",
      or "associative arrays" in other programming languages.
      See :ref:`the Python tutorial on dictionaries <tut-dictionaries>`.

   edge
      Edges are either two-tuples of nodes `(u, v)` or three tuples of nodes
      with an edge attribute dictionary `(u, v, dict)`.

   ebunch
      An iterable container of edge tuples like a list, iterator,
      or file.

   edge attribute
      Edges can have arbitrary Python objects assigned as attributes
      by using keyword/value pairs when adding an edge
      assigning to the `G.edges[u][v]` attribute dictionary for the
      specified edge *u*-*v*.

   nbunch
      An nbunch is a single node, container of nodes or `None` (representing
      all nodes). It can be a list, set, graph, etc. To filter an nbunch
      so that only nodes actually in ``G`` appear, use ``G.nbunch_iter(nbunch)``.

      If the nbunch is a container or iterable that is not itself a node
      in the graph, then it will be treated as an iterable of nodes, for
      instance, when nbunch is a string or a tuple::

         >>> import networkx as nx
         >>> G = nx.DiGraph()
         >>> G.add_edges_from([("b", "c"), ("a", "ab"), ("ab", "c")])
         >>> G.edges("ab")
         OutEdgeDataView([('ab', 'c')])
      
      Since "ab" is a node in G, it is treated as a single node::

         >>> G.edges("bc")
         OutEdgeDataView([('b', 'c')])

      Since "bc" is not a node in G, it is treated as an iterator::

         >>> G.edges(["bc"])
         OutEdgeDataView([])

      If "bc" is wrapped in a list, the list is the iterable and
      "bc" is treated as a single node. That is, if the
      nbunch is an iterable of iterables, the inner iterables will
      always be treated as nodes::

         >>> G.edges("de")
         OutEdgeDataView([])

      When nbunch is an iterator that is not itself a node and none of 
      its elements are nodes, then the edge view suite of methods return
      an empty edge view.

   node
      A node can be any hashable Python object except None.

   node attribute
     Nodes can have arbitrary Python objects assigned as attributes
     by using keyword/value pairs when adding a node or
     assigning to the `G.nodes[n]` attribute dictionary for the
     specified node `n`.
