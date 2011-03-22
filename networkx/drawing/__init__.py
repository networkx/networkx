# graph drawing and interface to graphviz
import sys
from networkx.drawing.layout import *
from networkx.drawing.nx_pylab import *

# graphviz interface
# prefer pygraphviz/agraph (it's faster)
from networkx.drawing.nx_agraph import *
try:
    import pydot
    import networkx.drawing.nx_pydot
    from networkx.drawing.nx_pydot import *
except:
    pass
try:
    import pygraphviz
    from networkx.drawing.nx_agraph import *
except:    
    pass 

