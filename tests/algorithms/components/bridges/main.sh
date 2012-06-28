#!/usr/bin/env bash

for f in */*.sh
do
  echo $f
  cd `dirname $f`
  ./`basename $f`
  cd -
done

