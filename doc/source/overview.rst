..  -*- coding: utf-8 -*-

Introduction
============

NetworkX is a Python-based package for the creation, manipulation, and
study of the structure, dynamics, and function of complex networks.

The structure of a graph or network is encoded in the **edges**
(connections, links, ties, arcs, bonds) between **nodes** (vertices,
sites, actors). If unqualified, by graph we mean an undirected
graph, i.e. no multiple edges are allowed. By a network we usually 
mean a graph with weights (fields, properties) on nodes and/or edges.

Who uses NetworkX?
------------------

The potential audience for NetworkX includes mathematicians,
physicists, biologists, computer scientists, and social scientists. The
current state of the art of the science of
complex networks is presented in Albert and Barabási [BA02]_, Newman
[Newman03]_, and Dorogovtsev and Mendes [DM03]_. See also the classic
texts [Bollobas01]_, [Diestel97]_ and [West01]_ for graph theoretic
results and terminology. For basic graph algorithms, we recommend the
texts of Sedgewick, e.g. [Sedgewick01]_ and [Sedgewick02]_ and the
survey of Brandes and Erlebach [BE05]_.
  
The Python programming language
-------------------------------

Why Python? Past experience showed this approach to maximize
productivity, power, multi-disciplinary scope (applications include large communication, social, data and biological
networks), and platform independence. This philosophy does not exclude
using whatever other language is appropriate for a specific subtask,
since Python is also an excellent "glue" language [Langtangen04]_. 
Equally important, Python is free, well-supported and a joy to use. 
Among the many guides to Python, we recommend the documentation at
http://www.python.org and the text by Alex Martelli [Martelli03]_.

Free software
-------------

NetworkX is free software; you can redistribute it and/or
modify it under the terms of the :doc:`NetworkX License </reference/legal>`.
We welcome contributions from the community.  Information on
NetworkX development is found at the NetworkX Developer Zone
https://networkx.lanl.gov/trac.

Goals
-----
NetworkX is intended to:

-  Be a tool to study the structure and
   dynamics of social, biological, and infrastructure networks

-  Provide ease-of-use and rapid
   development in a collaborative, multidisciplinary environment 

-  Be an Open-source software package that can provide functionality
   to a diverse community of active and easily participating users
   and developers. 

-  Provide an easy interface to 
   existing code bases written in C, C++, and FORTRAN 

-  Painlessly slurp in large nonstandard data sets 

-  Provide a standard API and/or graph implementation that is 
   suitable for many applications. 

History
-------

-  NetworkX was inspired by Guido van Rossum's 1998 Python 
   graph representation essay [vanRossum98]_.

-  First public release in April 2005.  Version 1.0 released in 2009.


What Next
^^^^^^^^^

 - :doc:`A Brief Tour </tutorial/tutorial>`

 - :doc:`Installing </install>`

 - :doc:`Reference </reference/index>`

 - :doc:`Examples </examples/index>`
