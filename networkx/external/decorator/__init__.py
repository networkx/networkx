"""
    Hack for including decorator-3.3.1 in NetworkX.
"""

import sys

if sys.version >= '3':
    from ._decorator3 import *
    _decorator = _decorator3
else:
    from ._decorator import *
