#!/usr/bin/env bash

root_git=`pathresolve.sh -d . .git`
root=`dirname "$root_git"`

path="$root"

if [ "$PYTHONPATH" ]
then
  export PYTHONPATH="$path"
else
  export PYTHONPATH="$path:$PYTHONPATH"
fi

./main.py

