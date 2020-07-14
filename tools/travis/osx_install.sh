#!/usr/bin/env bash
set -ex

section "OSX install section"

# set up Python and virtualenv on OSX
git clone https://github.com/matthew-brett/multibuild
source multibuild/osx_utils.sh
get_macpython_environment $TRAVIS_PYTHON_VERSION venv

if [[ "${OPTIONAL_DEPS}" == 1 ]]; then
    brew install graphviz
    dot -V
    sed -i "" 's/^gdal.*/gdal==3.1.2/' requirements/extras.txt
fi

section_end "OSX install section"

set +ex
