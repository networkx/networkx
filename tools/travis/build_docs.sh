#!/usr/bin/env bash

set -e

pip install --retries 3 -q -r requirements/doc.txt
export SPHINXCACHE=$HOME/.cache/sphinx
cd doc
make html
make latexpdf
cd ..

set +e
