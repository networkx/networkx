#!/usr/bin/env bash
set -ex

# create new empty venv
virtualenv -p python ~/venv
source ~/venv/bin/activate

# install required packages
pip install --upgrade pip
pip install requirements.txt

if [[ "${OPTIONAL_DEPS}" == pip ]]; then

  # needed to build Python binding for GDAL
  export CPLUS_INCLUDE_PATH=/usr/include/gdal
  export C_INCLUDE_PATH=/usr/include/gdal

  # install optional packages
  pip install --retries 3 $PIP_FLAGS -r requirements/extras.txt

fi

set +ex
