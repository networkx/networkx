# graph drawing and interface to graphviz
import sys
# These packages need 2.6 <= Python < 3.0
if sys.version_info[:2] < (3, 0):
    from nx_pylab import *
    import nx_pylab
    from layout import *
    import layout

    # graphviz interface
    # prefer pygraphviz/agraph (it's faster)
    from nx_agraph import *
    import nx_agraph
    try:
        import pydot
        import nx_pydot    
        from nx_pydot import *
    except:
        pass

    try:
        import pygraphviz
        from nx_agraph import *
    except:    
        pass 
else:
    import warnings
    warnings.warn('Drawing package networkx/drawing not supported '
                  'with Python 3.x') 
