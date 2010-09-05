**********
Installing
**********

Quick install
=============

Get NetworkX from the Python Package Index at
http://pypi.python.org/pypi/networkx

or install it with::

   easy_install networkx

and an attempt will be made to find and install an appropriate version
that matches your operating system and Python version. 

More download options are at http://networkx.lanl.gov/download.html

Installing from source
======================

You can install from source by downloading a source archive file
(tar.gz or zip) or by checking out the source files from the
Subversion repository.

NetworkX is a pure Python package; you don't need a compiler to build
or install it.

Source archive file
-------------------

  1. Download the source (tar.gz or zip file).

  2. Unpack and change directory to networkx-"version" 

  3. Run "python setup.py install" to build and install 

  4. (optional) Run "python setup_egg.py nosetests" to execute the tests


SVN repository
--------------

  1. Check out the networkx trunk::

       svn co https://networkx.lanl.gov/svn/networkx/trunk networkx

  2. Change directory to "networkx"   

  3.  Run "python setup.py install" to build and install 

  4. (optional) Run "python setup_egg.py nosetests" to execute the tests


If you don't have permission to install software on your
system, you can install into another directory using
the --prefix or --home flags to setup.py.

For example

::  

    python setup.py install --prefix=/home/username/python
    or
    python setup.py install --home=~

If you didn't install in the standard Python site-packages directory
you will need to set your PYTHONPATH variable to the alternate location.
See http://docs.python.org/inst/search-path.html for further details.


Installing pre-built packages
======================================

Linux
-----
Debian packages are available at http://packages.debian.org/python-networkx


Requirements
============

Python
------

To use NetworkX you need Python version 2.6 or later.  
Most of NetworkX works with Python version 3.1.2 or later.
http://www.python.org/


The easiest way to get Python and most optional packages is to install
the Enthought Python distribution
http://www.enthought.com/products/epd.php

Other options are

Windows
~~~~~~~
 - Official Python site version:  http://www.python.org/download/

 - ActiveState version: http://www.activestate.com/activepython/

OSX
~~~

OSX 10.5 ships with Python version 2.5.  You need Python 2.6 or 
later to use NetworkX.  If you have an older version and need
to install a newer release pre-built Python packages are available from 

 - Official Python site version  http://www.python.org/download/

 - Pythonmac  http://www.pythonmac.org/packages/ 

 - ActiveState http://activestate.com/Products/ActivePython/


If you are using Fink or MacPorts, Python is available through both
of those package systems.

Linux
~~~~~
Python is included in all major Linux distributions


Optional packages 
=================

The following are optional packages that NetworkX can use to
provide additional functions.


NumPy
-----
  - Download: http://scipy.org/Download

SciPy
-----

Provides sparse matrix representation of graphs and many
numerical scientific tools.


Matplotlib
----------
Provides flexible drawing of graphs

  - Download: http://matplotlib.sourceforge.net/


GraphViz
--------

In conjunction with either
      
      - PyGraphviz:  http://networkx.lanl.gov/pygraphviz/

      or

      - pydot: http://dkbza.org/pydot.html

provides graph drawing and graph layout algorithms.

  - Download: http://graphviz.org/

Pyparsing
---------

http://pyparsing.wikispaces.com/

Required for pydot, GML file reading.

PyYAML
------

http://pyyaml.org/

Required for YAML format reading and writing.


Other packages 
---------------

These are extra packages you may consider using with NetworkX

      - IPython, interactive Python shell, http://ipython.scipy.org/
      - PyYAML, structured output format, http://pyyaml.org/
