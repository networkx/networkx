"""Release data for NetworkX."""

#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.


import os
import re
import time
import datetime
import subprocess


def write_versionfile():
    """Creates a static file containing version information."""
    base = os.path.split(__file__)[0]
    versionfile = os.path.join(base, 'version.py')
    if revision is None and os.path.isfile(versionfile):
        # Unable to get revision info, so probably not in an vcs directory
        # If a version.py already exists, let's not overwrite it.
        # Useful mostly for nightly tarballs, but also for installed builds.
        return
    fh = open(versionfile, 'w')
    text = '''"""
Version information for NetworkX, created during installation.

Do not add this file to the repository.

"""

import datetime

version = %(version)r
date = %(date)r

# Was NetworkX built from a development version? If so, remember the the major
# and minor versions reference the "target" (rather than "current") release.
dev = %(dev)r

# Format: (name, major, min, mercurial revision)
version_info = %(version_info)r

# Format: a 'datetime.datetime' instance
date_info = %(date_info)r

# Format: (vcs, vcs_tuple)
vcs_info = %(vcs_info)r

'''
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

def get_revision():
    # currently supported: mercurial, git
    funcs = {'mercurial': get_mercurial_revision, 'git': get_git_revision}
    vcs_dict = {'mercurial': None, 'git': None}
    for vcs in vcs_dict:
        vcs_dict[vcs] = funcs[vcs]()

    # only mercurial revision is used
    if vcs_dict['mercurial'] is not None:
        rev = vcs_dict['mercurial']['hash']
    else:
        rev = None

    return rev, vcs_dict
        
def get_mercurial_revision():
    from subprocess import PIPE
    
    basedir = os.path.split(__file__)[0]
    curdir = os.path.abspath(os.path.curdir)
    if basedir:
        os.chdir(basedir)
    p = subprocess.Popen(['hg', 'id'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if not p.returncode:
        hg = {}
        hg['hash'], hg['tag'] = stdout.decode().strip().split(' ')
    else:
        hg = None
    os.chdir(curdir)
    return hg
    
def get_git_revision():
    from subprocess import PIPE
    
    basedir = os.path.split(__file__)[0]
    curdir = os.path.abspath(os.path.curdir)
    if basedir:
        os.chdir(basedir)
    
    # Determine hash value
    cmd = ['git', 'rev-parse', 'HEAD']
    p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if not p.returncode:
        git = {}
        git['hash'] = stdout.strip()
        
        # Determine if there are local modifications
        local = False
        cmd = ['git', 'diff']
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            local = True
        cmd = ['git', 'diff', '--staged']
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            local = True
        if local:
            git['hash'] += '+'
            
        # Determine the branch name
        cmd = ['git', 'branch']
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        for line in stdout:
            if line.startswith("*"):
                branch = line.split()[1]
                break
        git['branch'] = branch
    else:
        git = None
    os.chdir(curdir)
    return git
    
def get_dynamic_info():
    version = ''.join([str(major), '.', str(minor)])
    revision, vcs_dict = get_revision()
    if dev:
        version += '.dev'
        # revision info is in `version` only if this is a 'dev' revision
        if revision is not None:
            version += "_%s" % revision
    # mercurial revision info is always in `version_info`.
    version_info = (name, major, minor, revision)

    # vcs_info
    mercurial = vcs_dict['mercurial']
    git = vcs_dict['git']
    if mercurial is not None:
        vcs_info = ('mercurial', (mercurial['hash'], mercurial['tag']))
    elif git is not None:
        vcs_info = ('git', (git['hash'], git['branch']))
    else:
        vcs_info = (None,  ())

    return revision, version, version_info, vcs_info

## Date information
date_info = datetime.datetime.now()
date = time.asctime(date_info.timetuple())

## Version information
name = 'networkx'
major = 1
minor = 4

## Declare current release as a development release.
## Change to False before tagging a release; then change back.
dev = True

## Populate other dynamic values
revision, version, version_info, vcs_info = get_dynamic_info()

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
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics']

if __name__ == '__main__':
    # Write versionfile for nightly snapshots.
    write_versionfile()

