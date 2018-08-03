#!/usr/bin/env bash
set -ex

# create new empty venv
virtualenv -p python ~/venv
source ~/venv/bin/activate

if [[ "${OPTIONAL_DEPS}" == 1 ]]; then

  # needed to build Python binding for GDAL
  export CPLUS_INCLUDE_PATH=/usr/include/gdal
  export C_INCLUDE_PATH=/usr/include/gdal

  # needed for view_graphviz and default_opener
  alias xdg-open="file"

fi

set +ex
