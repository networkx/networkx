NetworkX 
========

*High productivity software for complex networks*
-------------------------------------------------
.. raw:: html

   <div align="left" class="image image align-right image-reference">
    <img align="right" alt="NetworkX art" class="image" height="540"
    src="https://networkx.lanl.gov/images/art.png"  width="270" />
    </div>


About
-----

   NetworkX (NX) is a Python package for the creation, manipulation, and
   study of the structure, dynamics, and functions of complex networks.  
 
   Features:

      - Includes standard graph-theoretic and statistical physics functions
      - Easy exchange of network algorithms between applications, 
      	disciplines, and platforms
      - Includes many classic graphs and synthetic networks
      - Nodes and edges can be "anything" 
      	(e.g. time-series, text, images, XML records)
      - Exploits existing code from high-quality legacy software in C, 
        C++, Fortran, etc.
      - Open source (encourages community input)
      - Unit-tested

   Additional benefits due to Python:              
    
      - Allows fast prototyping of new algorithms
      - Easy to teach 
      - Multi-platform
      - Allows easy access to almost any database


Quick Example
-------------

   Just write in Python

   >>> import networkx as NX
   >>> G=NX.Graph()
   >>> G.add_edge(1,2)
   >>> G.add_node("spam")
   >>> print G.nodes()
   [1, 2, 'spam']
   >>> print G.edges()
   [(1, 2)]


Download
--------

   - Releases

     - Python Cheese Shop:  http://cheeseshop.python.org/pypi/networkx/
     - NetworkX site: https://networkx.lanl.gov/download/?C=M;O=D

   - Subversion repository: https://networkx.lanl.gov/svn/networkx/trunk


Authors
-------
   
  - Aric Hagberg  http://math.lanl.gov/~hagberg/
  - Dan Schult
  - Pieter Swart



