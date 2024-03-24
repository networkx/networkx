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

# This uses the `gh` CLI; you may need to run `gh auth login` first
# Also, this skips if `_repo_info.json` already exists. To update data, first remove them:
# $ ./_X_remove_github_info.sh
for dir in repos*/*/
do
    if ! [[ -f _repo_info.json ]]; then
        continue
    fi
    pushd $dir
    echo $dir
    if ! gh api repos/{owner}/{repo} > _repo_info.json ; then
        rm _repo_info.json
        grep 'url =' .git/config
    fi
    popd
done
