.. _mission_and_values:

==================
Mission and Values
==================

Our mission
-----------

NetworkX aims to be the reference library for network science algorithms in
Python. We accomplish this by:

- **being easy to use and install**. We are careful in taking on new
  dependencies, and sometimes cull existing ones, or make them optional. All
  functions in our API have thorough docstrings clarifying expected inputs and
  outputs.
- **providing a consistent API**. Conceptually identical arguments have the
  same name and position in a function signature.
- **ensuring correctness**. Test coverage is close to 100% and code is reviewed by
  at least two core developers before being included in the library.
- **caring for users’ data**. We have a functional API and don't modify
  input data unless explicitly directed to do so.
- **promoting education in network science**, with extensive pedagogical
  documentation.

Our values
----------

- We are inclusive (:ref:`code_of_conduct`). We welcome and mentor newcomers who are
  making their first contribution.
- We are open source and community-driven (:ref:`governance`).
- We focus on graph data structures and algorithms for network science applications.
- We prefer pure Python implementations using native data structures
  (especially dicts) due to their consistent, intuitive interface and amazing
  performance capabilities. We include interfaces to other data structures,
  especially NumPy arrays and SciPy sparse matrices for algorithms that more
  naturally use arrays and matrices or where time or space requirements are
  significantly lower. Sometimes we provide two algorithms for the same result,
  one using each data structure, when pedagogy or space/time trade-offs justify
  such multiplicity.
- We value simple, readable implementations over getting every last ounce of
  performance. Readable code that is easy to understand, for newcomers and
  maintainers alike, makes it easier to contribute new code as well as prevent
  bugs. This means that we will prefer a 20% slowdown if it reduces lines of
  code two-fold, for example.
- We value education and documentation. All functions should have `NumPy-style
  docstrings <https://numpy.org/doc/stable/docs/howto_document.html>`,
  preferably with examples, as well as gallery examples that showcase how that
  function is used in a scientific application.

Acknowledgments
---------------

This document is modified from the `scikit-image` mission and values document.
