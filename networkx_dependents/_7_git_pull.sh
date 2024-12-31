#!/usr/bin/env bash
for dir in repos*/*/
do
    pushd $dir
    echo $dir
    git pull --rebase
    popd
done
