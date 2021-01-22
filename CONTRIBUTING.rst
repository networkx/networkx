.. _contributor_guide:

Contributor Guide
=================

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
         pip install -r <(cat requirements/{default,developer,doc,optional,test}.txt)
         #
         # (Optional) Install pygraphviz, pydot, and gdal packages
         # These packages require that you have your system properly configured
         # and what that involves differs on various systems.
         # pip install -r requirements/extra.txt
         #
         # Build and install networkx from source
         pip install -e .
         # Test your installation
         PYTHONPATH=. pytest networkx
     
     * ``conda`` (Anaconda or Miniconda)
    
       ::
 
         # Create a conda environment named ``networkx-dev``
         conda create --name networkx-dev
         # Activate it
         conda activate networkx-dev
         # Install main development and runtime dependencies of networkx
         conda install -c conda-forge `for i in requirements/{default,developer,doc,optional,test}.txt; do echo -n " --file $i "; done`
         #
         # (Optional) Install pygraphviz, pydot, and gdal packages
         # These packages require that you have your system properly configured
         # and what that involves differs on various systems.
         # pip install -r requirements/extra.txt
         #
         # Install networkx from source
         pip install -e . --no-deps
         # Test your installation
         PYTHONPATH=. pytest networkx

   * Finally, we recommend you use a pre-commit hook, which runs black when
     you type ``git commit``::

       pre-commit install

2. Develop your contribution:

   * Pull the latest changes from upstream::

      git checkout master
      git pull upstream master

   * Create a branch for the feature you want to work on. Since the
     branch name will appear in the merge message, use a sensible name
     such as 'bugfix-for-issue-1480'::

      git checkout -b bugfix-for-issue-1480

   * Commit locally as you progress (``git add`` and ``git commit``)

3. Test your contribution:

   * Run the test suite locally (see `Testing`_ for details)::

      PYTHONPATH=. pytest networkx

   * Running the tests locally *before* submitting a pull request helps catch
     problems early and reduces the load on the continuous integration
     system.


4. Submit your contribution:

   * Push your changes back to your fork on GitHub::

      git push origin bugfix-for-issue-1480

   * Go to GitHub. The new branch will show up with a green Pull Request
     button---click it.

   * If you want, post on the `mailing list
     <http://groups.google.com/group/networkx-discuss>`_ to explain your changes or
     to ask for review.

For a more detailed discussion, read these :doc:`detailed documents
<gitwash/index>` on how to use Git with ``networkx``
(`<https://networkx.org/documentation/latest/developer/gitwash/index.html>`_).

5. Review process:

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

6. Document changes

   If your change introduces any API modifications, please update
   ``doc/release/release_dev.rst``.

   If your change introduces a deprecation, add a reminder to
   ``doc/developer/deprecations.rst`` for the team to remove the
   deprecated functionality in the future.

   .. note::
   
      To reviewers: make sure the merge message has a brief description of the
      change(s) and if the PR closes an issue add, for example, "Closes #123"
      where 123 is the issue number.


Divergence from ``upstream master``
-----------------------------------

If GitHub indicates that the branch of your Pull Request can no longer
be merged automatically, merge the master branch into yours::

   git fetch upstream master
   git merge upstream/master

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
   The way the text looks in the master branch
   >>>>>>> master

Choose one version of the text that should be kept, and delete the
rest::

   The way the text looks in your branch

Now, add the fixed file::


   git add file_with_conflict.txt

Once you've fixed all merge conflicts, do::

   git commit

.. note::

   Advanced Git users are encouraged to `rebase instead of merge
   <https://networkx.org/documentation/stable/developer/gitwash/development_workflow.html#rebase-on-trunk>`__,
   but we squash and merge most PRs either way.


Guidelines
----------

* All code should have tests.
* All code should be documented, to the same
  `standard <https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#docstring-standard>`_
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

  After importing `sp`` for ``scipy``::

   import scipy as sp

  use the following imports:: 
 
   import scipy.linalg  # call as sp.linalg
   import scipy.sparse  # call as sp.sparse
   import scipy.sparse.linalg  # call as sp.sparse.linalg
   import scipy.stats  # call as sp.stats
   import scipy.optimize  # call as sp.optimize

  For example, many libraries have a ``linalg`` subpackage: ``nx.linalg``,
  ``np.linalg``, ``sp.linalg``, ``sp.sparse.linalg``. The above import
  pattern makes the origin of any particular instance of ``linalg`` explicit.

* Use the decorator ``not_implemented_for`` in ``networkx/utils/decorators.py``
  to designate that a function doesn't accept 'directed', 'undirected',
  'multigraph' or 'graph'.  The first argument of the decorated function should
  be the graph object to be checked.

  .. code-block:: python
  
      @nx.not_implemented_for('directed', 'multigraph')
      def function_not_for_MultiDiGraph(G, others):
          # function not for graphs that are directed *and* multigraph
          pass
  
      @nx.not_implemented_for('directed')
      @nx.not_implemented_for('multigraph')
      def function_only_for_Graph(G, others):
          # function not for directed graphs *or* for multigraphs
          pass


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

    $ PYTHONPATH=. pytest networkx/readwrite/tests/test_yaml.py

Or a single test within that file::

    $ PYTHONPATH=. pytest networkx/readwrite/tests/test_yaml.py::TestYaml::testUndirected

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


Bugs
----

Please `report bugs on GitHub <https://github.com/networkx/networkx/issues>`_.
