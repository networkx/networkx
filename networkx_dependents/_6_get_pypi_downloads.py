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
"""
This skips repos that already have `_pypi_downloads.json`, because pypistats API
may be rate-limited. To update, simply remove all `_pypi_downloads.json` files first:

$ ./_X_remove_pypi_downloads.sh

"""
import glob
import json
import os
import random
import time

import pypistats

for path in sorted(glob.glob("repos*/*/")):
    if os.path.exists(f"{path}_pypi_downloads.json"):
        continue
    # Sleep to be nice to the API
    time.sleep(0.4 + 0.4 * random.random())
    conda_name = path.split("/")[-2]
    if known_pypi_name := os.path.exists(f"{path}_pypi_name"):
        with open(f"{path}_pypi_name") as f:
            pypi_name = f.read().strip()
    else:
        # Guess that it's the same as the conda-forge name
        pypi_name = conda_name
    try:
        d = json.loads(pypistats.overall(pypi_name, mirrors=False, format="json", total="monthly"))
    except Exception as exc:
        if not known_pypi_name and "404 Not Found" in str(exc):
            print(f"{conda_name}: SKIPPED!")
            continue
        raise
    print(conda_name)
    d["total"] = sum(v["downloads"] for v in d["data"])
    with open(f"{path}_pypi_downloads.json", "w") as f:
        json.dump(d, f, indent=2, sort_keys=True)
