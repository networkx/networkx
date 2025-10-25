Install
=======

NetworkX requires Python 3.11, 3.12, 3.13, or 3.14.  If you do not already
have a Python environment configured on your computer, please see the
instructions for installing the full `scientific Python stack
<https://scipy.org/install.html>`_.

Below we assume you have the default Python environment already configured on
your computer and you intend to install ``networkx`` inside of it.  If you want
to create and work with Python virtual environments, please follow instructions
on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

First, make sure you have the latest version of ``pip`` (the Python package manager)
installed. If you do not, refer to the `Pip documentation
<https://pip.pypa.io/en/stable/installing/>`_ and install ``pip`` first.

Install the released version
----------------------------

Install the current release of ``networkx`` with ``pip``::

    $ pip install networkx[default]

To upgrade to a newer release use the ``--upgrade`` flag::

    $ pip install --upgrade networkx[default]

If you do not have permission to install software systemwide, you can
install into your user directory using the ``--user`` flag::

    $ pip install --user networkx[default]

If you do not want to install our dependencies (e.g., ``numpy``, ``scipy``, etc.),
you can use::

    $ pip install networkx

This may be helpful if you are using PyPy or you are working on a project that
only needs a limited subset of our functionality and you want to limit the
number of dependencies.

Alternatively, you can manually download ``networkx`` from
`GitHub <https://github.com/networkx/networkx/releases>`_  or
`PyPI <https://pypi.python.org/pypi/networkx>`_.
To install one of these versions, unpack it and run the following from the
top-level source directory using the Terminal::

    $ pip install .[default]

Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``networkx``.

Before installing the development version, you may need to uninstall the
standard version of ``networkx`` using ``pip``::

    $ pip uninstall networkx

Then do::

    $ git clone https://github.com/networkx/networkx.git
    $ cd networkx
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

.. note::
   Some optional packages may require compiling
   C or C++ code.  If you have difficulty installing these packages
   with `pip`, please consult the homepages of those packages.

The following extra packages provide additional functionality. See the
files in the ``requirements/`` directory for information about specific
version requirements.

- `PyGraphviz <http://pygraphviz.github.io/>`_ and
  `pydot <https://github.com/erocarrera/pydot>`_ provide graph drawing
  and graph layout algorithms via `GraphViz <http://graphviz.org/>`_.
- `lxml <http://lxml.de/>`_ used for GraphML XML format.

To install ``networkx`` and extra packages, do::

    $ pip install networkx[default,extra]

To explicitly install all optional packages, do::

    $ pip install pygraphviz pydot lxml

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
