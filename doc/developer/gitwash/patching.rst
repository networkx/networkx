.. highlight:: bash

================
 Making a patch
================

You've discovered a bug or something else you want to change
in `networkx`_ .. |emdash| excellent!

You've worked out a way to fix it |emdash| even better!

You want to tell us about it |emdash| best of all!

The easiest way is to make a *patch* or set of patches.  Here
we explain how.  Making a patch is the simplest and quickest,
but if you're going to be doing anything more than simple
quick things, please consider following the
:ref:`git-development` model instead.

.. _making-patches:

Making patches
==============

Overview
--------

::

   # tell git who you are
   git config --global user.email you@yourdomain.example.com
   git config --global user.name "Your Name Comes Here"
   # get the repository if you don't have it
   git clone git://github.com/networkx/networkx.git
   # make a branch for your patching
   cd networkx
   git branch the-fix-im-thinking-of
   git checkout the-fix-im-thinking-of
   # hack, hack, hack
   # Tell git about any new files you've made
   git add somewhere/tests/test_my_bug.py
   # commit work in progress as you go
   git commit -am 'BF - added tests for Funny bug'
   # hack hack, hack
   git commit -am 'BF - added fix for Funny bug'
   # make the patch files
   git format-patch -M -C master

Then, send the generated patch files to the `networkx
mailing list`_ |emdash| where we will thank you warmly.

In detail
---------

#. Tell git who you are so it can label the commits you've
   made::

      git config --global user.email you@yourdomain.example.com
      git config --global user.name "Your Name Comes Here"

#. If you don't already have one, clone a copy of the
   `networkx`_ repository::

      git clone git://github.com/networkx/networkx.git
      cd networkx

#. Make a 'feature branch'.  This will be where you work on
   your bug fix.  It's nice and safe and leaves you with
   access to an unmodified copy of the code in the main
   branch::

      git branch the-fix-im-thinking-of
      git checkout the-fix-im-thinking-of

#. Do some edits, and commit them as you go::

      # hack, hack, hack
      # Tell git about any new files you've made
      git add somewhere/tests/test_my_bug.py
      # commit work in progress as you go
      git commit -am 'BF - added tests for Funny bug'
      # hack hack, hack
      git commit -am 'BF - added fix for Funny bug'

   Note the ``-am`` options to ``commit``. The ``m`` flag just
   signals that you're going to type a message on the command
   line.  The ``a`` flag |emdash| you can just take on faith |emdash|
   or see `why the -a flag?`_.

#. When you have finished, check you have committed all your
   changes::

      git status

#. Finally, make your commits into patches.  You want all the
   commits since you branched from the ``master`` branch::

      git format-patch -M -C master

   You will now have several files named for the commits:

   .. code-block:: none

      0001-BF-added-tests-for-Funny-bug.patch
      0002-BF-added-fix-for-Funny-bug.patch

   Send these files to the `networkx mailing list`_.

When you are done, to switch back to the main copy of the
code, just return to the ``master`` branch::

   git checkout master

Moving from patching to development
===================================

If you find you have done some patches, and you have one or
more feature branches, you will probably want to switch to
development mode.  You can do this with the repository you
have.

Fork the `networkx`_ repository on github |emdash| :ref:`forking`.
Then::

   # checkout and refresh master branch from main repo
   git checkout master
   git pull origin master
   # rename pointer to main repository to 'upstream'
   git remote rename origin upstream
   # point your repo to default read / write to your fork on github
   git remote add origin git@github.com:your-user-name/networkx.git
   # push up any branches you've made and want to keep
   git push origin the-fix-im-thinking-of

Then you can, if you want, follow the
:ref:`development-workflow`.

.. include:: links.inc
