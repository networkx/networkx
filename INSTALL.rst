Install
=======

NetworkX requires Python 2.7, 3.4, 3.5, or 3.6.  If you do not already
have a Python environment configured on your computer, please see the
instructions for installing the full `scientific Python stack
<https://scipy.org/install.html>`_.

.. note::
   If you are on Windows and want to install optional packages (e.g., `scipy`),
   then you will need to install a Python distribution such as
   `Anaconda <https://www.anaconda.com/download/>`_,
   `Enthought Canopy <https://www.enthought.com/product/canopy>`_,
   `Python(x,y) <http://python-xy.github.io/>`_,
   `WinPython <https://winpython.github.io/>`_, or
   `Pyzo <http://www.pyzo.org/>`_.
   If you use one of these Python distribution, please refer to their online
   documentation.

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

    $ pip install networkx

To upgrade to a newer release use the ``--upgrade`` flag::

    $ pip install --upgrade networkx

If you do not have permission to install software systemwide, you can
install into your user directory using the ``--user`` flag::

    $ pip install --user networkx

Alternatively, you can manually download ``networkx`` from
`GitHub <https://github.com/networkx/networkx/releases>`_  or
`PyPI <https://pypi.python.org/pypi/networkx>`_.
To install one of these versions, unpack it and run the following from the
top-level source directory using the Terminal::

    $ pip install .

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
    $ pip install -e .

The ``pip install -e .`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``networkx`` at any time, in the same directory do::

    $ git pull

Optional packages
-----------------

.. note::
   Some optional packages (e.g., `scipy`, `gdal`) may require compiling
   C or C++ code.  If you have difficulty installing these packages
   with `pip`, please review the instructions for installing
   the full `scientific Python stack <https://scipy.org/install.html>`_.

The following optional packages provide additional functionality.

- `NumPy <http://www.numpy.org/>`_ (>= 1.12.0) provides matrix representation of
  graphs and is used in some graph algorithms for high-performance matrix
  computations.
- `SciPy <http://scipy.org/>`_ (>= 0.19.0) provides sparse matrix representation
  of graphs and many numerical scientific tools.
- `pandas <http://pandas.pydata.org/>`_ (>= 0.20.0) provides a DataFrame, which
  is a tabular data structure with labeled axes.
- `Matplotlib <http://matplotlib.org/>`_ (>= 2.0.2) provides flexible drawing of
  graphs.
- `PyGraphviz <http://pygraphviz.github.io/>`_ and
  `pydot <https://github.com/erocarrera/pydot>`_ (>= 1.2.3) provide graph drawing
  and graph layout algorithms via `GraphViz <http://graphviz.org/>`_.
- `PyYAML <http://pyyaml.org/>`_ provides YAML format reading and writing.
- `gdal <http://www.gdal.org/>`_ provides shapefile format reading and writing.
- `lxml <http://lxml.de/>`_ used for GraphML XML format.

To install ``networkx`` and all optional packages, do::

    $ pip install networkx[all]

To explicitly install all optional packages, do::

    $ pip install numpy scipy pandas matplotlib pygraphviz pydot pyyaml gdal

Or, install any optional package (e.g., ``numpy``) individually::

    $ pip install numpy

Testing
-------

NetworkX uses the Python ``nose`` testing package.  If you don't already have
that package installed, follow the directions on the `nose homepage
<https://nose.readthedocs.org/>`_.

Test a source distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can test the complete package from the unpacked source directory with::

    nosetests networkx -v

Test an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a file-based (not a Python egg) installation you can test the
installed package with::

    >>> import networkx as nx
    >>> nx.test()

or::

    python -c "import networkx as nx; nx.test()"

Testing for developers
^^^^^^^^^^^^^^^^^^^^^^

You can test any or all of NetworkX by using the ``nosetests`` test runner.

First make sure the NetworkX version you want to test is in your ``PYTHONPATH``
(either installed or pointing to your unpacked source directory).

Then you can run individual test files with::

    nosetests path/to/file

or all tests found in dir and an directories contained in dir::

    nosetests path/to/dir

By default nosetests does not test docutils style tests in
Python modules but you can turn that on with::

    nosetests --with-doctest

For doctests in stand-alone files NetworkX uses the extension ``txt`` so
you can add::

    nosetests --with-doctest --doctest-extension=txt

to also execute those tests.

These options are on by default if you run nosetests from the root of the
NetworkX distribution since they are specified in the ``setup.cfg`` file found
there.
