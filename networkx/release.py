"""Release data for NetworkX."""

#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.


import os
import re


def write_versionfile():
    """Creates a file containing version information."""
    base = os.path.split(__file__)[0]
    versionfile = os.path.join(base, 'version.py')
    if revision is None and os.path.isfile(versionfile):
        # Unable to get revision info, so probably not in an SVN directory
        # If a version.py already exists, let's not overwrite it.
        # Useful mostly for nightly tarballs.
        return
    fh = open(versionfile, 'w')
    text = '''"""
Version information for NetworkX, created during installation.

Do not add this file to the repository.

"""

__version__ = '%(version)s'
__revision__ = %(revision)s
__date__ = '%(date)s'

'''
    if revision is not None:
        rev = "'%s'" % (revision,)
    else:
        rev = revision
    subs = {'version': version,
            'revision': rev,
            'date': date}
    fh.write(text % subs)
    fh.close()

def get_svn_revision():
    rev = None
    base = os.path.split(__file__)[0]
    entries_path = os.path.join(base, '.svn', 'entries')
    if os.path.isfile(entries_path):
        entries = open(entries_path, 'r').read()
        # Versions >= 7 of the entries file are flat text.  The first line is
        # the version number. The next set of digits after 'dir' is the revision.
        if re.match('(\d+)', entries):
            rev_match = re.search('\d+\s+dir\s+(\d+)', entries)
            if rev_match:
                rev = rev_match.groups()[0]
    if rev:
        return rev
    else:
        return None


name = 'networkx'
version = '1.1'

# Declare current release as a development release.
# Change to False before tagging a release; then change back.
dev = False

revision = None
if dev:
    version += '.dev'   
    revision = get_svn_revision()
    if revision is not None:
        version += "%s" % revision

description = "Python package for creating and manipulating graphs and networks"

long_description = \
"""
NetworkX is a Python package for the creation, manipulation, and
study of the structure, dynamics, and functions of complex networks.  

"""
license = 'BSD'
authors = {'Hagberg' : ('Aric Hagberg','hagberg@lanl.gov'),
           'Schult' : ('Dan Schult','dschult@colgate.edu'),
           'Swart' : ('Pieter Swart','swart@lanl.gov')
           }
maintainer = "NetworkX Developers",
maintainer_email = "networkx-discuss@googlegroups.com",
url = 'http://networkx.lanl.gov/'
download_url="http://networkx.lanl.gov/download/networkx"
platforms = ['Linux','Mac OSX','Windows','Unix']
keywords = ['Networks', 'Graph Theory', 'Mathematics', 'network', 'graph', 'discrete mathematics', 'math']
classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics',
        ]

# Get date dynamically
import time
date = time.asctime()
del time

if __name__ == '__main__':
    # Write versionfile for nightly snapshots.
    write_versionfile()

