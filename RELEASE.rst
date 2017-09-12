How to make a new release of ``networkx``
=========================================

- Update the release notes:

  1. Review and cleanup ``doc/release/release_dev.txt``,

  2. Fix code in documentation by running
     ``cd doc && make doctest``.

  3. Make a list of merges and contributors by running
     ``doc/release/contribs.py <tag of previous release>``.

  4. Paste this list at the end of the ``release_dev.txt``. Scan the PR titles
     for highlights, deprecations, and API changes, and mention these in the
     relevant sections of the notes.

  5. Rename to ``doc/release/release_<major>.<minor>.txt``.

  6. Copy ``doc/release/release_template.txt`` to
     ``doc/release/release_dev.txt`` for the next release.

  7. Update ``doc/news.rst``.

- Toggle ``dev = True`` to ``dev = False`` in ``networkx/release.py``.

- Commit changes.

- Add the version number as a tag in git::

   git tag -s [-u <key-id>] networkx-<major>.<minor>

  (If you do not have a gpg key, use -m instead; it is important for
  Debian packaging that the tags are annotated)

- Push the new meta-data to github::

   git push --tags upstream master

  (where ``upstream`` is the name of the
   ``github.com:networkx/networkx`` repository.)

- Review the github release page::

  https://github.com/networkx/networkx/releases

- Publish on PyPi::

   git clean -fxd
   python setup.py sdist --formats=zip
   twine upload -s dist/networkx*.zip

- Increase the version number

  - Toggle ``dev = False`` to ``dev = True`` in ``networkx/release.py``.
  - Update ``major`` and ``minor`` in ``networkx/release.py``.

- Build the documentation::

    cd doc
    make docs

  The built documentation is in ``build/html``.

- Push documentation to the web:
  The documentation is kept in a separate repo: networkx/documentation

  - Sync your branch with the remote repo: ``git pull``.
  - Copy the documentation that you built in the previous step.
    Assuming your ``networkx`` and your ``documentation`` repos are in the
    same parent directory::

      cp -a ../networkx/doc/build/html networkx-<major>.<minor> 
      git add networkx-<major>.<minor>
      git commit -m "Add <major>.<minor> docs"
      git push

  - Update the symlink to ``stable``.
  - Push upstream

- Update the web frontpage:
  The webpage is kept in a separate repo: networkx/website

  - Sync your branch with the remote repo: ``git pull``.
    If you try to ``make github`` when your branch is out of sync, it
    creates headaches.
  - Update ``_templates/sidebar_versions.html``.
  - Edit ``_static/docversions.js`` and commit
  - Push your changes to the repo.
  - Deploy using ``make github``.

- Post release notes on mailing list.

  - networkx-discuss@googlegroups.com
