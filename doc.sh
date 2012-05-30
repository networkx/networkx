#!/usr/bin/env bash

if [ $# -ne 0 ]
then
  case "$1" in
    -w|--webpage)
      open doc/build/html/index.html
      exit
      ;;
  esac
fi

echo "$@"

exit

abspath_script=`readlink -f -e "$0"`
lib=`dirname "$abspath_script"`

if [ "$PYTHONPATH" ]
then
  export PYTHONPATH="$lib"
else
  export PYTHONPATH="$lib:$PYTHONPATH"
fi

cd "$lib/doc"
make html


