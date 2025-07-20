We use Sphinx for generating the API and reference documentation.

Pre-built versions can be found at

    https://networkx.org/

for both the stable and the latest (i.e., development) releases.

Instructions
~~~~~~~~~~~~

Install NetworkX along with its extra dependencies. For example, from
the root of the repository:

```
pip install .[extra]
```

Then, install the Python packages needed to build the documentation with::

    pip install --group doc

Building the example gallery additionally requires::

    pip install --group example

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
