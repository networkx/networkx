Release Process
===============

- Set release variables:

      export VERSION=<version number>
      export PREVIOUS=<previous version number>
      export ORG="networkx"
      export REPO="networkx"

  If this is a prerelease:

      export NOTES="doc/release/release_dev.rst"

  If this is release:

      export NOTES="doc/release/release_${VERSION}.rst"
      git rm doc/release/release_dev.rst

- Autogenerate release notes:

      changelist ${ORG}/${REPO} networkx-${PREVIOUS} main --version ${VERSION}  --out ${NOTES} --format rst

- Edit ``doc/_static/version_switcher.json`` in order to add the release, move the
  key value pair `"preferred": true` to the most recent stable version, and commit.

- Update ``__version__`` in ``networkx/__init__.py``.

- Commit changes::

   git add networkx/__init__.py ${NOTES} doc/_static/version_switcher.json
   git commit -m "Designate ${VERSION} release"

- Add the version number as a tag in git::

   git tag -s networkx-${VERSION} -m "signed ${VERSION} tag"

- Push the new meta-data to github::

   git push --tags origin main

  (where ``origin`` is the name of the
   ``github.com:networkx/networkx`` repository.)

- Review the github release page::

   https://github.com/networkx/networkx/tags

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
      rm -rf stable
      cp -rf networkx-<major>.<minor> stable
      git add networkx-<major>.<minor> stable
      git commit -m "Add <major>.<minor> docs"
      git push  # force push---be careful!

- Update ``__version__`` in ``networkx/__init__.py``.

 - Commit and push changes::

    git add networkx/__init__.py 
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
