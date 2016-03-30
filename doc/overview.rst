..  -*- coding: utf-8 -*-

Overview
========

NetworkX is a Python language software package for the creation, 
manipulation, and study of the structure, dynamics, and function of complex networks.  

With NetworkX you can load and store networks in standard and nonstandard data formats, generate many types of random and classic networks, analyze network structure,  build network models, design new network algorithms, draw networks, and much more.


Who uses NetworkX?
------------------

The potential audience for NetworkX includes mathematicians,
physicists, biologists, computer scientists, and social scientists. Good 
reviews of the state-of-the-art in the science of
complex networks are presented in Albert and Barabási [BA02]_, Newman
[Newman03]_, and Dorogovtsev and Mendes [DM03]_. See also the classic
texts [Bollobas01]_, [Diestel97]_ and [West01]_ for graph theoretic
results and terminology. For basic graph algorithms, we recommend the
texts of Sedgewick, e.g. [Sedgewick01]_ and [Sedgewick02]_ and the
survey of Brandes and Erlebach [BE05]_.
  
.. [BA02] R. Albert and A.-L. Barabási, "Statistical mechanics of complex
   networks", Reviews of Modern Physics, 74, pp. 47-97, 2002. 
   http://arxiv.org/abs/cond-mat/0106096

.. [Newman03] M.E.J. Newman, "The Structure and Function of Complex
   Networks", SIAM Review, 45, pp. 167-256, 2003. 
   http://epubs.siam.org/doi/abs/10.1137/S003614450342480

.. [DM03] S.N. Dorogovtsev and J.F.F. Mendes, "Evolution of Networks",
   Oxford University Press, 2003.

.. [Bollobas01] B. Bollobás, "Random Graphs", Second Edition,
   Cambridge University Press, 2001.

.. [Diestel97] R. Diestel, "Graph Theory", Springer-Verlag, 1997. 
   http://diestel-graph-theory.com/index.html

.. [West01] D. B. West, "Introduction to Graph Theory", Prentice Hall,
    2nd ed., 2001.

.. [Sedgewick01] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
   Addison Wesley Professional, 3rd ed., 2001.

.. [Sedgewick02] R. Sedgewick, "Algorithms in C: Parts 1-4: 
   Fundamentals, Data Structure, Sorting, Searching", Addison Wesley
   Professional, 3rd ed., 2002.

.. [BE05] U. Brandes and T. Erlebach, "Network Analysis:
   Methodological Foundations", Lecture Notes in Computer Science, 
   Volume 3418, Springer-Verlag, 2005.


Goals
-----
NetworkX is intended to provide

-  tools for the study of the structure and
   dynamics of social, biological, and infrastructure networks,

-  a standard programming interface and graph implementation that is suitable
   for many applications, 

-  a rapid development environment for collaborative, multidisciplinary
   projects,

-  an interface to existing numerical algorithms and code written in C, 
   C++, and FORTRAN, 

-  the ability to painlessly slurp in large nonstandard data sets. 


The Python programming language
-------------------------------

Python is a powerful programming language that allows simple and flexible representations of networks, and  clear and concise expressions of network algorithms (and other algorithms too).  Python has a vibrant and growing ecosystem of packages that NetworkX uses to provide more features such as numerical linear algebra and drawing.  In addition 
Python is also an excellent "glue" language for putting together pieces of software from other languages which allows reuse of legacy code and engineering of high-performance algorithms [Langtangen04]_. 

Equally important, Python is free, well-supported, and a joy to use. 

In order to make the most out of NetworkX you will want to know how to write basic programs in Python.  
Among the many guides to Python, we recommend the documentation at
http://www.python.org and the text by Alex Martelli [Martelli03]_.

.. [Langtangen04] H.P. Langtangen, "Python Scripting for Computational
   Science.", Springer Verlag Series in Computational Science and
   Engineering, 2004. 

.. [Martelli03]  A. Martelli, "Python in a Nutshell", O'Reilly Media
   Inc, 2003.


Free software
-------------

NetworkX is free software; you can redistribute it and/or
modify it under the terms of the :doc:`BSD license <license>`.
We welcome contributions from the community.  Information on
NetworkX development is found at the NetworkX Developer Zone at Github
https://github.com/networkx/networkx


History
-------

NetworkX was born in May 2002. The original version was designed and written by Aric Hagberg, Dan Schult, and Pieter Swart in 2002 and 2003.  
The first public release was in April 2005.

Many people have contributed to the success of NetworkX. Some of the contributors are listed in the :doc:`credits`.


What Next
---------

- :doc:`install`
- :doc:`tutorial`
- :doc:`reference/index`
- :doc:`examples/index`
