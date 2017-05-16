**********
Installing
**********

Installing with pip
===================
Try to install it with

::

   pip install networkx

and an attempt will be made to find and install an appropriate version
that matches your operating system and Python version.

You can also get NetworkX from the Python Package Index manually
at http://pypi.python.org/pypi/networkx
To use pip, you need to have `setuptools <https://pypi.python.org/pypi/setuptools>`_ installed.

You can install the development version (at github.com) with

::

  pip install git://github.com/networkx/networkx.git#egg=networkx

More download file options are at http://networkx.github.io/download.html.


Installing with conda
=====================

If you are using Ananconda/Miniconda distribution of Python then you can
update/install NetworkX to the latest version with

::

    conda install networkx

or to update an existing installation

::

    conda update networkx


Installing from source
======================

You can install from source by downloading a source archive file
(tar.gz or zip) or by checking out the source files from the
Git source code repository.

NetworkX is a pure Python package; you don't need a compiler to build
or install it.

Source archive file
-------------------

  1. Download the source (tar.gz or zip file) from
     https://pypi.python.org/pypi/networkx/
     or get the latest development version from
     https://github.com/networkx/networkx/

  2. Unpack and change directory to the source directory
     (it should have the files README.txt and setup.py).

  3. Run :samp:`python setup.py install` to build and install

  4. (Optional) Run :samp:`nosetests` to execute the tests if you have
     `nose <https://pypi.python.org/pypi/nose>`_ installed.


GitHub
------

  1. Clone the networkx repository
     (see https://github.com/networkx/networkx/ for options)
     ::

       git clone https://github.com/networkx/networkx.git


  2. Change directory to :samp:`networkx`

  3. Run :samp:`python setup.py install` to build and install

  4. (Optional) Run :samp:`nosetests` to execute the tests if you have
     `nose <https://pypi.python.org/pypi/nose>`_ installed.


If you don't have permission to install software on your
system, you can install into another directory using
the :samp:`--user`, :samp:`--prefix`, or :samp:`--home` flags to setup.py.

For example

::

    python setup.py install --prefix=/home/username/python

or

::

    python setup.py install --home=~

or

::

    python setup.py install --user

If you didn't install in the standard Python site-packages directory
you will need to set your PYTHONPATH variable to the alternate location.
See http://docs.python.org/2/install/index.html#search-path for further details.


Requirements
============

Python
------

To use NetworkX you need Python 2.7, 3.3 or later.

The easiest way to get Python and most optional packages is to install
the Enthought Python distribution "`Canopy <https://www.enthought.com/products/canopy/>`_".

There are several other distributions that contain the key packages you need for scientific computing.  See http://scipy.org/install.html for a list.


Optional packages
=================

The following are optional packages that NetworkX can use to
provide additional functions.


NumPy
-----
Provides matrix representation of graphs and is used in some graph algorithms for high-performance matrix computations.

  - Download: http://scipy.org/Download

SciPy
-----

Provides sparse matrix representation of graphs and many numerical scientific tools.

  - Download: http://scipy.org/Download


Matplotlib
----------
Provides flexible drawing of graphs.

  - Download: http://matplotlib.sourceforge.net/


GraphViz
--------

In conjunction with either

      - PyGraphviz:  http://pygraphviz.github.io/

      or

      - pydot: https://github.com/erocarrera/pydot

provides graph drawing and graph layout algorithms.

  - Download: http://graphviz.org/

PyYAML
------

http://pyyaml.org/

Required for YAML format reading and writing.


Other packages
---------------

These are extra packages you may consider using with NetworkX

      - IPython, interactive Python shell, http://ipython.scipy.org/
