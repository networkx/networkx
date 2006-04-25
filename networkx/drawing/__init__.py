# graph drawing
# try to load drawing and layout modules and fail silently if not available

try:
    # needs pydot, graphviz 
    from nx_pydot import *
except ImportError:
    pass

try:
    # needs pygraphviz, graphviz
    # if successful,
    # write_dot, read_dot, graphviz_layout will come from pygraphviz
    # else they will be the ones in nx_pydot or none at all if that failed
    from nx_pygraphviz import *
except ImportError:
    pass

try:
    # needs matplotlib (including either numpy, Numeric, or numarray)
    from nx_pylab import *
except ImportError:
    pass

try:
    # needs numpy or Numeric
    from layout import *
except ImportError:
    pass
