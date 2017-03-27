# -*- coding: utf-8 -*-
"""
Tests for the Generator for extended-Barabasi graphs.

"""
#    Copyright (C) 2017 by
#    Bilal Al Jammal (bilal.eljammal@gmail.com)
#    Jose Ignacio Tamayo (jose.tamayo@gmail.com)
#
#    During Master of Science studies at Telecom Sudparis (www.telecom-sudparis.eu)
#
#    All rights reserved.

import networkx as nx
import sys,getopt
import matplotlib.pyplot as plt

from networkx.generators.random_graphs import extended_barabasi_albert_graph

def main(argv):
    """
        This creates a extended-BA graph according to the parameters passed by CLI
        
        Usage:
        ------
        
        python ExtendedBA.py -m <1> -n <100> -p <0.3> -q <0.3>
        
    """
    
    m_arg = 1
    n_arg = 100
    p_arg = 0.3
    q_arg = 0.3
    
    try:
      opts, args = getopt.getopt(argv,"n:m:p:q:",["n=","m=","p=","q="])
    except getopt.GetoptError:
      usage_print()
      sys.exit(9)
    for opt, arg in opts:
      if opt in ("-n", "--n"):
         n_arg = int(arg)
      elif opt in ("-m", "--m"):
         m_arg = int(arg)
      elif opt in ("-p", "--p"):
         p_arg = float(arg)
      elif opt in ("-q", "--q"):
         q_arg = float(arg)
   
    print 'eBA graph of %d nodes, with %d attachment, and (p=%f,q=%f) probabilities  "' % (n_arg,m_arg,p_arg,q_arg)
   
    G = extended_barabasi_albert_graph(n=n_arg, m=m_arg, p=p_arg,q=q_arg)
    
    pos=nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos,
                           node_color='r',
                           node_size=500,
                           alpha=0.8)
    
    nx.draw_networkx_edges(G,pos,width=1.0,alpha=0.5)
    
    
    plt.axis('off')
    #nx.draw(G)
    plt.show()
    
#endef

def usage_print():
    print "Usage:"
    print "python ExtendedBA.py -m <> -n <> -p <> -q <>"
    print "\t-m\tAttachment value for the graph. >1, generally in the range [1,inf)."
    print "\t-n\tSize of the desired graph, as number of nodes. >1, generally in the range [100,inf)."
    print "\t-p -q\tProbabilities of growth. In the range [0,1), such that p+q<1."

if __name__ == "__main__":
   main(sys.argv[1:])
