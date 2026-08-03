Install
=======

NetworkX requires Python 3.12, 3.13, or 3.14.
NetworkX is a pure Python package with no hard dependencies; however, certain
features (e.g. graph drawing, spectral analysis, link analysis, etc.) depend
on the scientific Python stack.
These soft dependencies are captured in the ``default`` optional dependency group
and can be installed with, e.g. ``pip install networkx[default]``.
For more detailed information, check out SciPy's instructions for installing
the full `scientific Python stack <https://scipy.org/install.html>`_.

Below we assume you have a Python environment already configured on
your computer and you intend to install ``networkx`` inside of it.
For further details on environment setup and management tools, from the
built-in Python ``venv`` module to toolchains like ``uv``, ``conda/mamba`` and
``pixi``, check out the `Scientific Python Development Guide
<https://learn.scientific-python.org/development/tutorials/dev-environment/#development-environment>`_.

First, make sure you have the latest version of ``pip`` (the Python package manager)
installed. If you do not, refer to the `Pip documentation
<https://pip.pypa.io/en/stable/installation/>`_ and install ``pip`` first.

Install the released version
----------------------------

Install the current release of ``networkx`` with ``pip``::

    $ pip install networkx

This installs NetworkX without any dependencies.
In order to make use of additional functionality in NetworkX, it is
recommended to install the default scientific Python dependencies
(e.g. ``numpy``, ``scipy``, ``matplotlib``)::

    $ pip install networkx[default]

To upgrade to a newer release use the ``--upgrade`` flag::

    $ pip install --upgrade networkx[default]

Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``networkx``.

First, ``git clone`` the source code::

    $ git clone https://github.com/networkx/networkx.git
    $ cd networkx

Then, in a new development environment::

    $ pip install -e .[default]

The ``pip install -e .[default]`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``networkx`` at any time, in the same directory do::

    $ git pull

Backends
--------

NetworkX has the ability to dispatch function calls to optional,
separately-installed, third-party backends. NetworkX backends let users
experience improved performance and/or additional functionality without
changing their NetworkX Python code.

While NetworkX is a pure-Python implementation with minimal to no dependencies,
backends may be written in other languages and require specialized hardware
and/or OS support, additional software dependencies, or even separate services.

Installation instructions vary based on the backend, and additional information
can be found from the individual backend project pages listed in the
:doc:`/backends` section.


Extra packages
--------------

The following extra packages provide additional functionality. See the
files in the ``requirements/`` directory for information about specific
version requirements.

- `PyGraphviz <https://pygraphviz.github.io/>`_ provides graph drawing
  and graph layout algorithms via `GraphViz <https://graphviz.org/>`_.
- `lxml <https://lxml.de/>`_ for improved performance in parsing GraphML XML format.

To install ``networkx`` and extra packages, do::

    $ pip install networkx[default,extra]

To explicitly install all optional packages, do::

    $ pip install pygraphviz lxml

Or, install any optional package (e.g., ``pygraphviz``) individually::

    $ pip install pygraphviz

Testing
-------

NetworkX uses the Python ``pytest`` testing package.  You can learn more
about pytest on their `homepage <https://pytest.org>`_.

Test a source distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can test the complete package from the unpacked source directory with::

    pytest networkx

Test an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^

From a shell command prompt you can test the installed package with::

   pytest --pyargs networkx
