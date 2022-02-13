#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# kirchhoffs_circuit_laws.py - using NetworkX for Kirchhoff's circuit laws
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Example of creating Kirchhoff's circuit laws from a (directed) multigraph.

"""

import networkx as nx

if __name__ == "__main__":
    # Create a graph representing three resistors in series.
    resistors = [(1, 2, "R0", {"volt": "V0", "curr": "I0"}),
                 (1, 2, "R1", {"volt": "V1", "curr": "I1"}),
                 (1, 2, "R2", {"volt": "V2", "curr": "I2"}),
                 (1, 3, "c0", {"volt": "Vcc", "curr": "Icc"}),
                 (3, 2, "c1", {"volt": "Vss", "curr": "Iss"})]
    G = nx.MultiGraph(resistors)
    volt = [e[2]["volt"] for e in G.edges(data=True)]
    curr = [e[2]["curr"] for e in G.edges(data=True)]

    # Kirchhoff's voltage law states that the sum of all voltages in a
    # resistor network is zero. Each element of the list `KVL` stores a
    # string representation of an equation demonstrating this law.
    KVL = []
    M = nx.cycle_basis_matrix(G).T
    for row in M:
        ind = row.nonzero()[0]
        token = "".join(" {} {}".format("+" if row[j] > 0 else "-", volt[j])
                        for j in ind)
        KVL.append(token + " = 0")

    # Kirchhoff's current law states that the sum of currents flowing
    # into a node equals the sum of currents flowing out of a node. Each
    # element of the list `KCL` stores a string representation of an
    # equation demonstrating this law.
    KCL = []
    M = nx.incidence_matrix(G, oriented=True).toarray()[:-1]
    for row in M:
        ind = row.nonzero()[0]
        token = "".join(" {} {}".format("+" if row[j] > 0 else "-", curr[j])
                        for j in ind)
        KCL.append(token + " = 0")

    print("Kirchhoff's laws for three resistors in series:")
    for eq in KVL:
        print(eq)
    for eq in KCL:
        print(eq)
