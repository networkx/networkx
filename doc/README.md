# Building docs

We currently use Sphinx for generating the API and reference
documentation for NetworkX.

If you only want to get the documentation, note that pre-built
versions can be found at

    http://networkx.github.io/

for both the stable and the latest (i.e., development) releases.

## Instructions

In addition to installing NetworkX and its dependencies, install the Python
packages need to build the documentation by entering::

   pip install -r requirements.txt

in the ``doc/`` directory.

To build the HTML documentation, enter::

    make html

in the ``doc/`` directory. If all goes well, this will generate a
``build/html`` subdirectory containing the built documentation.

To build the PDF documentation, enter::

    make latexpdf

You will need to have Latex installed for this.
