#!/usr/bin/env bash

set -e

section "build_docs section"

pip install --retries 3 -q -r requirements/doc.txt
pip list
export SPHINXCACHE=$HOME/.cache/sphinx
cd doc
make html
make latexpdf LATEXMKOPTS="-silent"
cp -a build/latex/networkx_reference.pdf build/html/_downloads/.
cd ..

section_end "build_docs section"

set +e
