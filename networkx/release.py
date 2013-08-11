"""Release data for NetworkX.

When NetworkX is imported a number of steps are followed to determine
the version information.

   1) If the release is not a development release (dev=False), then version
      information is read from version.py, a file containing statically
      defined version information.  This file should exist on every
      downloadable release of NetworkX since setup.py creates it during
      packaging/installation.  However, version.py might not exist if one
      is running NetworkX from the mercurial repository.  In the event that
      version.py does not exist, then no vcs information will be available.

   2) If the release is a development release, then version information
      is read dynamically, when possible.  If no dynamic information can be
      read, then an attempt is made to read the information from version.py.
      If version.py does not exist, then no vcs information will be available.

Clarification:
      version.py is created only by setup.py

When setup.py creates version.py, it does so before packaging/installation.
So the created file is included in the source distribution.  When a user
downloads a tar.gz file and extracts the files, the files will not be in a
live version control repository.  So when the user runs setup.py to install
NetworkX, we must make sure write_versionfile() does not overwrite the
revision information contained in the version.py that was included in the
tar.gz file. This is why write_versionfile() includes an early escape.

"""

#    Copyright (C) 2004-2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from __future__ import absolute_import

import os
import sys
import time
import datetime
import subprocess

basedir = os.path.abspath(os.path.split(__file__)[0])

def write_versionfile():
    """Creates a static file containing version information."""
    versionfile = os.path.join(basedir, 'version.py')

    text = '''"""
Version information for NetworkX, created during installation.

Do not add this file to the repository.

"""

import datetime

version = %(version)r
date = %(date)r

# Was NetworkX built from a development version? If so, remember that the major
# and minor versions reference the "target" (rather than "current") release.
dev = %(dev)r

# Format: (name, major, min, revision)
version_info = %(version_info)r

# Format: a 'datetime.datetime' instance
date_info = %(date_info)r

# Format: (vcs, vcs_tuple)
vcs_info = %(vcs_info)r

'''

    # Try to update all information
    date, date_info, version, version_info, vcs_info = get_info(dynamic=True)

    def writefile():
        fh = open(versionfile, 'w')
        subs = {
            'dev' : dev,
            'version': version,
            'version_info': version_info,
            'date': date,
            'date_info': date_info,
            'vcs_info': vcs_info
        }
        fh.write(text % subs)
        fh.close()

    if vcs_info[0] == 'mercurial':
        # Then, we want to update version.py.
        writefile()
    else:
        if os.path.isfile(versionfile):
            # This is *good*, and the most likely place users will be when
            # running setup.py. We do not want to overwrite version.py.
            # Grab the version so that setup can use it.
            sys.path.insert(0, basedir)
            from version import version
            del sys.path[0]
        else:
            # This is *bad*.  It means the user might have a tarball that
            # does not include version.py.  Let this error raise so we can
            # fix the tarball.
            ##raise Exception('version.py not found!')

            # We no longer require that prepared tarballs include a version.py
            # So we use the possibly trunctated value from get_info()
            # Then we write a new file.
            writefile()

    return version

def get_revision():
    """Returns revision and vcs information, dynamically obtained."""
    vcs, revision, tag = None, None, None

    hgdir = os.path.join(basedir, '..', '.hg')
    gitdir = os.path.join(basedir, '..', '.git')

    if os.path.isdir(hgdir):
        vcs = 'mercurial'
        try:
            p = subprocess.Popen(['hg', 'id'], 
                                 cwd=basedir,
                                 stdout=subprocess.PIPE)
        except OSError:
            # Could not run hg, even though this is a mercurial repository.
            pass
        else:
            stdout = p.communicate()[0]
            # Force strings instead of unicode.
            x = list(map(str, stdout.decode().strip().split()))
            
            if len(x) == 0:
                # Somehow stdout was empty. This can happen, for example,
                # if you're running in a terminal which has redirected stdout.
                # In this case, we do not use any revision/tag info.
                pass
            elif len(x) == 1:
                # We don't have 'tip' or anything similar...so no tag.
                revision = str(x[0])
            else:
                revision = str(x[0])
                tag = str(x[1])
                
    elif os.path.isdir(gitdir):
        vcs = 'git'
        # For now, we are not bothering with revision and tag.

    vcs_info = (vcs, (revision, tag))

    return revision, vcs_info

def get_info(dynamic=True):
    ## Date information
    date_info = datetime.datetime.now()
    date = time.asctime(date_info.timetuple())

    revision, version, version_info, vcs_info = None, None, None, None

    import_failed = False
    dynamic_failed = False

    if dynamic:
        revision, vcs_info = get_revision()
        if revision is None:
            dynamic_failed = True

    if dynamic_failed or not dynamic:
        # This is where most final releases of NetworkX will be.
        # All info should come from version.py. If it does not exist, then
        # no vcs information will be provided.
        sys.path.insert(0, basedir)
        try:
            from version import date, date_info, version, version_info, vcs_info
        except ImportError:
            import_failed = True
            vcs_info = (None, (None, None))
        else:
            revision = vcs_info[1][0]
        del sys.path[0]

    if import_failed or (dynamic and not dynamic_failed):
        # We are here if:
        #   we failed to determine static versioning info, or
        #   we successfully obtained dynamic revision info
        version = ''.join([str(major), '.', str(minor)])
        if dev:
            version += '.dev_' + date_info.strftime("%Y%m%d%H%M%S")
        version_info = (name, major, minor, revision)

    return date, date_info, version, version_info, vcs_info

## Version information
name = 'networkx'
major = "1"
minor = "9"


## Declare current release as a development release.
## Change to False before tagging a release; then change back.
dev = True


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
maintainer = "NetworkX Developers"
maintainer_email = "networkx-discuss@googlegroups.com"
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics']

date, date_info, version, version_info, vcs_info = get_info()

if __name__ == '__main__':
    # Write versionfile for nightly snapshots.
    write_versionfile()

