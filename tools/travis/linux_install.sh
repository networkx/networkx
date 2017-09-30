#!/usr/bin/env bash
set -e

# create new empty venv
virtualenv -p python ~/venv
source ~/venv/bin/activate

if [[ "${OPTIONAL_DEPS}" == 1 ]]; then

  # needed to build Python binding for GDAL
  export CPLUS_INCLUDE_PATH=/usr/include/gdal
  export C_INCLUDE_PATH=/usr/include/gdal

  # needed for view_graphviz and default_opener
  DIR=~/.local/share/applications
  mkdir -p $DIR
  FILE=$DIR/png.desktop
  cat <<EOF >$FILE
[Desktop Entry]
Name=png
MimeType=image/png;
Exec=/usr/bin/file
Type=Application
Terminal=true
NoDisplay=true
EOF

  xdg-mime default png.desktop image/png

fi

set +e
