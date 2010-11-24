"""
    Module containing version information for NetworkX.
    
    If this info can be obtained from a live vcs repo, then it is so obtained.
    Otherwise, an attempt is made to grab the version info from the statically
    generated version.py. As a last resort, if version.py has not been created,
    then no vcs info will be available.
"""

import networkx.release as release

__all__ = ['date', 'date_info', 'dev', 'vcs_info', 'version', 'version_info']

# Note, these could all be kept/accessible in/from release.py
# So this module really just exists to consolidate information we want to 
# present to the user as an 'offical' sys module.

dev = release.dev
date, date_info, version, version_info, vcs_info = release.get_info()

