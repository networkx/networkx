#!/usr/bin/env bash
# Copyright (c) 2024, NVIDIA CORPORATION.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
