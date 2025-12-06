.. _contributor_guide:

Contributor Guide
=================

.. note::
   This document assumes some familiarity with contributing to open source
   scientific Python projects using GitHub pull requests. If this does not
   describe you, you may first want to see the :ref:`contributing_faq`.
   If you are using a LLM or any other AI model, you will still need to
   follow the process described here.

.. _dev_workflow:

Development Workflow
--------------------

1. If you are a first-time contributor:

   * Go to `https://github.com/networkx/networkx
     <https://github.com/networkx/networkx>`_ and click the
     "fork" button to create your own copy of the project.

   * Clone the project to your local computer::

      git clone git@github.com:your-username/networkx.git

   * Navigate to the folder networkx and add the upstream repository::

      git remote add upstream git@github.com:networkx/networkx.git

   * Now, you have remote repositories named:

     - ``upstream``, which refers to the ``networkx`` repository
     - ``origin``, which refers to your personal fork

   * Next, you need to set up your build environment.
     Here are instructions for two popular environment managers:

     * ``venv`` (pip based)

       ::

         # Create a virtualenv named ``networkx-dev`` that lives in the directory of
         # the same name
         python -m venv networkx-dev
         # Activate it
         source networkx-dev/bin/activate
         # Install main development and runtime dependencies of networkx
         pip install -r requirements/default.txt -r requirements/test.txt -r requirements/developer.txt
         #
         # (Optional) Install pygraphviz and pydot packages
         # These packages require that you have your system properly configured
         # and what that involves differs on various systems.
         # pip install -r requirements/extra.txt
         #
         # Build and install networkx from source
         pip install -e .
         # Test your installation
         pytest --pyargs networkx

     * ``conda`` (Anaconda or Miniconda)

       ::

         # Create a conda environment named ``networkx-dev``
         conda create --name networkx-dev
         # Activate it
         conda activate networkx-dev
         # Install main development and runtime dependencies of networkx
         conda install -c conda-forge --file requirements/default.txt --file requirements/test.txt --file requirements/developer.txt
         #
         # (Optional) Install pygraphviz and pydot packages
         # These packages require that you have your system properly configured
         # and what that involves differs on various systems.
         # conda install -c conda-forge --file requirements/extra.txt
         #
         # Install networkx from source
         pip install -e .
         # Test your installation
         pytest --pyargs networkx

   * Finally, we recommend you install pre-commit which checks
     that your code matches formatting guidelines::

       pre-commit install

2. Develop your contribution:

   * Pull the latest changes from upstream::

      git checkout main
      git pull upstream main

   * Create a branch for the feature you want to work on. Since the
     branch name will appear in the merge message, use a sensible name
     such as 'bugfix-for-issue-1480'::

      git checkout -b bugfix-for-issue-1480 main

   * Commit locally as you progress (``git add`` and ``git commit``)

3. Test your contribution:

   * Run the test suite locally (see `Testing`_ for details)::

      PYTHONPATH=. pytest networkx

   * Running the tests locally *before* submitting a pull request helps catch
     problems early and reduces the load on the continuous integration
     system.

4. Ensure your contribution is properly formatted.

   * If you installed ``pre-commit`` as recommended in step 1, all necessary
     linting should run automatically at commit time. If there are any
     formatting issues, the commit will not be successful and linting
     suggestions will be applied to the patch automatically.
     Simply ``git add`` and ``git commit`` a second time to accept the proposed
     formatting changes.

   * If the above fails for whatever reason, you can also run the linter over
     the entire codebase with::

         pre-commit run --all-files

5. Submit your contribution:

   * Push your changes back to your fork on GitHub::

      git push origin bugfix-for-issue-1480

   * Go to GitHub. The new branch will show up with a green Pull Request
     button---click it.

   * If you want, post on the `mailing list
     <http://groups.google.com/group/networkx-discuss>`_ to explain your changes or
     to ask for review.

6. Review process:

   * Every Pull Request (PR) update triggers a set of `continuous integration
     <https://en.wikipedia.org/wiki/Continuous_integration>`_ services
     that check that the code is up to standards and passes all our tests.
     These checks must pass before your PR can be merged.  If one of the
     checks fails, you can find out why by clicking on the "failed" icon (red
     cross) and inspecting the build and test log.

   * Reviewers (the other developers and interested community members) will
     write inline and/or general comments on your PR to help
     you improve its implementation, documentation, and style.  Every single
     developer working on the project has their code reviewed, and we've come
     to see it as friendly conversation from which we all learn and the
     overall code quality benefits.  Therefore, please don't let the review
     discourage you from contributing: its only aim is to improve the quality
     of project, not to criticize (we are, after all, very grateful for the
     time you're donating!).

   * To update your PR, make your changes on your local repository
     and commit. As soon as those changes are pushed up (to the same branch as
     before) the PR will update automatically.

   .. note::

      If the PR closes an issue, make sure that GitHub knows to automatically
      close the issue when the PR is merged.  For example, if the PR closes
      issue number 1480, you could use the phrase "Fixes #1480" in the PR
      description or commit message.

7. Document deprecations and API changes

   If your change introduces any API modifications including deprecations,
   please make sure the PR has the ``type: API`` label.

   See the
   `deprecation policy <https://networkx.org/documentation/latest/developer/deprecations#procedure>`__
   for a step-by-step guide to the deprecation procedure.


Divergence from ``upstream main``
---------------------------------

If GitHub indicates that the branch of your Pull Request can no longer
be merged automatically, merge the main branch into yours::

   git fetch upstream main
   git merge upstream/main

If any conflicts occur, they need to be fixed before continuing.  See
which files are in conflict using::

   git status

Which displays a message like::

   Unmerged paths:
     (use "git add <file>..." to mark resolution)

     both modified:   file_with_conflict.txt

Inside the conflicted file, you'll find sections like these::

   <<<<<<< HEAD
   The way the text looks in your branch
   =======
   The way the text looks in the main branch
   >>>>>>> main

Choose one version of the text that should be kept, and delete the
rest::

   The way the text looks in your branch

Now, add the fixed file::


   git add file_with_conflict.txt

Once you've fixed all merge conflicts, do::

   git commit

.. note::

   Advanced Git users may want to rebase instead of merge,
   but we squash and merge PRs either way.


Guidelines
----------

* All code should have tests.
* All code should be documented, to the same
  `standard <https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard>`_
  as NumPy and SciPy.
* All changes are reviewed.  Ask on the
  `mailing list <http://groups.google.com/group/networkx-discuss>`_ if
  you get no response to your pull request.
* Default dependencies are listed in ``requirements/default.txt`` and extra
  (i.e., optional) dependencies are listed in ``requirements/extra.txt``.
  We don't often add new default and extra dependencies.  If you are considering
  adding code that has a dependency, you should first consider adding a gallery
  example.  Typically, new proposed dependencies would first be added as extra
  dependencies.  Extra dependencies should be easy to install on all platforms
  and widely-used.  New default dependencies should be easy to install on all
  platforms, widely-used in the community, and have demonstrated potential for
  wide-spread use in NetworkX.
* Use the following import conventions::

   import numpy as np
   import scipy as sp
   import matplotlib as mpl
   import matplotlib.pyplot as plt
   import pandas as pd
   import networkx as nx

  After importing ``sp`` for ``scipy``::

   import scipy as sp

  access the relevant scipy subpackages from the top-level ``sp`` namespace, e.g.::

   sp.sparse.linalg

  Instead of ``from scipy.sparse import linalg`` or
  ``import scipy.sparse.linalg as spla``.

  For example, many libraries have a ``linalg`` subpackage: ``nx.linalg``,
  ``np.linalg``, ``sp.linalg``, ``sp.sparse.linalg``. The above import
  pattern makes the origin of any particular instance of ``linalg`` explicit.

* Use the decorator ``not_implemented_for`` in ``networkx/utils/decorators.py``
  to designate that a function doesn't accept 'directed', 'undirected',
  'multigraph' or 'graph'.  The first argument of the decorated function should
  be the graph object to be checked.

  .. code-block:: python

      @nx.not_implemented_for("directed", "multigraph")
      def function_not_for_MultiDiGraph(G, others):
          # function not for graphs that are directed *and* multigraph
          pass


      @nx.not_implemented_for("directed")
      @nx.not_implemented_for("multigraph")
      def function_only_for_Graph(G, others):
          # function not for directed graphs *or* for multigraphs
          pass
* Functions should avoid returning numpy scalars (e.g., `numpy.int64`, `numpy.float64`)
  to ensure better compatibility and avoid issues with parts of the codebase that may
  not recognize or handle numpy scalars properly. If a function returns a numpy scalar,
  it should be converted to a native Python type.

  .. code-block:: python

      def convert_to_python_type():
          # Perform some computation resulting in a numpy scalar
          a = np.int64(42)
          # Convert to a Python scalar before returning
          return a.item()

Testing
-------

``networkx`` has an extensive test suite that ensures correct
execution on your system.  The test suite has to pass before a pull
request can be merged, and tests should be added to cover any
modifications to the code base.
We make use of the `pytest <https://docs.pytest.org/en/latest/>`__
testing framework, with tests located in the various
``networkx/submodule/tests`` folders.

To run all tests::

    $ PYTHONPATH=. pytest networkx

Or the tests for a specific submodule::

    $ PYTHONPATH=. pytest networkx/readwrite

Or tests from a specific file::

    $ PYTHONPATH=. pytest networkx/readwrite/tests/test_edgelist.py

Or a single test within that file::

    $ PYTHONPATH=. pytest networkx/readwrite/tests/test_edgelist.py::test_parse_edgelist_with_data_list

Use ``--doctest-modules`` to run doctests.
For example, run all tests and all doctests using::

    $ PYTHONPATH=. pytest --doctest-modules networkx

Tests for a module should ideally cover all code in that module,
i.e., statement coverage should be at 100%.

To measure the test coverage, run::

  $ PYTHONPATH=. pytest --cov=networkx networkx

This will print a report with one line for each file in `networkx`,
detailing the test coverage::

  Name                                             Stmts   Miss Branch BrPart  Cover
  ----------------------------------------------------------------------------------
  networkx/__init__.py                                33      2      2      1    91%
  networkx/algorithms/__init__.py                    114      0      0      0   100%
  networkx/algorithms/approximation/__init__.py       12      0      0      0   100%
  networkx/algorithms/approximation/clique.py         42      1     18      1    97%
  ...

There are additional pytest plugins that provide enhanced features for running
the test suite. These can be installed with
``pip install -r requirements/test-extras.txt``.
For example, with these plugins installed it is possible to run the tests
(including doctests) with multiple cores in randomized order with::

   pytest -n auto --doctest-modules --pyargs networkx


Adding tests
~~~~~~~~~~~~

If you're **new to testing**, see existing test files for examples of things to do.
**Don't let the tests keep you from submitting your contribution!**
If you're not sure how to do this or are having trouble, submit your pull request
anyway.
We will help you create the tests and sort out any kind of problem during code review.

Tests for drawing
^^^^^^^^^^^^^^^^^

When adding tests for the matplotlib-based drawing functions in ``nx_pylab.py``,
the ``subplots`` fixture should be used to create a figure and axis object for
each unit test.
Using this fixture prevents figure and axis objects from being unintentionally
re-used between tests.
An example usage in ``networkx/drawing/tests/test_pylab.py`` would look something
like:

.. code-block:: python

   def test_my_new_viz_test(subplots):
       fig, ax = subplots

       <remainder of unit test>

Image comparison
^^^^^^^^^^^^^^^^

.. note::
   Image comparison tests require the ``pytest-mpl`` extension, which can be
   installed with::

      pip install pytest-mpl

   If ``pytest-mpl`` is not installed, the test suite may emit warnings related
   to ``pytest.mark.mpl_image_compare`` - these can be safely ignored.

To run image comparisons::

    $ PYTHONPATH=. pytest --mpl --pyargs networkx.drawing

The ``--mpl`` tells ``pytest`` to use ``pytest-mpl`` to compare the generated plots
with baseline ones stored in ``networkx/drawing/tests/baseline``.

To add a new test, add a test function to ``networkx/drawing/tests`` that
returns a Matplotlib figure (or any figure object that has a savefig method)
and decorate it as follows::

    @pytest.mark.mpl_image_compare
    def test_barbell():
        fig = plt.figure()
        barbell = nx.barbell_graph(4, 6)
        # make sure to fix any randomness
        pos = nx.spring_layout(barbell, seed=42)
        nx.draw(barbell, pos=pos)
        return fig

Then create a baseline image to compare against later::

    $ pytest -k test_barbell --mpl-generate-path=networkx/drawing/tests/baseline

.. note:: In order to keep the size of the repository from becoming too large, we
   prefer to limit the size and number of baseline images we include.

And test::

    $ pytest -k test_barbell --mpl

Documentation
-------------

.. include:: ../README.rst

Adding examples
~~~~~~~~~~~~~~~

The gallery examples are managed by
`sphinx-gallery <https://sphinx-gallery.readthedocs.io/>`_.
The source files for the example gallery are ``.py`` scripts in ``examples/`` that
generate one or more figures. They are executed automatically by sphinx-gallery when the
documentation is built. The output is gathered and assembled into the gallery.

Building the example gallery locally requires that the additional dependencies
in ``requirements/example.txt`` be installed in your development environment.

You can **add a new** plot by placing a new ``.py`` file in one of the directories inside the
``examples`` directory of the repository. See the other examples to get an idea for the
format.

.. note:: Gallery examples should start with ``plot_``, e.g. ``plot_new_example.py``

General guidelines for making a good gallery plot:

* Examples should highlight a single feature/command.
* Try to make the example as simple as possible.
* Data needed by examples should be included in the same directory and the example script.
* Add comments to explain things that aren't obvious from reading the code.
* Describe the feature that you're showcasing and link to other relevant parts of the
  documentation.

Adding References
~~~~~~~~~~~~~~~~~

If you are contributing a new algorithm (or an improvement to a current algorithm),
a reference paper or resource should also be provided in the function docstring.
For references to published papers, we try to follow the
`Chicago Citation Style <https://en.wikipedia.org/wiki/The_Chicago_Manual_of_Style>`__.
The quickest way of generating citation in this style is
by searching for the paper on `Google Scholar <https://scholar.google.com/>`_ and clicking on
the ``cite`` button. It will pop up the citation of the paper in multiple formats, and copy the
``Chicago`` style.

We prefer adding DOI links for URLs. If the DOI link resolves to a paywalled version of
the article, we prefer adding a link to the arXiv version (if available) or any other
publicly accessible copy of the paper.

An example of a reference::

    .. [1] Cheong, Se-Hang, and Yain-Whar Si. "Force-directed algorithms for schematic drawings and
    placement: A survey." Information Visualization 19, no. 1 (2020): 65-91.
    https://doi.org/10.1177%2F1473871618821740


If the resource is uploaded as a PDF/DOCX/PPT on the web (lecture notes, presentations) it is better
to use the `wayback machine <https://web.archive.org/>`_ to create a snapshot of the resource
and link the internet archive link. The URL of the resource can change, and it creates unreachable
links from the documentation.

Using Math Formulae and Latex Formatting in Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When working with docstrings that contain math symbols or formulae
use raw strings (``r"""``) to ensure proper rendering.
While LaTeX formatting can improve the appearance of the rendered documentation,
it's best to keep it simple and readable.

An example of a math formula::

      .. math::
          Ax = \lambda x

.. math::
    Ax = \lambda x

Some inline math::

    These are Cheeger's Inequalities for \d-Regular graphs:
    $\frac{d- \lambda_2}{2} \leq h(G) \leq \sqrt{2d(d- \lambda_2)}$

These are Cheeger's Inequalities for \d-Regular graphs:
$\frac{d- \lambda_2}{2} \leq h(G) \leq \sqrt{2d(d- \lambda_2)}$

Bugs
----

Please `report bugs on GitHub <https://github.com/networkx/networkx/issues>`_.

Policies
--------

- Deprecation Policies

  - :doc:`NetworkX deprecation policy <deprecations>`
  - :external+neps:doc:`Python version support <nep-0029-deprecation_policy>`

- Code of Conduct

  This online space is operating under the
  `NumFOCUS Code of Conduct <https://numfocus.org/code-of-conduct>`_
  which also governs all interactions within the NetworkX project.
  See `the NetworkX code of conduct page.
  <https://networkx.org/documentation/stable/developer/code_of_conduct.html>`_

  If you would like to report violation of Code of Conduct please

  - Contact one of the NetworkX online space moderators

    - `Dan Schult <https://github.com/dschult>`_,
      `Aditi Juneja <https://github.com/Schefflera-Arboricola>`_,
      or `Ross Barnowski <https://github.com/rossbar>`_ , OR

  - Report the violation either anonymously or with your name, using
    `the NumFOCUS Code of Conduct form <https://numfocus.typeform.com/to/ynjGdT>`_.
    The report goes to the independent NumFOCUS Code of Conduct Working Group.
    You can find more information about the group members and the procedure at
    `the Code of Conduct website. <https://numfocus.org/code-of-conduct>`_

