#!/usr/bin/env python
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
