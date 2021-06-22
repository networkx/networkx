.. _contents:

Software for Complex Networks
=============================

.. only:: html

    :Release: |version|
    :Date: |today|

NetworkX is a Python package for the creation, manipulation, and study
of the structure, dynamics, and functions of complex networks.
It provides:

-  tools for the study of the structure and
   dynamics of social, biological, and infrastructure networks;
-  a standard programming interface and graph implementation that is suitable
   for many applications;
-  a rapid development environment for collaborative, multidisciplinary
   projects;
-  an interface to existing numerical algorithms and code written in C,
   C++, and FORTRAN; and
-  the ability to painlessly work with large nonstandard data sets.

With NetworkX you can load and store networks in standard and nonstandard data
formats, generate many types of random and classic networks, analyze network
structure, build network models, design new network algorithms, draw networks,
and much more.

Citing
------

To cite NetworkX please use the following publication:

Aric A. Hagberg, Daniel A. Schult and Pieter J. Swart,
`"Exploring network structure, dynamics, and function using NetworkX"
<http://conference.scipy.org/proceedings/SciPy2008/paper_2/>`_,
in
`Proceedings of the 7th Python in Science Conference (SciPy2008)
<http://conference.scipy.org/proceedings/SciPy2008/index.html>`_, Gäel
Varoquaux, Travis Vaught, and Jarrod Millman (Eds), (Pasadena, CA
USA), pp. 11--15, Aug 2008

.. only:: html

   `PDF <http://conference.scipy.org/proceedings/SciPy2008/paper_2/full_text.pdf>`_
   `BibTeX <http://conference.scipy.org/proceedings/SciPy2008/paper_2/reference.bib>`_

Audience
--------

The audience for NetworkX includes mathematicians, physicists, biologists,
computer scientists, and social scientists. Good reviews of the science of
complex networks are presented in Albert and Barabási [BA02]_, Newman
[Newman03]_, and Dorogovtsev and Mendes [DM03]_. See also the classic texts
[Bollobas01]_, [Diestel97]_ and [West01]_ for graph theoretic results and
terminology. For basic graph algorithms, we recommend the texts of Sedgewick
(e.g., [Sedgewick01]_ and [Sedgewick02]_) and the survey of Brandes and
Erlebach [BE05]_.

Python
------

Python is a powerful programming language that allows simple and flexible
representations of networks as well as clear and concise expressions of network
algorithms.  Python has a vibrant and growing ecosystem of packages that
NetworkX uses to provide more features such as numerical linear algebra and
drawing.  In order to make the most out of NetworkX you will want to know how
to write basic programs in Python.  Among the many guides to Python, we
recommend the `Python documentation <https://docs.python.org/3/>`_ and the text
by Alex Martelli [Martelli03]_.

License
-------

.. include:: ../LICENSE.txt

Bibliography
------------

.. [BA02] R. Albert and A.-L. Barabási, "Statistical mechanics of complex
   networks", Reviews of Modern Physics, 74, pp. 47-97, 2002.
   https://arxiv.org/abs/cond-mat/0106096

.. [Bollobas01] B. Bollobás, "Random Graphs", Second Edition,
   Cambridge University Press, 2001.

.. [BE05] U. Brandes and T. Erlebach, "Network Analysis:
   Methodological Foundations", Lecture Notes in Computer Science,
   Volume 3418, Springer-Verlag, 2005.

.. [Diestel97] R. Diestel, "Graph Theory", Springer-Verlag, 1997.
   http://diestel-graph-theory.com/index.html

.. [DM03] S.N. Dorogovtsev and J.F.F. Mendes, "Evolution of Networks",
   Oxford University Press, 2003.

.. [Martelli03]  A. Martelli, "Python in a Nutshell", O'Reilly Media
   Inc, 2003.

.. [Newman03] M.E.J. Newman, "The Structure and Function of Complex
   Networks", SIAM Review, 45, pp. 167-256, 2003.
   http://epubs.siam.org/doi/abs/10.1137/S003614450342480

.. [Sedgewick02] R. Sedgewick, "Algorithms in C: Parts 1-4:
   Fundamentals, Data Structure, Sorting, Searching", Addison Wesley
   Professional, 3rd ed., 2002.

.. [Sedgewick01] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
   Addison Wesley Professional, 3rd ed., 2001.

.. [West01] D. B. West, "Introduction to Graph Theory", Prentice Hall,
    2nd ed., 2001.

.. toctree::
   :maxdepth: 1
   :hidden:

   install
   tutorial
   reference/index
   release/index
   developer/index
   auto_examples/index
