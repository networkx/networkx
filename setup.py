#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for networkx

You can install networkx with

python setup.py install
"""
from glob import glob
import os
import sys
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

from setuptools import setup

if sys.argv[-1] == 'setup.py':
    print("To install, run 'python setup.py install'")
    print()

if sys.version_info[:2] < (3, 6):
    error = """NetworkX 2.5+ requires Python 3.6 or later (%d.%d detected).
             
For Python 2.7, please install version 2.2 using:

$ pip install 'networkx==2.2'
""" % sys.version_info[:2]
    sys.stderr.write(error + "\n")
    sys.exit(1)

# Write the version information.
sys.path.insert(0, 'networkx')
import release
version = release.write_versionfile()
sys.path.pop(0)

packages = ["networkx",
            "networkx.algorithms",
            "networkx.algorithms.assortativity",
            "networkx.algorithms.bipartite",
            "networkx.algorithms.node_classification",
            "networkx.algorithms.centrality",
            "networkx.algorithms.community",
            "networkx.algorithms.components",
            "networkx.algorithms.connectivity",
            "networkx.algorithms.coloring",
            "networkx.algorithms.flow",
            "networkx.algorithms.traversal",
            "networkx.algorithms.isomorphism",
            "networkx.algorithms.shortest_paths",
            "networkx.algorithms.link_analysis",
            "networkx.algorithms.operators",
            "networkx.algorithms.approximation",
            "networkx.algorithms.tree",
            "networkx.classes",
            "networkx.generators",
            "networkx.drawing",
            "networkx.linalg",
            "networkx.readwrite",
            "networkx.readwrite.json_graph",
            "networkx.tests",
            "networkx.testing",
            "networkx.utils"]

docdirbase = 'share/doc/networkx-%s' % version
# add basic documentation
data = [(docdirbase, glob("*.txt"))]
# add examples
for d in ['.',
          'advanced',
          'algorithms',
          'basic',
          '3d_drawing',
          'drawing',
          'graph',
          'javascript',
          'jit',
          'pygraphviz',
          'subclass']:
    dd = os.path.join(docdirbase, 'examples', d)
    pp = os.path.join('examples', d)
    data.append((dd, glob(os.path.join(pp, "*.txt"))))
    data.append((dd, glob(os.path.join(pp, "*.py"))))
    data.append((dd, glob(os.path.join(pp, "*.bz2"))))
    data.append((dd, glob(os.path.join(pp, "*.gz"))))
    data.append((dd, glob(os.path.join(pp, "*.mbox"))))
    data.append((dd, glob(os.path.join(pp, "*.edgelist"))))
# add js force examples
dd = os.path.join(docdirbase, 'examples', 'javascript/force')
pp = os.path.join('examples', 'javascript/force')
data.append((dd, glob(os.path.join(pp, "*"))))

# add the tests
package_data = {
    'networkx': ['tests/*.py'],
    'networkx.algorithms': ['tests/*.py'],
    'networkx.algorithms.assortativity': ['tests/*.py'],
    'networkx.algorithms.bipartite': ['tests/*.py'],
    'networkx.algorithms.node_classification': ['tests/*.py'],
    'networkx.algorithms.centrality': ['tests/*.py'],
    'networkx.algorithms.community': ['tests/*.py'],
    'networkx.algorithms.components': ['tests/*.py'],
    'networkx.algorithms.connectivity': ['tests/*.py'],
    'networkx.algorithms.coloring': ['tests/*.py'],
    'networkx.algorithms.flow': ['tests/*.py', 'tests/*.bz2'],
    'networkx.algorithms.isomorphism': ['tests/*.py', 'tests/*.*99'],
    'networkx.algorithms.link_analysis': ['tests/*.py'],
    'networkx.algorithms.approximation': ['tests/*.py'],
    'networkx.algorithms.operators': ['tests/*.py'],
    'networkx.algorithms.shortest_paths': ['tests/*.py'],
    'networkx.algorithms.traversal': ['tests/*.py'],
    'networkx.algorithms.tree': ['tests/*.py'],
    'networkx.classes': ['tests/*.py'],
    'networkx.generators': ['tests/*.py', 'atlas.dat.gz'],
    'networkx.drawing': ['tests/*.py'],
    'networkx.linalg': ['tests/*.py'],
    'networkx.readwrite': ['tests/*.py'],
    'networkx.readwrite.json_graph': ['tests/*.py'],
    'networkx.testing': ['tests/*.py'],
    'networkx.utils': ['tests/*.py']
}

install_requires = ['decorator>=4.3.0']
extras_require = {'all': ['numpy', 'scipy', 'pandas', 'matplotlib',
                          'pygraphviz', 'pydot', 'pyyaml', 'gdal', 'lxml',
                          'pytest'],
                  'gdal': ['gdal'],
                  'lxml': ['lxml'],
                  'matplotlib': ['matplotlib'],
                  'pytest': ['pytest'],
                  'numpy': ['numpy'],
                  'pandas': ['pandas'],
                  'pydot': ['pydot'],
                  'pygraphviz': ['pygraphviz'],
                  'pyyaml': ['pyyaml'],
                  'scipy': ['scipy']
                 }

with open("README.rst", "r") as fh:
    long_description = fh.read()

if __name__ == "__main__":

    setup(
        name=release.name.lower(),
        version=version,
        maintainer=release.maintainer,
        maintainer_email=release.maintainer_email,
        author=release.authors['Hagberg'][0],
        author_email=release.authors['Hagberg'][1],
        description=release.description,
        keywords=release.keywords,
        long_description=long_description,
        license=release.license,
        platforms=release.platforms,
        url=release.url,
        project_urls=release.project_urls,
        classifiers=release.classifiers,
        packages=packages,
        data_files=data,
        package_data=package_data,
        install_requires=install_requires,
        extras_require=extras_require,
        python_requires='>=3.6',
        zip_safe=False
    )
