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
import json
import os
import subprocess
from pathlib import Path

import networkx as nx
from conda_forge_tick.utils import load_graph, LazyJson

# Additional repos not on conda-forge (tutorials, classes, etc.)
extra_urls = {
    "Network-Analysis-Made-Simple": "https://github.com/ericmjl/Network-Analysis-Made-Simple",
    "FirstCourseNetworkScience": "https://github.com/CambridgeUniversityPress/FirstCourseNetworkScience",
    "networks-science-course": "https://github.com/chatox/networks-science-course",
    "Applied-Data-Science-with-Python-Specialization": "https://github.com/yonycherkos/Applied-Data-Science-with-Python-Specialization",
    "graphml-class": "https://github.com/Graphlet-AI/graphml-class",
    "Graph-Analysis-with-NetworkX": "https://github.com/KangboLu/Graph-Analysis-with-NetworkX",
    "Network-Science-with-Python": "https://github.com/PacktPublishing/Network-Science-with-Python",
    "GML2023": "https://github.com/xbresson/GML2023",
}

# Not sure how/if/whether these use networkx (TBD, skip for now)
with Path("SKIP").open() as f:
    SKIP = {x.strip() for x in f.readlines()}
# Very limited networkx usage (TBD, skip for now)
with Path("MAYBE_SKIP").open() as f:
    MAYBE_SKIP = {x.strip() for x in f.readlines()}

os.chdir("cf-graph-countyfair")
with open("graph.json") as f:
    nx_deps = sorted(d["target"] for d in json.load(f)["links"] if d["source"] == "networkx")

G = load_graph()
nx_deps2 = sorted(G.succ["networkx"])
assert nx_deps == nx_deps2
nx_deps_transitive = sorted(nx.descendants(G, "networkx") - set(nx_deps))


def unlazy(d):
    return {k: unlazy(v) if isinstance(v, (dict, LazyJson)) else v for k, v in d.items()}


# Manual fixes
G.nodes["alphashape"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/bellockk/alphashape"
G.nodes["dagster-libs"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/dagster-io/dagster"
G.nodes["pomegranate"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/jmschrei/pomegranate"
G.nodes["sceptre"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/Sceptre/sceptre"
G.nodes["ties20"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/UCL-CCS/TIES"
G.nodes["ties20"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/UCL-CCS/TIES"
G.nodes["awssert"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/TSNobleSoftware/awssert"
G.nodes["de-forcefields"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/jthorton/de-forcefields"
G.nodes["dftd3-python"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/dftd3/simple-dftd3"
G.nodes["dynophores"]["payload"] = unlazy(G.nodes["dynophores"]["payload"])
G.nodes["dynophores"]["payload"]["url"] = "https://github.com/wolberlab/dynophores"
G.nodes["earth2observe"]["payload"] = unlazy(G.nodes["earth2observe"]["payload"])
G.nodes["earth2observe"]["payload"]["meta_yaml"]["about"]["dev_url" ] = "https://github.com/Serapieum-of-alex/earth2observe"
G.nodes["earth2observe"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/Serapieum-of-alex/earth2observe"
G.nodes["earth2observe"]["payload"]["url"] = "https://github.com/Serapieum-of-alex/earth2observe"
G.nodes["functorch"]["payload"] = unlazy(G.nodes["functorch"]["payload"])
G.nodes["functorch"]["payload"]["url"] = "https://github.com/pytorch/functorch"
G.nodes["geowombat"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/jgrss/geowombat"
G.nodes["jobtastic"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/PolicyStat/jobtastic"
G.nodes["libefp"]["payload"] = unlazy(G.nodes["libefp"]["payload"])
G.nodes["libefp"]["payload"]["url"] = "https://github.com/libefp2/libefp"
G.nodes["libefp"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/libefp2/libefp"
G.nodes["lsds"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/funkelab/lsd"
G.nodes["pandera"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/unionai-oss/pandera"
G.nodes["puma"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/nasa/puma"
G.nodes["pyiron_dft"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/pyiron/pyiron_dft"
G.nodes["pyiron_example_job"]["payload"]["meta_yaml"]["about"][
    "dev_url"
] = "https://github.com/pyiron/pyiron_example_job"
G.nodes["pyiron_vasp"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/pyiron/pyiron_vasp"
G.nodes["pytorch-dp"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/pytorch/opacus"
G.nodes["pytorch-dp"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/pytorch/opacus"
G.nodes["recorder-napari"]["payload"]["meta_yaml"]["about"]["home"] = "https://pypi.org/project/recorder-napari"
G.nodes["sisppeo"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/inrae/SISPPEO"
G.nodes["tesspy"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/siavash-saki/tesspy"
G.nodes["thalassa"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/ec-jrc/thalassa"
G.nodes["torch_em"]["payload"] = unlazy(G.nodes["torch_em"]["payload"])
G.nodes["torch_em"]["payload"]["url"] = "https://github.com/constantinpape/torch-em"
G.nodes["vector-quantize-pytorch"]["payload"]["meta_yaml"]["about"]["dev_url"] = "https://github.com/lucidrains/vector-quantize-pytorch"
G.nodes["vector-quantize-pytorch"]["payload"]["meta_yaml"]["about"]["home"] = "https://github.com/lucidrains/vector-quantize-pytorch"

manual_urls = {
    "asimov": "https://git.ligo.org/asimov/asimov",
    "curviriver": "https://github.com/cheginit/curviriver",
    "elyra-server": "https://github.com/elyra-ai/elyra",
    "finesse": "https://git.ligo.org/finesse/finesse3",
    "geograph": "https://github.com/ai4er-cdt/geograph",
    "guardian": "https://git.ligo.org/cds/software/guardian",
    "ligo-asimov": "https://git.ligo.org/asimov/asimov",
    "ligo.skymap": "https://github.com/lpsinger/ligo.skymap",
    "manim": "https://github.com/ManimCommunity/manim",
    "nitime": "https://github.com/nipy/nitime",
    "nomad-camels": "https://github.com/FAU-LAP/NOMAD-CAMELS",
    "pandapower": "https://github.com/e2nIEE/pandapower",
    "polytope": "https://github.com/tulip-control/polytope",
    "pydiverse-pipedag": "https://github.com/pydiverse/pydiverse.pipedag",
    "pyg4ometry": "https://bitbucket.org/jairhul/pyg4ometry",
    "pymatgen": "https://github.com/materialsproject/pymatgen",
    "pyomo.extras": "https://github.com/Pyomo/pyomo",
    "pyscal-rdf": "https://github.com/pyscal/pyscal_rdf",
    "pytorch-cpu": "https://github.com/pytorch/pytorch",
    "scikit-image": "https://github.com/scikit-image/scikit-image",
    "solaris": "https://github.com/CosmiQ/solaris",
    "zipline-reloaded": "https://github.com/stefan-jansen/zipline-reloaded",
}
force_urls = {
    "atom-ml": "https://github.com/tvdboom/ATOM",
    "bfee2": "https://github.com/fhh2626/BFEE2",
    "compas_robots": "https://github.com/compas-dev/compas_robots",
    "dalex": "https://github.com/ModelOriented/DALEX",
    "dftd4-python": "https://github.com/dftd4/dftd4",
    "flytekitplugins-modin": "https://github.com/flyteorg/flytekit",
    "flytekitplugins-pandera": "https://github.com/flyteorg/flytekit",
    "kuti": "https://github.com/subpic/ku",
    "monotonicnetworks": "https://github.com/niklasnolte/MonotoneNorm",
    "neuralforecast": "https://github.com/Nixtla/neuralforecast",
    "oneat": "https://github.com/Kapoorlabs-CAPED/caped-ai-oneat",
    "openlineage-airflow": "https://github.com/OpenLineage/OpenLineage",
    "pennylane-qchem": "https://github.com/PennyLaneAI/pennylane",
    "primod": "https://github.com/Deltares/imod_coupler",
    "pygraft": "https://github.com/nicolas-hbt/pygraft",
    "pyiron": "https://github.com/pyiron/pyiron",
    "pyiron_dft": "https://github.com/pyiron/pyiron-dft-uncertainty",
    "pymatgen-diffusion": "https://github.com/materialsvirtuallab/pymatgen-analysis-diffusion",
    "pysal": "https://github.com/pysal/pysal",
    "ribasim": "https://github.com/Deltares/Ribasim",
    "stellarphot": "https://github.com/feder-observatory/stellarphot",
    "torchkin": "https://github.com/facebookresearch/theseus",
    "torchlie": "https://github.com/facebookresearch/theseus",
}
for name in [
    "dagster", "dagster_aws", "dagster_bash", "dagster_cron", "dagster_dask", "dagster_datadog",
    "dagster_dbt", "dagster_gcp", "dagster_graphql", "dagster_pagerduty", "dagster_papertrail",
    "dagster_postgres", "dagster_pyspark", "dagster_slack", "dagster_snowflake", "dagster_spark",
    "dagster_ssh", "dagster_twilio",
]:
    force_urls[name] = "https://github.com/dagster-io/dagster"
for name in [
    "llama-index-core", "llama-index-legacy", "llama-index-agent-openai",
    "llama-index-embeddings-openai", "llama-index-llms-openai", "llama-index-multi-modal-llms-openai",
    "llama-index-program-openai", "llama-index-question-gen-openai",
]:
    force_urls[name] = "https://github.com/run-llama/llama_index"


def get_urls(name, d):
    dev_url = d.get("meta_yaml", {}).get("about", {}).get("dev_url", "") or ""
    home = d.get("meta_yaml", {}).get("about", {}).get("home", "") or ""
    url = d.get("url", "") or ""
    if "/archive/" in url:
        url = url[: url.rindex("/archive/")]
    if "/releases/" in url:
        url = url[: url.rindex("/releases/")]
    dev_url = dev_url.rstrip("/").replace("http://", "https://").replace("https://www.github.", "https://github.")
    home = home.rstrip("/").replace("http://", "https://").replace("https://www.github.", "https://github.")
    url = url.rstrip("/").replace("http://", "https://").replace("https://www.github.", "https://github.")
    if dev_url.endswith(".git"):
        dev_url = dev_url[:-4]
    if home.endswith(".git"):
        home = dev_url[:-4]
    if url.endswith(".git"):
        url = dev_url[:-4]
    if dev_url.endswith("/-"):
        dev_url = dev_url[:-2]
    if home.endswith("/-"):
        home = dev_url[:-2]
    if url.endswith("/-"):
        url = dev_url[:-2]
    return [dev_url, home, url]


def get_github_url(name, d):
    dev_url, home, url = get_urls(name, d)
    if "github.com" not in dev_url and "https://gitlab." not in dev_url:
        dev_url = ""
    if "github.com" not in home and "https://gitlab." not in home:
        home = ""
    if "github.com" not in url and "https://gitlab." not in url:
        url = ""
    assert not dev_url or dev_url.startswith("https://github.com/") or dev_url.startswith("https://gitlab."), (
        name, dev_url, home, url)
    assert not home or home.startswith("https://github.com/") or home.startswith("https://gitlab."), (
        name, dev_url, home, url)
    assert not url or url.startswith("https://github.com/") or url.startswith("https://gitlab."), (
        name, dev_url, home, url)
    if dev_url:
        assert not home or dev_url.lower().startswith(home.lower()), (name, dev_url, home, url)
        assert not url or dev_url.lower().startswith(url.lower()), (name, dev_url, home, url)
    if home:
        assert not url or home.lower().startswith(url.lower()), (name, dev_url, home, url)
    return dev_url or home or url


repo_urls = {name: get_github_url(name, G.nodes[name]["payload"]) for name in nx_deps + nx_deps_transitive}
for k, v in manual_urls.items():
    if k in repo_urls and not repo_urls[k]:
        repo_urls[k] = v
for k, v in force_urls.items():
    if k in repo_urls:
        repo_urls[k] = v

with open("mappings/pypi/name_mapping.json") as f:
    name_mappings = json.load(f)
conda_to_pypi = {info["conda_name"]: info["pypi_name"] for info in name_mappings}
conda_to_pypi = {dep: conda_to_pypi.get(dep) for dep in nx_deps + nx_deps_transitive}

conda_to_pypi2 = {}
for name in repo_urls:
    urls = get_urls(name, G.nodes[name]["payload"])
    urls = {url for url in urls if "pypi." in url.lower()}
    names = set()
    for url in urls:
        if url.lower().startswith("https://pypi.io/packages/source/") or url.lower().startswith(
            "https://pypi.org/packages/source/"
        ):
            names.add(url.split("/")[6])
        elif url.lower().startswith("https://pypi.io/project/") or url.lower().startswith("https://pypi.org/project/"):
            names.add(url.split("/")[4])
        else:
            raise ValueError(f"{name}: {url}")
    if names:
        if len(names) > 1:
            names2 = {x.lower().replace("_", "-") for x in names}
            if len(names2) > 1:
                # print(urls)
                raise ValueError(f"{name}: {names}")
            names = names2
        [conda_to_pypi2[name]] = names


for k, v in conda_to_pypi2.items():
    if conda_to_pypi[k] is None:
        conda_to_pypi[k] = v

for k, v in extra_urls.items():
    if k not in repo_urls:
        repo_urls[k] = v
        conda_to_pypi[k] = None

LICENSE = """
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

def write_file(repo_urls, suffix="", reverse=False):
    with open(f"_2_git_clone{suffix}.sh", "w") as f:
        f.write("#!/usr/bin/env bash")
        f.write(LICENSE)
        f.write("#\n# THIS FILE IS AUTOMATICALLY GENERATED BY _1_create_git_clone.py\n")
        f.write(f"mkdir -p repos{suffix}\n")
        for k in sorted(repo_urls, reverse=reverse):
            v = repo_urls[k]
            f.write(f"if [ ! -d repos{suffix}/{k} ]; then git clone --depth 1 {v}.git repos{suffix}/{k} ; fi\n")
            if conda_to_pypi[k]:
                f.write(f"echo {conda_to_pypi[k]} > repos{suffix}/{k}/_pypi_name\n")
            f.write(f"echo {k} > repos{suffix}/{k}/_conda_forge_name\n")
    subprocess.run(["chmod", "+x", f"_2_git_clone{suffix}.sh"])


ALL_PROJECTS = set(nx_deps) | set(extra_urls) | set(nx_deps_transitive)
UNSKIPPED_PROJECTS = ALL_PROJECTS - SKIP - MAYBE_SKIP
os.chdir("..")
if __name__ == "__main__":
    s = set(nx_deps) | set(extra_urls)
    write_file({k: v for k, v in repo_urls.items() if v and k in s and k not in SKIP and k not in MAYBE_SKIP})
    write_file({k: v for k, v in repo_urls.items() if v and k in s and (k in SKIP or k in MAYBE_SKIP)}, suffix="-skip")
    s = set(nx_deps_transitive)
    write_file(
        {k: v for k, v in repo_urls.items() if v and k in s and k not in SKIP and k not in MAYBE_SKIP},
        suffix="-transitive",
    )
    write_file(
        {k: v for k, v in repo_urls.items() if v and k in s and (k in SKIP or k in MAYBE_SKIP)},
        suffix="-transitive-skip",
    )

    # TODO: if we have no repository, we could still download and use the build artifact
    no_repo = sorted(k for k, v in repo_urls.items() if not v)
    print("No repository found for:")
    print("   ", "\n    ".join(no_repo))
    no_pypi = sorted(k for k, v in conda_to_pypi.items() if not v)
    print("No PyPI name found for:")
    print("   ", "\n    ".join(no_pypi))
