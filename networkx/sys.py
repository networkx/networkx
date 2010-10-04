"""
    Module containing version information for NetworkX.
    
    If this info can be obtained from a live vcs repo, then it is so obtained.
    Otherwise, an attempt is made to grab the version info from the statically
    generated version.py. As a last resort, if version.py has not been created,
    then no vcs info will be available.
"""

import networkx.release as release

__all__ = ['date', 'date_info', 'dev', 'vcs_info', 'version', 'version_info']

date = None
date_info = None
dev = None
vcs_info = None
version = None
version_info = None

if release.revision is None:
    # we probably not running in an vcs directory   
    try:
        import networkx.version
    except ImportError:
        print "import error"
        dynamic = True
    else:
        dynamic = False
else:
    dynamic = True

if dynamic:
    # 1) either version.py didn't exist or
    # 2) we are running from a live version control directory
    date = release.date
    date_info = release.date_info
    dev = release.dev
    vcs_info = release.vcs_info
    version = release.version
    version_info = release.version_info
else:
    # using statically stored release data (from installation/build time).
    date = networkx.version.date
    date_info = networkx.version.date_info
    dev = networkx.version.dev
    vcs_info = networkx.version.vcs_info
    version = networkx.version.version
    version_info = networkx.version.version_info    

