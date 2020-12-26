"""Release data for NetworkX.

When NetworkX is imported a number of steps are followed to determine
the version information.

   1) If the release is not a development release (dev=False), then version
      information is read from version.py, a file containing statically
      defined version information.  This file should exist on every
      downloadable release of NetworkX since setup.py creates it during
      packaging/installation.

   2) If the release is a development release, then version information
      is read dynamically, when possible.  If no dynamic information can be
      read, then an attempt is made to read the information from version.py.

Clarification:
      version.py is created only by setup.py

When setup.py creates version.py, it does so before packaging/installation.
So the created file is included in the source distribution.
"""

import os
import time
import datetime


def write_versionfile():
    """Creates a static file containing version information."""
    basedir = os.path.abspath(os.path.split(__file__)[0])
    versionfile = os.path.join(basedir, "version.py")

    text = '''"""
Version information for NetworkX, created during installation.

Do not add this file to the repository.
"""

version = %(version)r
date = %(date)r
'''

    # Try to update all information
    date, version = get_info()

    def writefile():
        fh = open(versionfile, "w")
        subs = {
            "version": version,
            "date": date,
        }
        fh.write(text % subs)
        fh.close()

    if os.path.isfile(versionfile):
        # This is *good*, and the most likely place users will be when
        # running setup.py. We do not want to overwrite version.py.
        # Grab the version so that setup can use it.
        from version import version

    else:
        # This is *bad*.  It means the user might have a tarball that
        # does not include version.py.  Let this error raise so we can
        # fix the tarball.
        # raise Exception('version.py not found!')

        # We no longer require that prepared tarballs include a version.py
        # So we use the possibly trunctated value from get_info()
        # Then we write a new file.
        writefile()

    return version


def get_info():
    # Date information
    date_info = datetime.datetime.utcfromtimestamp(
        int(os.environ.get("SOURCE_DATE_EPOCH", time.time()))
    )
    date = time.asctime(date_info.timetuple())

    version = None

    # This is where most final releases of NetworkX will be.
    # All info should come from version.py.
    try:
        from network import version as _version

        version = _version.version
        date = _version.date
        del _version
    except ImportError:
        #   we failed to determine static versioning info
        version = "".join([str(major), ".", str(minor)])
        if dev:
            version += ".dev_" + date_info.strftime("%Y%m%d%H%M%S")

    return date, version


# Version information
name = "networkx"
major = "2"
minor = "6rc1"


# Declare current release as a development release.
# Change to False before tagging a release; then change back.
dev = True


description = "Python package for creating and manipulating graphs and networks"
authors = {
    "Hagberg": ("Aric Hagberg", "hagberg@lanl.gov"),
    "Schult": ("Dan Schult", "dschult@colgate.edu"),
    "Swart": ("Pieter Swart", "swart@lanl.gov"),
}
maintainer = "NetworkX Developers"
maintainer_email = "networkx-discuss@googlegroups.com"
url = "https://networkx.org/"
project_urls = {
    "Bug Tracker": "https://github.com/networkx/networkx/issues",
    "Documentation": "https://networkx.org/documentation/stable/",
    "Source Code": "https://github.com/networkx/networkx",
}
platforms = ["Linux", "Mac OSX", "Windows", "Unix"]
keywords = [
    "Networks",
    "Graph Theory",
    "Mathematics",
    "network",
    "graph",
    "discrete mathematics",
    "math",
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Physics",
]

date, version = get_info()
