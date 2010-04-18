*******
Testing
*******

Requirements for testing
========================
NetworkX uses the Python nose testing package.
If you don't already have that package installed, follow
the directions here
http://somethingaboutorange.com/mrl/projects/nose

Testing a source distribution
=============================

You can test the complete package from the unpacked source directory with::

   python setup_egg.py nosetests


Testing an installed package
============================

If you have a file-based (not a Python egg) installation you can
test the installed package with 

>>> import networkx
>>> networkx.test()

or::

   python -c "import networkx; networkx.test()"

Testing for developers
======================

You can test any or all of NetworkX by using the "nosetests"
test runner.  

First make sure the NetworkX version you want to test
is in your PYTHONPATH (either installed or pointing to your
unpacked source directory).  

Then you can run individual test files with::

   nosetests path/to/file

or all tests found in dir and an directories contained in dir::

   nosetests path/to/dir

By default nosetests doesn't test docutils style tests in
Python modules but you can turn that on with::

   nosetests --with-doctest

For doctests in stand-alone files NetworkX uses the extension txt so
you can add::

   nosetests --with-doctest --doctest-extension=txt

to also execute those tests.

These options are on by default if you run nosetests from 
the root of the NetworkX distribution since they are specified
in the setup.cfg file found there.
