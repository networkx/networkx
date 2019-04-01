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

if [[ "${MINIMUM_REQUIREMENTS}" == 1 ]]; then
    sed -i 's/>=/==/g' requirements/default.txt
    sed -i 's/>=/==/g' requirements/extras.txt
    sed -i 's/>=/==/g' requirements/test.txt
    sed -i 's/>=/==/g' requirements/doc.txt
fi

set +e
