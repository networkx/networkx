"""
Setup script for networkx

You can install networkx with

python setup.py install
"""
from glob import glob
import os
import sys

if os.path.exists("MANIFEST"):
    os.remove("MANIFEST")

from setuptools import setup

if sys.argv[-1] == "setup.py":
    print("To install, run 'python setup.py install'")
    print()

# Write the version information.
sys.path.insert(0, "networkx")
import release

version = release.write_versionfile()
sys.path.pop(0)


docdirbase = "share/doc/networkx-%s" % version
# add basic documentation
data = [(docdirbase, glob("*.txt"))]
# add examples
for d in [
    ".",
    "advanced",
    "algorithms",
    "basic",
    "3d_drawing",
    "drawing",
    "graph",
    "javascript",
    "jit",
    "pygraphviz",
    "subclass",
]:
    dd = os.path.join(docdirbase, "examples", d)
    pp = os.path.join("examples", d)
    data.append((dd, glob(os.path.join(pp, "*.txt"))))
    data.append((dd, glob(os.path.join(pp, "*.py"))))
    data.append((dd, glob(os.path.join(pp, "*.bz2"))))
    data.append((dd, glob(os.path.join(pp, "*.gz"))))
    data.append((dd, glob(os.path.join(pp, "*.mbox"))))
    data.append((dd, glob(os.path.join(pp, "*.edgelist"))))
# add js force examples
dd = os.path.join(docdirbase, "examples", "javascript/force")
pp = os.path.join("examples", "javascript/force")
data.append((dd, glob(os.path.join(pp, "*"))))


if __name__ == "__main__":

    setup(
        data_files=data
    )
