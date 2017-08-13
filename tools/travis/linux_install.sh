#!/usr/bin/env bash
set -ex

# create new empty venv
virtualenv -p python ~/venv
source ~/venv/bin/activate

if [[ "${OPTIONAL_DEPS}" == pip ]]; then

  # needed to build Python binding for GDAL
  export CPLUS_INCLUDE_PATH=/usr/include/gdal
  export C_INCLUDE_PATH=/usr/include/gdal

fi

set +ex
