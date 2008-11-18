..  -*- coding: utf-8 -*-

Introduction
============
NetworkX is a Python-based package for the creation, manipulation, and
study of the structure, dynamics, and function of complex networks. The
name means **Network "X"** and we pronounce it **NX**. We often 
will shorten NetworkX to "nx" in code examples by using the
Python import 

>>> import networkx as nx

The structure of a graph or network is encoded in the **edges**
(connections, links, ties, arcs, bonds) between **nodes** (vertices,
sites, actors). If unqualified, by graph we mean an undirected
graph, i.e. no multiple edges are allowed. By a network we usually 
mean a graph with weights (fields, properties) on nodes and/or edges.

The potential audience for NetworkX include: mathematicians,
physicists, biologists, computer scientists, social scientists. The
current state of the art of the (young and rapidly growing) science of
complex networks is presented in Albert and Barabási [BA02]_, Newman
[Newman03]_, and Dorogovtsev and Mendes [DM03]_. See also the classic
texts [Bollobas01]_, [Diestel97]_ and [West01]_ for graph theoretic
results and terminology. For basic graph algorithms, we recommend the
texts of Sedgewick, e.g. [Sedgewick01]_ and [Sedgewick02]_ and the
modern survey of Brandes and Erlebach [BE05]_.
  
Why Python? Past experience showed this approach to maximize
productivity, power, multi-disciplinary scope (our application test
beds included large communication, social, data and biological
networks), and platform independence. This philosophy does not exclude
using whatever other language is appropriate for a specific subtask,
since Python is also an excellent "glue" language [Langtangen04]_. 
Equally important, Python is free, well-supported and a joy to use. 
Among the many guides to Python, we recommend the documentation at
http://www.python.org and the text by Alex Martelli [Martelli03]_.

NetworkX is free software; you can redistribute it and/or
modify it under the terms of the **LGPL** (GNU Lesser General Public
License) as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
Please see the license for more information. 
