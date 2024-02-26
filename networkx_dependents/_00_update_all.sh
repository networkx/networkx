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
echo
echo =======================
echo = _0_initial_setup.sh =
echo =======================
echo
./_0_initial_setup.sh
echo
echo ====================
echo = _8_trim_repos.py =
echo ====================
echo
./_8_trim_repos.py
echo
echo ==================
echo = _7_git_pull.sh =
echo ==================
echo
./_7_git_pull.sh
echo
echo ==========================
echo = _1_create_git_clone.py =
echo ==========================
echo
./_1_create_git_clone.py
echo
echo ==============================
echo = _2_git_clone-transitive.sh =
echo ==============================
echo
./_2_git_clone-transitive.sh
echo
echo ===================
echo = _2_git_clone.sh =
echo ===================
echo
./_2_git_clone.sh
echo
echo ========================
echo = _3_get_conda_info.py =
echo ========================
echo
./_3_get_conda_info.py
echo
echo =========================
echo = _4_get_github_info.sh =
echo =========================
echo
./_4_get_github_info.sh
echo
echo ======================
echo = _5_get_nx_usage.sh =
echo ======================
echo
./_5_get_nx_usage.sh
echo
echo ============================
echo = _6_get_pypi_downloads.py =
echo ============================
echo
./_6_get_pypi_downloads.py
