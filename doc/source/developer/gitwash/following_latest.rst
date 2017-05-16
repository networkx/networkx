.. _following-latest:

=============================
 Following the latest source
=============================

These are the instructions if you just want to follow the latest
*networkx* source, but you don't need to do any development for now.

The steps are:

* :ref:`install-git`
* get local copy of the `networkx github`_ git repository
* update local copy from time to time

Get the local copy of the code
==============================

From the command line::

   git clone git://github.com/networkx/networkx.git

You now have a copy of the code tree in the new ``networkx`` directory.

Updating the code
=================

From time to time you may want to pull down the latest code.  It is necessary
to add the networkx repository as a remote to your configuration file.  We call it
upstream.

   git remote set-url upstream https://github.com/networkx/networkx.git

Now git knows where to fetch updates from.

   cd networkx
   git fetch upstream

The tree in ``networkx`` will now have the latest changes from the initial
repository, unless you have made local changes in the meantime.  In this
case, you have to merge.

    git merge upstream/master

It is also possible to update your local fork directly from GitHub:

  1. Open your fork on GitHub.
  2. Click on 'Pull Requests'.
  3. Click on 'New Pull Request'.  By default, GitHub will compare the
  original with your fork.  If you didn’t make any changes, there is
  nothing to compare.
  4. Click on 'Switching the base' or click 'Edit' and switch the
  base manually.  Now GitHub will compare your fork with the original,
  and you should see all the latest changes.
  5. Click on 'Click to create a pull request for this comparison' and name
  your pull request.
  6. Click on Send pull request.
  7. Scroll down and click 'Merge pull request' and finally 'Confirm merge'.
  You will be able to merge it automatically unless you did not change you local repo.


.. include:: links.inc
