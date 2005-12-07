NetworkX 
========
.. include:: Menu.txt

*High productivity software for complex networks*
-------------------------------------------------
.. image:: art.png
   :align: right



About
-----

   NetworkX (NX) is a Python package for the creation, manipulation, and
   study of the structure, dynamics, and functions of complex networks.  
 
   Features:

      - Allows for 1M+ nodes, 10M+ edges
      - Includes standard graph-theoretic and statistical physics functions
      - Easy exchange of network algorithms between applications, 
      	disciplines, and platforms
      - Includes many classic graphs and synthetic networks
      - Nodes and edges can be "anything" 
      	(e.g. time-series, text, images, XML records)
      - Exploits existing code from high-quality legacy software in
      	 C, C++, Fortran, etc.
      - Open source (encourages community input)
      - Unit-tested

   Additional benefits due to Python:              
    

      - Allows fast prototyping of new algorithms
      - Easy to teach 
      - Multiplatform
      - Allows easy access to almost any database


   See the trac Wiki_ for code development information, bug tracking,
   and source code browsing.

Requirements
-------------

   To use NetworkX you need

      - Python version 2.3 or later http://www.python.org/

   Optional packages to enable drawing networks:      

      - Matplotlib       http://matplotlib.sourceforge.net/
      - Pygraphviz	 http://networkx.lanl.gov/pygraphviz/
      - Graphviz         http://graphviz.org/
      - Pydot            http://www.dkbza.org/pydot.html

   Optional useful packages:

      - Numerical Python http://numeric.scipy.org/
      - PyGSL            http://pygsl.sourceforge.net/
      - Ipython          http://ipython.scipy.org/

Downloading
-----------

   You can download NetworkX from 
   http://sourceforge.net/project/showfiles.php?group_id=122233

   You can browse the source at https://networkx.lanl.gov/wiki/browser/networkx/trunk

   To access the source repository using subversion, you will need a subversion client (e.g. svn for Linux). Then check out the code using

    svn co https://networkx.lanl.gov/svn/networkx/trunk networkx



Quick Install
-------------

   (See the Tutorial_ for more information)

   **Linux and OSX** (install from source)

      Download the source tar file or zip file, unpack, and run 
      "python setup.py install". 

   **Windows** (binary installer)
 
      Download the installer, run and follow the instructions.
      Please note that we are not Windows users and have only verified
      that the Windows installer passes the "smoke test".  If you
      have problems we suggest installing from the source distribution.


   NetworkX also may be installed using EasyInstall http://peak.telecommunity.com/DevCenter/EasyInstall

   easy_install networkx


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



