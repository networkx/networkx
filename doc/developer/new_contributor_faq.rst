.. _contributing_faq:

New Contributor FAQ
*******************

A collection of frequently-asked questions by newcomers to
open-source development and first-time contributors to NetworkX.

Q: I'm new to open source and would like to contribute to NetworkX. How do I get started?
-----------------------------------------------------------------------------------------

To contribute to NetworkX, you will need three things:

  1. The source code
  2. A development environment
  3. An idea of what you'd like to contribute

Steps 1 & 2 are covered extensively in :ref:`Development Workflow <dev_workflow>`.
There is no generic answer for step 3. There are many ways that NetworkX can
be improved, from adding new algorithms, improving existing algorithms,
improving the test suite (e.g. increasing test coverage), and improving the
documentation.
The "best" way to find a place to start is to follow your own personal
interests!
That said, a few places to check for ideas on where to get started:

 - `The issue tracker <https://github.com/networkx/networkx/issues>`_ lists
   known bugs and feature requests. Of particular interest for first-time
   contributors are issues that have been tagged with the `Good First Issue`_
   or `Sprint`_ labels.
 - The `Algorithms discussion`_ includes a listing of algorithms that users
   would like to have but that are not yet included in NetworkX.

.. _Good First Issue: https://github.com/networkx/networkx/issues?q=is%3Aopen+is%3Aissue+label%3A%22Good+First+Issue%22

.. _Sprint: https://github.com/networkx/networkx/issues?q=is%3Aopen+is%3Aissue+label%3ASprint

.. _Algorithms discussion: https://github.com/networkx/networkx/discussions/categories/algorithms

Q: How do I contribute an example to the Gallery?
-------------------------------------------------

The example gallery is great place to contribute, particularly if you have an
interesting application or visualization that uses NetworkX.
The gallery is generated using :doc:`sphinx-gallery <sphinx-gallery:index>`
from Python scripts stored in the ``examples/`` directory.

For instance, let's say I'd like to contribute an example of visualizing a
`complete graph <networkx.generators.classic.complete_graph>` using a
`circular layout <networkx.drawing.layout.circular_layout>`.
Assuming you have already followed the procedure for
:ref:`setting up a development environment <dev_workflow>`, start by
creating a new branch:

.. code-block:: bash

   git checkout -b complete-graph-circular-layout-example

.. note:: It's generally a good idea to give your branch a descriptive name so
   that it's easy to remember what you are working on.

Now you can begin work on your example. Sticking with the circular layout idea,
you might create a file in ``examples/drawing`` called ``plot_circular_layout.py``
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
`creating a pull request`__. 

.. _PR: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request

__ PR_

.. seealso:: The :ref:`developer guide <dev_workflow>` has more details on
   creating pull requests.

Q: I want to work on a specific function. How do I find it in the source code?
------------------------------------------------------------------------------

Assuming you have followed the instructions for
:ref:`setting up the development workflow <dev_workflow>`, there are several
ways of determining where the in the **source code** a particular function or
class is defined.

For example, let's say you are interested in making a change to the
`~networkx.drawing.layout.kamada_kawai_layout` function, so you need to know
where it is defined. In an IPython terminal, you can use ``?`` --- the source file is
listed in the ``File:`` field:

.. code-block:: ipython

   In [1]: import networkx as nx
   In [2]: nx.kamada_kawai_layout?

.. code-block:: text

   Signature: <clipped for brevity>
   Docstring: <clipped for brevity>
   File: ~/networkx/networkx/drawing/layout.py
   Type: function

Command line utilities like ``grep`` or ``git grep`` are also very useful.
For example, from the NetworkX source directory:

.. code-block:: bash

   $ grep -r "def kamada_kawai_layout" .
   ./networkx/drawing/layout.py:def kamada_kawai_layout(
