# Building docs

We use Sphinx for generating the API and reference documentation.

Pre-built versions can be found at

    https://networkx.org/

for both the stable and the latest (i.e., development) releases.

## Instructions

After installing NetworkX and its dependencies, install the Python
packages needed to build the documentation by entering::

    pip install -r requirements/doc.txt

in the root directory.

To build the HTML documentation, enter::

    make html

in the ``doc/`` directory.  This will generate a ``build/html`` subdirectory
containing the built documentation.

To build the PDF documentation, enter::

    make latexpdf

You will need to have LaTeX installed for this.
