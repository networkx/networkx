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

- Add the version number as a tag in git::

   git tag -s [-u <key-id>] v<major>.<minor>.0

  (If you do not have a gpg key, use -m instead; it is important for
  Debian packaging that the tags are annotated)

- Push the new meta-data to github::

   git push --tags upstream master

  (where ``upstream`` is the name of the
   ``github.com:networkx/networkx`` repository.)

- Publish on PyPi::

   python setup.py register
   python setup.py sdist upload
   python setup.py bdist_wheel upload

- Increase the version number

  - Toggle ``dev = False`` to ``dev = True`` in ``networkx/release.py``.
  - Update ``major`` and ``minor`` in ``networkx/release.py``.

- Update the web frontpage:
  The webpage is kept in a separate repo: networkx-website

  - Sync your branch with the remote repo: ``git pull``.
    If you try to ``make github`` when your branch is out of sync, it
    creates headaches.
  - Update ``_templates/sidebar_versions.html``.
  - Deploy using ``make github``.

- Update ``https://readthedocs.org/projects/networkx/versions/``

- Post release notes on mailing list.

  - networkx-discuss@googlegroups.com
