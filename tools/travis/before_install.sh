#!/usr/bin/env bash
set -e

section () {
    echo -en "travis_fold:start:$1\r"
}

section_end () {
    echo -en "travis_fold:end:$1\r"
}

export -f section
export -f section_end

set +e
