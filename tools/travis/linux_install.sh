#!/usr/bin/env bash
set -ex

section "Linux install section"

# create new empty venv
virtualenv -p python ~/venv
source ~/venv/bin/activate

if [[ "${EXTRA_DEPS}" == 1 ]]; then

  # needed to build Python binding for GDAL
  export CPLUS_INCLUDE_PATH=/usr/include/gdal
  export C_INCLUDE_PATH=/usr/include/gdal
  pip install gdal==1.10.0

  # needed for view_graphviz and default_opener
  DIR=~/.local/bin
  export PATH=$DIR:$PATH
  mkdir -p $DIR
  FILE=$DIR/xdg-open
  cat <<EOF >$FILE
#!/bin/sh

echo $1
EOF
  chmod +x $FILE

fi

section_end "Linux install section"

set +ex
