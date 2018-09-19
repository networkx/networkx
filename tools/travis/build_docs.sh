#!/usr/bin/env bash

set -ex

pip install --retries 3 -q -r requirements/doc.txt
pip list
export SPHINXCACHE=$HOME/.cache/sphinx
cd doc
make html
make doctest
make latexpdf
cd ..

set +ex
