Release Process
===============

- Set release variables:

  .. code-block:: bash

      export VERSION=<version number>
      export PREVIOUS=<previous version number>
      export ORG="networkx"
      export REPO="networkx"

  If this is a prerelease:

  .. code-block:: bash

      export NOTES="doc/release/release_dev.rst"

  If this is release:

  .. code-block:: bash

      export NOTES="doc/release/release_${VERSION}.rst"
      git rm doc/release/release_dev.rst

- Autogenerate release notes:

  .. code-block:: bash

      changelist ${ORG}/${REPO} networkx-${PREVIOUS} main --version ${VERSION} --out ${NOTES} --format rst
      changelist ${ORG}/${REPO} networkx-${PREVIOUS} main --version ${VERSION} --out ${VERSION}.md

- Edit ``doc/_static/version_switcher.json`` in order to add the release, move the
  key value pair `"preferred": true` to the most recent stable version, and commit.

- Update ``doc/release/index.rst``.

- Update ``__version__`` in ``networkx/__init__.py``.

- Commit changes:

  .. code-block:: bash

      git add networkx/__init__.py ${NOTES} doc/_static/version_switcher.json doc/release/index.rst
      git commit -m "Designate ${VERSION} release"

- Add the version number as a tag in git:

  .. code-block:: bash

      git tag -s networkx-${VERSION} -m "signed ${VERSION} tag"

- Push the new meta-data to github:

  .. code-block:: bash

      git push --tags origin main

  (where ``origin`` is the name of the ``github.com:networkx/networkx`` repository.)

- Review the github release page: https://github.com/networkx/networkx/tags

- Update documentation on the web:

  The documentation is kept in a separate repo:
  https://github.com/networkx/documentation

  - Wait for the CI service to deploy to GitHub Pages
  - Sync your branch with the remote repo: ``git pull``.
  - Copy the documentation built by the CI service.
    Assuming you are at the top-level of the ``documentation`` repo:

    .. code-block:: bash

        # FIXME - use eol_banner.html
        cp -a latest ../networkx-${VERSION}
        git reset --hard <commit from last release>
        mv ../networkx-${VERSION} .
        rm -rf stable
        cp -rf networkx-${VERSION} stable
        git add networkx-${VERSION} stable
        git commit -m "Add ${VERSION} docs"
        git push  # force push---be careful!

- Update ``__version__`` in ``networkx/__init__.py``.

  - Commit and push changes:

    .. code-block:: bash

        git add networkx/__init__.py
        git commit -m "Bump release version"
        git push origin main

- Update the web frontpage:

  The webpage is kept in a separate repo: https://github.com/networkx/website

  - Sync your branch with the remote repo: ``git pull``.
    If you try to ``make github`` when your branch is out of sync, it
    creates headaches.
  - Update ``build/index.html``.
  - Edit ``build/_static/docversions.js`` and commit
  - Push your changes to the repo.
  - Deploy using ``make github``.

- Post release notes on mailing list.

  - networkx-discuss@googlegroups.com
