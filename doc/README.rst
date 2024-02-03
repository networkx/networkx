We use Sphinx for generating the API and reference documentation.

Pre-built versions can be found at

    https://networkx.org/

for both the stable and the latest (i.e., development) releases.

Instructions
~~~~~~~~~~~~

After installing NetworkX and its dependencies, install the Python
packages needed to build the documentation by entering the root
directory and executing::

    pip install -r requirements/doc.txt

Building the example gallery additionally requires the dependencies
listed in ``requirements/extra.txt`` and ``requirements/example.txt``::

    pip install -r requirements/extra.txt
    pip install -r requirements/example.txt

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
