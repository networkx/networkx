NetworkX
========
.. include:: Menu.txt


About
-----

   NetworkX (NX) is a Python package for the creation, manipulation, and
   study of the structure, dynamics, and functions of complex
   networks.  


Requirements
-------------

   To use NetworkX you need

      - Python version 2.3 or later http://www.python.org/

   Optional useful packages:

      - Numerical Python http://numeric.scipy.org/
      - PyGSL            http://pygsl.sourceforge.net/
      - Ipython          http://ipython.scipy.org/
      - Matplotlib       http://matplotlib.sourceforge.net/
      - Pydot            http://www.dkbza.org/pydot.html
      - Graphviz         http://graphviz.org/


Downloading
-----------

   You can download NetworkX from http://sourceforge.net/projects/networkx/


Quick Install
-------------

   (See the Tutorial_ for more information)

   **Linux and OSX** (install from source)

      Download the source tarball, unpack, and run "python setup.py install". 

   **Windows** (binary installer)
 
      Download the installer, run and follow the instructions.
      Please note that we are not Windows users and have only verified
      that the Windows installer passes the "smoke test".  If you
      have problems we suggest installing from the source distribution.


Using 
-----

   Just write in Python

   >>> import networkx as NX
   >>> G=NX.Graph()
   >>> G.add_edge(1,2)
   >>> G.add_node("spam")
   >>> print G.nodes()
   [1, 2, 'spam']
   >>> print G.edges()
   [(1, 2)]

   See the Tutorial_, Reference_, QuickRef_, and Examples_.

.. raw:: html

   <div align="left" class="image image align-left image-reference"><a
    class="reference" href="http://sourceforge.net/"><img align="left"
    alt="SourceForge.net Logo" class="image" height="31"
    src="http://sourceforge.net/sflogo.php?group_id=122233&amp;type=1"
    width="88" /></a></div>



