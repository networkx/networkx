#!/usr/bin/env bash

set -e

section "Deploy docs"
if [[ $TRAVIS_PULL_REQUEST == false && $TRAVIS_BRANCH == "master" && $BUILD_DOCS == 1 && $DEPLOY_DOCS == 1 ]]
then
    # "A deploy key is an SSH key that is stored on your server and grants access to a single GitHub repository.
    # This key is attached directly to the repository instead of to a personal user account."
    # -- https://developer.github.com/v3/guides/managing-deploy-keys/#deploy-keys
    #
    # $ ssh-keygen -t ed25519 -C "Networkx Travis Bot" -f deploy-key
    # Your identification has been saved in deploy-key.
    # Your public key has been saved in deploy-key.pub.
    #
    # Add the deploy-key.pub contents to your repo's settings under Settings -> Deploy Keys.
    # Encrypt the private deploy-key for Travis-CI and commit it to the repo
    #
    # $ gem install travis
    # $ travis login
    # $ travis encrypt-file deploy-key
    # storing result as deploy-key.enc
    #
    # The ``travis encrypt-file deploy-key`` command provides the ``openssl`` command below.

    # Decrypt the deploy-key with the Travis-CI key
    openssl aes-256-cbc -K $encrypted_64abb7a9cf51_key -iv $encrypted_64abb7a9cf51_iv -in tools/travis/deploy-key.enc -out deploy-key -d
    chmod 600 deploy-key
    eval `ssh-agent -s`
    ssh-add deploy-key

    # Push the latest docs to the networkx/documentation repo (gh-pages branch)
    GH_REF=git@github.com:networkx/documentation.git
    echo "-- pushing docs --"
    (
    git config --global user.email "travis@travis-ci.com"
    git config --global user.name "NetworkX Travis Bot"

    cd doc
    git clone --quiet --branch=gh-pages --depth=1 ${GH_REF} ghpages_build
    cd ghpages_build

    # Overwrite previous commit
    git rm -r latest
    cp -a ../build/html latest
    cp -a ../build/latex/networkx_reference.pdf latest/_downloads/.
    git add latest
    git commit -m "Deploy GitHub Pages"

    git push --force --quiet "${GH_REF}" gh-pages > /dev/null 2>&1
    cd ../..
    )
else
    echo "-- will only push docs from master --"
fi
section_end "Deploy docs"

set +e
