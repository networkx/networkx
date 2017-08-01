.. _setup:

.. highlight:: bash

===============================================
 Guide to setting up a development environment
===============================================

This guide explains how to set up a clean development environment using
`Anaconda <https://anaconda.org/>`__ virtual environments and ``virtualenv``
environments.

Anaconda
========

First, ensure that Anaconda is installed, then fork and clone NetworkX and check
out a development branch. Now create a new Conda environment, in this case
called ``networkx_dev``::

   conda create -n networkx_dev python=3

If you use Jupyter notebooks to run code during development, instead run::

   conda create -n networkx_dev python=3 jupyter nb_conda

Once the environment is created, activate it::

   source activate networkx_dev

Install an editable version of NetworkX and its required packages::

   pip install -e .
   pip install -r requirements.txt

N.B. ``gdal`` may need to be installed before installing the required packages
e.g.::

================ ============================================================
Debian / Ubuntu  ``sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable``
                 ``sudo apt-get update``
                 ``sudo apt-get install gdal``
Fedora           ``sudo dnf install gdal``
Windows          Download and install a `windows binary
                 <http://www.gisinternals.com/release.php>`__
OS X             ``brew install gdal``
================ ============================================================

If you use Jupyter notebooks to run code during development, it is very handy to
have the following in the first cell (N.B. these Juypter notebooks should not be
committed to the NetworkX repository)::

   %load_ext autoreload
   %autoreload 2
   import networkx

Once the changes have been tested, committed and pushed, the Conda environment
can be removed by::

   source deactivate networkx_dev
   conda env remove -n networkx_dev
