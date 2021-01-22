.. _contributing_faq:

Contributing FAQ
****************

A collection of frequently-asked questions related to open-source development
and contributing to NetworkX.

Q: I'm new to open source and would like to contribute to NetworkX. How do I get started?
-----------------------------------------------------------------------------------------

To contribute to NetworkX, you will need three things:

  1. The source code
  2. a development environment
  3. an idea of what you'd like to contribute

Steps 1 & 2 are covered extensively in :ref:`Development Workflow <dev_workflow>`.
There is no generic answer for step 3. There are many ways that NetworkX can
be improved, from adding new algorithms, improving existing algorithms,
improving the test suite (e.g. increasing test coverage), and improving the
documentation.
The "best" way to find a place to start is to follow your own personal
interests!

Q: How do I contribute an example to the Gallery?
-------------------------------------------------

The example gallery is great place to contribute, particularly if you have an
interesting application or visualization that uses NetworkX.
The gallery is generated using sphinx-gallery from Python scripts stored in
the ``examples/`` directory.

Example
~~~~~~~

Let's say I'd like to contribute an example of visualizing a complete Graph
using a circular layout.
Assuming you have already followed the procedure for
:ref:`setting up a development environment <dev_workflow>`, start by
creating a new branch:

.. note:: It's generally a good idea to give your branch a descriptive name so
   that it's easy to remember what you are working on.

.. code-block:: bash

   git checkout -b complete-graph-circular-layout-example

Now you can begin work on your example. Sticking with the circular layout idea,
you might create a file in ``examples/drawing`` called ``circular_layout.py``
with the following contents::

   import networkx as nx
   import matplotlib.pyplot as plt

   G = nx.complete_graph(10)  # A complete graph with 10 nodes
   nx.draw_networkx(G, pos=nx.circular_layout(G))

.. note:: It may not be clear where exactly an example belongs. Our circular
   layout example is very simple, so perhaps it belongs in ``examples/basic``.
   It would also make sense for it to be in ``examples/drawing`` since it deals
   with visualization. Don't worry if you're not sure: questions like this will
   be resolved during the review process.

At this point, your contribution is ready to be reviewed. You can make the
changes on your ``complete-graph-circular-layout-example`` branch visible to
other NetworkX developers by
`creating a pull request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request`__.

.. seealso:: The `developer guide <Development Workflow>` has more details on
   creating pull requests.

Q: I want to work on a specific function. How do I find it in the source code?
------------------------------------------------------------------------------

Assuming you have followed the instructions for
`setting up the development workflow <Development Workflow>`, there are several
ways of determining where the in the **source code** a particular function or
class is defined.

For example, let's say you are interested in making a change to the
`~networkx.kamada_kawai_layout` function, so you need to know where it is
defined. In an IPython terminal, you can use ``?``:

.. nbplot::

   >>> import networkx as nx
   >>> nx.kamada_kawai_layout?

The ``grep`` command-line utility is also very useful. For example, from the
NetworkX source directory:

.. code-block:: bash

   $ grep -r "def kamada_kawai_layout" .
   ./networkx/drawing/layout.py:def kamada_kawai_layout(
