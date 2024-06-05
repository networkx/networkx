We use Sphinx for generating the API and reference documentation.

Pre-built versions can be found at

    https://networkx.org/

for both the stable and the latest (i.e., development) releases.

Instructions
~~~~~~~~~~~~

To install NetworkX, its dependencies and the one necessary to build
the docs you can enter the root directory and execute::

    pip install .[doc]

Building the example gallery additionally requires the ``extra`` and ``example``::

    pip install .[extra,example]

To build the HTML documentation, enter ``doc/`` and execute::

    make html

This will generate a ``build/html`` subdirectory containing the built
documentation. If the dependencies in ``extra.txt`` and ``example.txt``
are **not** installed, build the HTML documentation without generating
figures by using::

    make html-noplot

To build the PDF documentation, enter::

    make latexpdf

You will need to have LaTeX installed for this.

.. note:: ``sphinx`` supports many other output formats. Type ``make`` without
   any arguments to see all the built-in options.
