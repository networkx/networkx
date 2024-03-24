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
import os
import shutil
import glob

from _1_create_git_clone import ALL_PROJECTS

os.makedirs("trimmed-repos", exist_ok=True)
for path in sorted(glob.glob("repos*/*/")):
    name = path.split("/")[-2]
    if name in ALL_PROJECTS:
        continue
    dst_base = dst = f"trimmed-repos/{name}"
    i = 1
    while os.path.exists(dst):
        i += 1
        dst = f"{dst_base}{i}"
    print(f"mv {path} {dst}")
    shutil.move(path, dst)
