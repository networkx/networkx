#!/usr/bin/env python
# encoding: utf-8
"""
Example of creating Kirchhof vcircuit laws from a (directed)multigraph.

"""

__author__ = """\n""".join(['Juan Pablo Carbajal <juanpi+dev@gmail.com>'])

import networkx as nx

if __name__ == '__main__':
    # Graph representing three resistors in series.
    cables = [(1,2,"R0",{"volt":"V0","curr":"I0"}), \
              (1,2,"R1",{"volt":"V1","curr":"I1"}), \
              (1,2,"R2",{"volt":"V2","curr":"I2"}),  \
              (1,3,"c0",{"volt":"Vcc","curr":"Icc"}), \
              (3,2,"c1",{"volt":"Vss","curr":"Iss"})]
    G = nx.MultiGraph(cables)
    volt = [ e[2]["volt"] for e in G.edges(data=True) ]
    curr = [ e[2]["curr"] for e in G.edges(data=True) ]
 
    # Voltage law
    M = nx.cycle_basis_matrix (G).T
    KVL = []
    for row in M:
        ind = row.nonzero()[0]
        token = []
        for j in ind:
            token.append (" + "+volt[j] if row[j]>0 else " - "+volt[j])

        KVL.append("".join(token)+" = 0")

    # Current law
    M = nx.incidence_matrix(G, oriented=True).toarray()[:-1]
    KCL = []
    for row in M:
        ind = row.nonzero()[0]
        token = []
        for j in ind:
            token.append (" + "+curr[j] if row[j]>0 else " - "+curr[j])

        KCL.append("".join(token)+" = 0")
    
    print "Kirchhof laws for three resistors in series:"
    for eq in KVL:
        print eq 
    for eq in KCL:
        print eq
        

