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
import glob
import json
import os
import yaml

from conda_forge_tick.utils import load_graph, LazyJson

os.chdir("cf-graph-countyfair")
with open("graph.json") as f:
    nx_deps = sorted(d["target"] for d in json.load(f)["links"] if d["source"] == "networkx")

G = load_graph()
nx_deps2 = sorted(G.succ["networkx"])
assert nx_deps == nx_deps2
os.chdir("..")


def unlazy(d):
    return {k: unlazy(v) if isinstance(v, (dict, LazyJson)) else v for k, v in d.items()}


for path in sorted(glob.glob("repos*/*/")):
    name = path.split("/")[-2]
    if name not in G:
        print("SKIPPING:", name)
        continue
    info = G.nodes[name]["payload"]
    print(name)
    with open(f"{path}_conda_meta.yaml", "w") as f:
        yaml.dump(unlazy(info), f)
