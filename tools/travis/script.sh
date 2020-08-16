#!/usr/bin/env bash

set -e

section "script section"

# Run pytest.
if [[ "${REPORT_COVERAGE}" == 1 ]]; then
  pytest --cov=networkx --runslow --doctest-modules --pyargs networkx
else
  pytest --doctest-modules --durations=10 --pyargs networkx
fi

section_end "script section"

set +e
