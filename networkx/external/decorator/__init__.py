"""
    Hack for including decorator-3.3.1 in NetworkX.
"""
import sys
if sys.version >= '3':
    from .decorator3._decorator3 import *
else:
    from .decorator2._decorator2 import *
