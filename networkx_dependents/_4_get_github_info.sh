#!/usr/bin/env bash
# This uses the `gh` CLI; you may need to run `gh auth login` first
# Also, this skips if `_repo_info.json` already exists. To update data, first remove them:
# $ ./_X_remove_github_info.sh
for dir in repos*/*/
do
    pushd $dir
    if [[ -f _repo_info.json ]]; then
        popd
        continue
    fi
    echo $dir
    if ! gh api repos/{owner}/{repo} > _repo_info.json ; then
        rm _repo_info.json
        grep 'url =' .git/config
    fi
    popd
done
