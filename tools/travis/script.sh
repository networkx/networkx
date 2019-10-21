#!/usr/bin/env bash

set -e

section "script section"

export NX_SOURCE=$PWD
export NX_INSTALL=$(pip show networkx | grep Location | awk '{print $2"/networkx"}')

# nose 1.3.0 does not tell coverage to only cover the requested
# package (except during the report).  So to restrict coverage, we must
# inform coverage through the .coveragerc file.
cp .coveragerc $NX_INSTALL

# Move to new directory so that networkx is not imported from repository.
# Why? Because we want the tests to make sure that NetworkX was installed
# correctly. Example: setup.py might not have included some submodules.
# Testing from the git repository cannot catch a mistake like that.
#
# Export current directory for logs.
cd $NX_INSTALL
printenv PWD

# Run pytest.
if [[ "${REPORT_COVERAGE}" == 1 ]]; then
  pytest --cov=networkx --doctest-modules --pyargs networkx
  cp -a .coverage $NX_SOURCE
elif [[ "${DOCTEST}" == 1 ]]; then
  pytest --doctest-modules --pyargs networkx
else
  pytest --doctest-modules --pyargs networkx
fi

cd $NX_SOURCE

section_end "script section"

set +e
