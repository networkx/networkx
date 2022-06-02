Release Process
===============

- Update the release notes:

  1. Review and cleanup ``doc/release/release_dev.rst``,

  2. Fix code in documentation by running
     ``cd doc && make doctest``.

  3. Make a list of merges and contributors by running
     ``doc/release/contribs.py <tag of previous release>``.

  4. Paste this list at the end of the ``release_dev.rst``. Scan the PR titles
     for highlights, deprecations, and API changes, and mention these in the
     relevant sections of the notes.

  5. Rename to ``doc/release/release_<major>.<minor>.rst``.

  6. Copy ``doc/release/release_template.rst`` to
     ``doc/release/release_dev.rst`` for the next release.

  7. Add ``release_<major>.<minor>`` to ``doc/release/index.rst``.

- Delete developer banner on docs::

   git rm doc/_templates/layout.html

- Update ``__version__`` in ``networkx/__init__.py``.

- Commit changes::

   git add networkx/__init__.py
   git commit -m "Designate X.X release"

- Add the version number as a tag in git::

   git tag -s [-u <key-id>] networkx-<major>.<minor> -m 'signed <major>.<minor> tag'

  (If you do not have a gpg key, use -m instead; it is important for
  Debian packaging that the tags are annotated)

- Push the new meta-data to github::

   git push --tags origin main

  (where ``origin`` is the name of the
   ``github.com:networkx/networkx`` repository.)

- Review the github release page::

   https://github.com/networkx/networkx/tags

- Pin badges in ``README.rst``::

  - https://github.com/networkx/networkx/workflows/test/badge.svg?tag=networkx-<major>.<minor>
  - https://github.com/networkx/networkx/actions?query=branch%3Anetworkx-<major>.<minor>

- Publish on PyPi::

   git clean -fxd
   pip install -r requirements/release.txt
   python -m build --sdist --wheel
   twine upload -s dist/*

- Unpin badges in ``README.rst``::

   git restore README.rst 

- Update documentation on the web:
  The documentation is kept in a separate repo: networkx/documentation

  - Wait for the CI service to deploy to GitHub Pages
  - Sync your branch with the remote repo: ``git pull``.
  - Copy the documentation built by the CI service.
    Assuming you are at the top-level of the ``documentation`` repo::

      # FIXME - use eol_banner.html
      cp -a latest ../networkx-<major>.<minor>
      git reset --hard <commit from last release>
      mv ../networkx-<major>.<minor> .
      ln -sfn networkx-<major>.<minor> stable
      git add networkx-<major>.<minor> stable
      git commit -m "Add <major>.<minor> docs"
      git push  # force push---be careful!

- Update ``__version__`` in ``networkx/__init__.py``.

- Create ``doc/_templates/layout.html`` with::

    {% extends "!layout.html" %}

    {% block content %}
      {% include "dev_banner.html" %}
      {{ super() }}
    {% endblock %}

 - Commit and push changes::

    git add networkx/__init__.py doc/_templates/layout.html
    git commit -m "Bump release version"
    git push origin main

- Update the web frontpage:
  The webpage is kept in a separate repo: networkx/website

  - Sync your branch with the remote repo: ``git pull``.
    If you try to ``make github`` when your branch is out of sync, it
    creates headaches.
  - Update ``build/index.html``.
  - Edit ``build/_static/docversions.js`` and commit
  - Push your changes to the repo.
  - Deploy using ``make github``.

- Post release notes on mailing list.

  - networkx-discuss@googlegroups.com
