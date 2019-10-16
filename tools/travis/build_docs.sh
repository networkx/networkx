#!/usr/bin/env bash

set -e

section "build_docs section"

pip install --retries 3 -q -r requirements/doc.txt
pip list
export SPHINXCACHE=$HOME/.cache/sphinx
cd doc
make html
make latexpdf
cd ..

section_end "build_docs section"

set +e
