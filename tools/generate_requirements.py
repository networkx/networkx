#!/usr/bin/env python
"""Generate requirements/*.txt files from pyproject.toml."""

import sys
from pathlib import Path
from typing import list


try:  # standard module since Python 3.11
    import tomllib as toml
except ImportError:
    try:  # available for older Python via pip
        import tomli as toml
    except ImportError:
        sys.exit("Please install `tomli` first: `pip install tomli`")

script_pth = Path(__file__)
repo_dir = script_pth.parent.parent
script_relpth = script_pth.relative_to(repo_dir)
header = [
    f"# Generated via {script_relpth.as_posix()} and pre-commit hook.",
    "# Do not edit this file; modify pyproject.toml instead.",
]


def generate_requirement_file(name: str, req_list: list) -> None:
    req_fname = repo_dir / "requirements" / f"{name}.txt"
    req_fname.write_text("\n".join(header + req_list) + "\n")


def main() -> None:
    pyproject = toml.loads((repo_dir / "pyproject.toml").read_text())

    generate_requirement_file("default", pyproject["project"]["dependencies"])

    for key, opt_list in pyproject["project"]["optional-dependencies"].items():
        generate_requirement_file(key, opt_list)


if __name__ == "__main__":
    main()
