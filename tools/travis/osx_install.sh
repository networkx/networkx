#!/usr/bin/env bash
set -ex

# set up Miniconda on OSX
if [[ "${OSX_PKG_ENV}" == miniconda ]]; then
    wget https://repo.continuum.io/miniconda/Miniconda3-4.3.21-MacOSX-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    hash -r
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    # Useful for debugging any issues with conda
    conda info -a

    conda create -q -n testenv python=$TRAVIS_PYTHON_VERSION decorator
    source activate testenv
else
    # set up Python and virtualenv on OSX
    git clone https://github.com/matthew-brett/multibuild
    source multibuild/osx_utils.sh
    get_macpython_environment $TRAVIS_PYTHON_VERSION venv
fi

if [[ "${OPTIONAL_DEPS}" == 1 ]]; then
    if [[ "${OSX_PKG_ENV}" == miniconda ]]; then
        conda install graphviz=2.38
        export PKG_CONFIG_PATH=/Users/travis/miniconda/envs/testenv/lib/pkgconfig
    else
        brew install graphviz
    fi
    dot -V
    sed -i "" 's/^gdal.*/gdal==1.11.2/' requirements/extras.txt
fi

set +ex
