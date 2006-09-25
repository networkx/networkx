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
    # write_dot, read_dot, graphviz_layout will come from pygraphviz Agraph
    # version 0.21 or earlier
    from nx_pygraphviz import *
except ImportError:
    pass

try:
    # needs pygraphviz, graphviz
    # if successful,
    # write_dot, read_dot, graphviz_layout will come from pygraphviz AGraph
    # version 0.32 or greater
    from nx_agraph import *
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
