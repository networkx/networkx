#!/usr/bin/env python
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
"""Create table_algorithms_cugraph.csv and table_repos_cugraph.csv"""
import glob
import json
import os
import networkx as nx
from collections import defaultdict

all_nx_funcs = {func.orig_func.__name__ for func in nx.utils.backends._registered_algorithms.values()}
package_pypi_downloads = {}
package_nx_funcs = {}
package_github_stars = {}
package_github_info = {}
repo_to_package = defaultdict(set)
skip = set()
for path in sorted(glob.glob("repos/*/") + glob.glob("repos-transitive/*/")):
    package = path.split("/")[-2]
    # PyPI downloads
    if not os.path.exists(f"{path}_pypi_downloads.json"):
        # print('No PyPI download info:', package)
        downloads = 0
    else:
        with open(f"{path}_pypi_downloads.json") as f:
            downloads = json.load(f)
        downloads = int(downloads["total"])
    package_pypi_downloads[package] = downloads

    # NetworkX usage
    with open(f"{path}_nx2") as f:
        lines = f.readlines()
    funcs = [line.strip().split(" ")[-1] for line in lines]
    package_nx_funcs[package] = set(funcs) & all_nx_funcs
    if not package_nx_funcs[package]:
        # print(package)
        skip.add(package)
        del package_nx_funcs[package]
        del package_pypi_downloads[package]
        continue

    # GitHub stars
    if not os.path.exists(f"{path}_repo_info.json"):
        package_github_stars[package] = 0
        # print('No repo info:', package)
    else:
        with open(f"{path}_repo_info.json") as f:
            repo_info = json.load(f)
        package_github_stars[package] = int(repo_info["stargazers_count"])
        package_github_info[package] = repo_info
        repo_to_package[repo_info["html_url"]].add(package)

repo_to_package = dict(repo_to_package)
for packages in repo_to_package.values():
    # Divide github stars by the number of packages that share a github repo.
    # This isn't perfect, but it helps some things from being exaggerated.
    denom = len(packages)
    if denom <= 1:
        continue
    for package in packages:
        package_github_stars[package] /= denom

rank_by_pypi_downloads = {
    v: k
    for k, v in enumerate(
        sorted(package_pypi_downloads, key=lambda x: (package_pypi_downloads[x], package_github_stars[x], x)),
        1,
    )
}
rank_by_github_stars = {
    v: k
    for k, v in enumerate(
        sorted(package_github_stars, key=lambda x: (package_github_stars[x], package_pypi_downloads[x], x)),
        1,
    )
}
rank_by_score = {
    v: k
    for k, v in enumerate(
        sorted(
            rank_by_pypi_downloads,
            key=lambda x: (rank_by_pypi_downloads[x] + rank_by_github_stars[x], rank_by_pypi_downloads[x], x),
        ),
        1,
    )
}

func_downloads = defaultdict(int)
func_stars = defaultdict(int)
func_scores = defaultdict(int)
for package, functions in package_nx_funcs.items():
    downloads = package_pypi_downloads[package]
    stars = package_github_stars[package]
    downloads_rank = rank_by_pypi_downloads.get(package, 0)
    stars_rank = rank_by_github_stars.get(package, 0)
    score = downloads_rank + stars_rank
    for func in functions:
        func_downloads[func] += downloads
        func_stars[func] += stars
        func_scores[func] += score
func_downloads = dict(func_downloads)
func_stars = dict(func_stars)
func_scores = dict(func_scores)

func_ranks = {
    v: k
    for k, v in enumerate(sorted(func_scores, key=lambda x: (func_scores[x], func_downloads[x], func_stars[x], x)), 1)
}

import _nx_cugraph

implemented = set(_nx_cugraph.get_info()["functions"])
sorted_funcs = sorted(func_ranks, key=lambda x: -func_ranks[x])
lines = [["package"] + sorted_funcs]
for package in sorted(rank_by_score, key=lambda x: -rank_by_score[x]):
    line = [package]
    for func in sorted_funcs:
        if func not in package_nx_funcs[package]:
            line.append("")
        elif func in implemented:
            line.append("Y")
        else:
            line.append("N")
    lines.append(line)

with open("table_algorithms_cugraph.csv", "w") as f:
    # Transpose
    for line in list(zip(*lines)):
        f.write(",".join(line))
        f.write("\n")

lines = [
    (
        "package,num_implemented,num_funcs,pypi_downloads,stars,forks,subscribers,"
        "created_at,updated_at,url,homepage,description,topics,nx_funcs"
    ).split(",")
]
for package in sorted(rank_by_score, key=lambda x: -rank_by_score[x]):
    funcs = package_nx_funcs[package]
    line = [package]
    line.append(str(len(funcs & implemented)))
    line.append(str(len(funcs)))
    info = package_github_info.get(package)
    line.append(str(package_pypi_downloads[package]))
    if info:
        line.append(str(info["stargazers_count"]))
        line.append(str(info["forks_count"]))
        line.append(str(info["subscribers_count"]))
        line.append(info["created_at"].split("T")[0])
        line.append(info["updated_at"].split("T")[0])
        line.append(info["html_url"] or "")
        line.append(info["homepage"] or "")
        desc = info["description"]
        if desc:
            desc = '"' + desc.replace('"', '""') + '"'
        line.append(desc or "")
        line.append(" ".join(info["topics"]))
    else:
        if os.path.exists(f"repos/{package}/.git/config"):
            with open(f"repos/{package}/.git/config") as f:
                git_config = f.readlines()
        else:
            with open(f"repos-transitive/{package}/.git/config") as f:
                git_config = f.readlines()
        url_lines = [x for x in git_config if "url =" in x]
        assert len(url_lines) == 1
        url = url_lines[0].split("=")[-1].strip()
        assert url.endswith(".git")
        url = url[:-4]
        line.append("")
        line.append("")
        line.append("")
        line.append("")
        line.append("")
        line.append(url)
        line.append("")
        line.append("")
        line.append("")
    line.append(" ".join(sorted(funcs)))
    lines.append(line)

with open("table_repos_cugraph.csv", "w") as f:
    for line in lines:
        f.write(",".join(line))
        f.write("\n")
