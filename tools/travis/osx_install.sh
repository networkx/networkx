#!/usr/bin/env bash
set -ex

# set up Python and virtualenv on OSX
git clone https://github.com/matthew-brett/multibuild
source multibuild/osx_utils.sh
get_macpython_environment $TRAVIS_PYTHON_VERSION venv

if [[ "${OPTIONAL_DEPS}" == pip ]]; then
  brew install graphviz
  sed -i "" 's/^gdal.*/gdal==1.11.2/' requirements/extras.txt
fi

set +ex
