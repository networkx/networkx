This folder contains scripts to help analyze packages that depend on NetworkX.
It uses dependency information from conda-forge.

- `_0_initial_setup.sh`: download conda forge tools and graph repos, and create conda environment
  - Don't forget to activate your environment: `conda activate cf-scripts`
  - Run this script again to update the conda-forge graph
- `_00_update_all.sh`: run all the scripts (`cf-scripts` environment must be active!)
- `_1_create_git_clone.py`: create `_2_git_clone*.sh` based on conda-forge dependency graph
- `_2_git_clone.sh`: `git clone` repositories to `repos/` and write `_pypi_name` to repo if known
- `_2_git_clone-skip.sh`: `git clone` repositories that we skip for now to `repos-skip/`
- `_2_git_clone-transitive.sh`: `git clone` transitive deps to `repos-transitive/`
- `_2_git_clone-transitive-skip.sh`: `git clone` transitive deps that we skip to `repos-transitive-skip/`
- `_3_get_conda_info.py`: write `_conda_meta.yaml` from conda-forge graph to repositories in `repos*/`
- `_4_get_github_info.sh`: use `gh` CLI to download github info to `_repo_info.json`
- `_5_get_nx_usage.sh`: scrape NetworkX usage from repos using `grep` (create `_nx*` files)
- `_6_get_pypi_downloads.py`: use `pypistats` to save PyPI download info to `_pypi_downloads.json`
- `_7_git_pull.sh`: update repositories (with `git pull`) in `repos*/`
- `_8_trim_repos.py`: move repos that are no longer in conda-forge graph to `trimmed-repos/`
