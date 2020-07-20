.. _contributor_guide:

Contributor Guide
=================

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
     system. To ensure you have a properly-configured development environment
     for running the tests, see `Build environment setup`_.

4. Format your code:

   * We use psf/black to format Python code.

5. To submit your contribution:

   * Push your changes back to your fork on GitHub::

      git push origin bugfix-for-issue-1480

   * Go to GitHub. The new branch will show up with a green Pull Request
     button---click it.

   * If you want, post on the `mailing list
     <http://groups.google.com/group/networkx-discuss>`_ to explain your changes or
     to ask for review.

For a more detailed discussion, read these :doc:`detailed documents
<gitwash/index>` on how to use Git with ``networkx``
(`<https://networkx.github.io/documentation/latest/developer/gitwash/index.html>`_).

6. Review process:

    * Reviewers (the other developers and interested community members) will
      write inline and/or general comments on your Pull Request (PR) to help
      you improve its implementation, documentation, and style.  Every single
      developer working on the project has their code reviewed, and we've come
      to see it as friendly conversation from which we all learn and the
      overall code quality benefits.  Therefore, please don't let the review
      discourage you from contributing: its only aim is to improve the quality
      of project, not to criticize (we are, after all, very grateful for the
      time you're donating!).

    * To update your pull request, make your changes on your local repository
      and commit. As soon as those changes are pushed up (to the same branch as
      before) the pull request will update automatically.

    * `Travis-CI <https://travis-ci.org/>`_, a continuous integration service,
      is triggered after each Pull Request update to build the code and run unit
      tests of your branch. The Travis tests must pass before your PR can be merged.
      If Travis fails, you can find out why by clicking on the "failed" icon (red
      cross) and inspecting the build and test log.

    * `AppVeyor <http://ci.appveyor.com>`_, is another continuous integration
      service, which we use.  You will also need to make sure that the AppVeyor
      tests pass.

.. note::

   If closing a bug, also add "Fixes #1480" where 1480 is the issue number.

7. Document changes

   If your change introduces any API modifications, please update
   ``doc/release/release_dev.rst``.

   If your change introduces a deprecation, add a reminder to
   ``doc/developer/deprecations.rst`` for the team to remove the
   deprecated functionality in the future.

.. note::

   To reviewers: make sure the merge message has a brief description of the
   change(s) and if the PR closes an issue add, for example, "Closes #123"
   where 123 is the issue number.


Divergence between ``upstream master`` and your feature branch
--------------------------------------------------------------

Never merge the main branch into yours. If GitHub indicates that the
branch of your Pull Request can no longer be merged automatically, rebase
onto master::

   git checkout master
   git pull upstream master
   git checkout bugfix-for-issue-1480
   git rebase master

If any conflicts occur, fix the according files and continue::

   git add conflict-file1 conflict-file2
   git rebase --continue

However, you should only rebase your own branches and must generally not
rebase any branch which you collaborate on with someone else.

Finally, you must push your rebased branch::

   git push --force origin bugfix-for-issue-1480

(If you are curious, here's a further discussion on the
`dangers of rebasing <http://tinyurl.com/lll385>`_.
Also see this `LWN article <http://tinyurl.com/nqcbkj>`_.)

Build environment setup
-----------------------

Once you've cloned your fork of the networkx repository,
you should set up a Python development environment tailored for networkx.
You may choose the environment manager of your choice.
Here we provide instructions for two popular environment managers:
``venv`` (pip based) and ``conda`` (Anaconda or Miniconda).

venv
^^^^
When using ``venv``, you may find the following bash commands useful::

  # Create a virtualenv named ``networkx-dev`` that lives in the directory of
  # the same name
  python -m venv networkx-dev
  # Activate it
  source networkx-dev/bin/activate
  # Install all development and runtime dependencies of networkx
  pip install -r <(cat requirements/*.txt)
  # Build and install networkx from source
  pip install -e .
  # Test your installation
  PYTHONPATH=. pytest networkx

conda
^^^^^

When using conda, you may find the following bash commands useful::

  # Create a conda environment named ``networkx-dev``
  conda create --name networkx-dev
  # Activate it
  conda activate networkx-dev
  # Install major development and runtime dependencies of networkx
  # (the rest can be installed from conda-forge or pip, if needed)
  conda install `for i in requirements/{default,test,doc,extras}.txt; do echo -n " --file $i "; done`
  # Install minimal testing dependencies
  conda install pytest
  # Install networkx from source
  pip install -e . --no-deps
  # Test your installation
  PYTHONPATH=. pytest networkx


Guidelines
----------

* All code should have tests.
* All code should be documented, to the same
  `standard <https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#docstring-standard>`_
  as NumPy and SciPy.
* All changes are reviewed.  Ask on the
  `mailing list <http://groups.google.com/group/networkx-discuss>`_ if
  you get no response to your pull request.

Stylistic Guidelines
--------------------

* Set up your editor to remove trailing whitespace.
  Follow `PEP08 <www.python.org/dev/peps/pep-0008/>`_.
  Check code with `pyflakes` / `flake8`.

* Use the following import conventions::

   import numpy as np
   import scipy as sp
   import matplotlib as mpl
   import matplotlib.pyplot as plt
   import networkx as nx

   cimport numpy as cnp # in Cython code

Testing
-------

``networkx`` has an extensive test suite that ensures correct
execution on your system.  The test suite has to pass before a pull
request can be merged, and tests should be added to cover any
modifications to the code base.

We make use of the `pytest <https://docs.pytest.org/en/latest/>`__
testing framework, with tests located in the various
``networkx/submodule/tests`` folders.

To use ``pytest``, ensure that the library is installed in development mode::

    $ pip install -e .

Now, run all tests using::

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

Test coverage
-------------

Tests for a module should ideally cover all code in that module,
i.e., statement coverage should be at 100%.

To measure the test coverage, install
`pytest-cov <https://pytest-cov.readthedocs.io/en/latest/>`__
(using ``pip install pytest-cov``) and then run::

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

Pull request codes
------------------

When you submit a pull request to GitHub, GitHub will ask you for a summary.  If
your code is not ready to merge, but you want to get feedback, please consider
using ``WIP: experimental optimization`` or similar for the title of your pull
request. That way we will all know that it's not yet ready to merge and that
you may be interested in more fundamental comments about design.

When you think the pull request is ready to merge, change the title (using the
*Edit* button) to remove the ``WIP:``.

.. _deprecation_policy:


Deprecation policy
------------------

If the behavior of the library has to be changed, a deprecation cycle must be
followed to warn users.

A deprecation cycle is *not* necessary when:

* adding a new function, or
* adding a new keyword argument to the *end* of a function signature, or
* fixing buggy behavior

A deprecation cycle is necessary for *any breaking API change*, meaning a
change where the function, invoked with the same arguments, would return a
different result after the change. This includes:

* changing the order of arguments or keyword arguments, or
* adding arguments or keyword arguments to a function, or
* changing the name of a function, class, method, etc., or
* moving a function, class, etc. to a different module, or
* changing the default value of a function's arguments.

Usually, our policy is to put in place a deprecation cycle over two releases.

Note that the 2-release deprecation cycle is not a strict rule and in some
cases, the developers can agree on a different procedure upon justification
(like when we can't detect the change, or it involves moving or deleting an
entire function for example).

Explicitly not supporting directed or multigraph in a function
--------------------------------------------------------------

Use the decorator ``not_implemented_for`` in ``networkx/utils/decorators.py``
to designate that a function doesn't accept 'directed', 'undirected',
'multigraph' or 'graph'.
The first argument of the decorated function should be the graph
object to be checked.

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

Bugs
----

Please `report bugs on GitHub <https://github.com/networkx/networkx/issues>`_.
