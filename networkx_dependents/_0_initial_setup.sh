#!/usr/bin/env bash
set -e
if [ ! -d cf-scripts ]; then
    git clone --depth 1 https://github.com/regro/cf-scripts.git
else
    pushd cf-scripts
    git pull
    popd
fi
if [ ! -d cf-graph-countyfair ]; then
    git clone --depth 1 https://github.com/regro/cf-graph-countyfair.git
else
    pushd cf-graph-countyfair
    git pull
    popd
fi
if ! [[ $(conda env list | grep '/cf-scripts$') ]]; then
    pushd cf-scripts
    conda env create -f environment.yml
    conda install -n cf-scripts -y pypistats gh ipython black
    conda run -n cf-scripts pip install -e . --no-deps
    popd
else
    echo cf-scripts environment already exists
fi
echo
echo You may now activate cf-scripts conda environment:
echo
echo "    $" conda activate cf-scripts
echo
