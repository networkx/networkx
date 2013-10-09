__author__ ='Johannes Castner'

"""
BayesNet inherits from both, a networkx DiGraph and Joint, a class object representing a joint distribution which is code that was originally written by by Allen B. Downey, for his book "Think Bayes", available from greenteapress.com
Copyright 2013 Johannes Castner, 2012 Allen B. Downey,
License: GNU GPLv3 http://www.gnu.org/licenses/gpl.html

2006-2011 Aric Hagberg <hagberg@lanl.gov>, Dan Schult <dschult@colgate.edu>, Pieter Swart <swart@lanl.gov>. BSD license.
"""
import bisect
import copy
import logging
import math
import numpy
import random
from thinkbayes import * #must have thinkbayes.py in the current directory or in the system path.
import scipy.stats
from scipy.special import erf, erfinv
from networkx import DiGraph
from numpy import zeros, array
from math import sqrt, log

#import the beta function for priors on causal effects in BayesNet:

from scipy.stats import beta

class BayesNet(DiGraph, Joint):
    """
    A BayesNet is both, a graph and a joint distribution. For now, it only
    allows for binary variables. All methods that start with capital letters
    relate more to joint distributions and those that are more graph-related start
    with lower case letters.
    The joint probability is encoded, using the Noisy-OR encoding (Pearl 1988).
    """

    def __init__(self, data=None, name='', p=0.5, effect_pdf=lambda x, a, b : beta(a, b).pdf(x), a=2, b=2):
        """
        Effect pdf is the pdf that a causal effect is assumed to be drawn from. In the absense of a "causal_effect" that is explicitly
        included in the link between two nodes, we integrate over this distribution.
        """

        DiGraph.__init__(self, data=data, name=name)
        Joint.__init__(self)
        self.p=p
        self.n=len(self.nodes())
        self.support=[]
        self.names=[]
        self.indep_vars=[]
        self.dep_vars=[]
        self.effect_pdf= lambda x: effect_pdf(x, a, b)


    def add_edges_from(self, ebunch):
        #first, we rename the nodes to be indices. This is practical
        #for manipulating the joint distribution (maybe not ideal).
        #newbunch=[e for e in ebunch if len(e)==3]
        #singletons=[v for v in e for e in ebunch if len(e)==1]
        #It would be interesting to extend the graphing capabilities of networkx to be able
        #to attach edge labels ('+', '-', '0' etc.) and show them.
        if self.names:
            self.names=sorted(set([v for e in ebunch for v in e[:2]] + self.names))

        #if we don't sort, we get in trouble with comparing joint distributions (the same nodes can be ordered differently)
            check_bunch=[(self.names[i], self.names[j]) for i, j in self.edges()]
            if [e[:2] for e in ebunch] in check_bunch:
                return
        else:
            self.names=sorted(set([v for e in ebunch for v in e[:2]]))


        for i, n in enumerate(self.names):

            for e in ebunch:
                index=ebunch.index(e)
                if len(e)==3:
                    l, k, dd=e
                    if type(dd)==dict:
                        dd=dd
                    elif type(dd)==float or type(dd)==int:
                        dd={'weight': dd}
                    else:
                        dd={'causal_effect': dd}

                if len(e)==2:
                    l, k = e
                    dd={}

                if l==n:
                    l=i
                elif k==n:
                    k=i

                ebunch[index]=l, k, dd
            for node in self.nodes():
                if n ==self.node[node]['name']:
                    self.node[i]={'name': n}
                    self.edge[i]={}
        DiGraph.add_edges_from(self, ebunch=ebunch)

        self.n=len(self.nodes())
        #attach the names:
        for node in self.nodes():
            self.node[node]['name']=self.names[node]
        #number of nodes
        fro, to = zip(*self.edges())
        self.indep_vars=sorted(set(f for f in self.nodes() if f not in set(to)))
        self.dep_vars  =sorted(set(to))
        for var in self.indep_vars:
            self.node[var]['pmf']=Pmf()
            self.node[var]['pmf'].Set(1,self.p)
            self.node[var]['pmf'].Set(0, 1-self.p)
        #for var in self.dep_vars:
         #   self.node[var]['pmf']=Pmf()
         #   self.node[var]['pmf'].Set(1,0) #first set it all to 0
         #   self.node[var]['pmf'].Set(0, 1)


        for w in self.dep_vars:
            self.node[w]['causes']={}

        for i in self.nodes():
            for j in self.edge[i]:
                self.node[j]['causes'][i]=self.edge[i][j]['causal_effect'] if 'causal_effect' in self.edge[i][j] else self.edge[i][j]['weight'] if 'weight' in self.edge[i][j] else '+'


        self.SetProbs()

    def SetProbs(self):
        self.d={}
        self.support=[]
        n=len(self.nodes())
        for outcome in range(2**n):
            self.support.append(tuple([(outcome>>i)&1 for i in xrange(n-1,-1,-1)]))


        for outcome in self.support:
            pr=[0]*len(outcome)
            p_out=1
            for i in range(len(outcome)):
                if i in self.indep_vars:
                    pr[i]=self.node[i]['pmf'].d[outcome[i]]
                    p_out *=pr[i]
                else:
                    tot=1
                    for node in self.node[i]['causes']:
                        if type(self.node[i]['causes'][node])==float and self.node[i]['causes'][node]>=0:
                            tot *=((1.0-self.node[i]['causes'][node])**outcome[node])
                        elif self.node[i]['causes'][node] =='+':
                            tot=outer(tot, [self.effect_pdf(w)*(1.0-w)**outcome[node] for w in linspace(0, 1, 100)])

                        elif self.node[i]['causes'][node] =='-':
                            tot=outer(tot, [self.effect_pdf(w)*(1.0-w)**(1-outcome[node]) for w in linspace(0, 1, 100)])
                        elif type(self.node[i]['causes'][node])==float and self.node[i]['causes'][node]<=0:
                            tot *=((1.0-abs(self.node[i]['causes'][node]))**(1-outcome[node]))

                    pr[i]=1-mean(tot) if outcome[i]==1 else 1-(1-mean(tot))
                    p_out *=pr[i]

            self.Set(outcome, p_out)

    def add_nodes_from(self, nodes, **attr):
        H=copy.deepcopy(self)
        self.clear()
        if not H.nodes():
            DiGraph.add_nodes_from(self, nodes, **attr)

            self.names=names=sorted(nodes)
            for i, n in enumerate(self.names):
                self.node[i]={'name': n, 'pmf': Pmf()}
                self.node[i]['pmf'].Set(1,self.p)
                self.node[i]['pmf'].Set(0, 1-self.p)
                self.remove_node(n)
                self.edge[i]={}
                self.indep_vars+=[i]
            self.SetProbs()
            return

        DiGraph.add_nodes_from(self, nodes, **attr)
        #ind_vars=[var for var in H.indep_vars]
        #DiGraph.add_nodes_from(self, ind_vars)
        self.names=names=sorted(set(H.names + nodes))
        for i, n in enumerate(names):
            try:
                self.node[i], self.edge[i]=H.node[i], H.edge[i]
            except:
                self.node[i]={'name': n, 'pmf': Pmf()}
                self.node[i]['pmf'].Set(1,self.p)
                self.node[i]['pmf'].Set(0, 1-self.p)
                self.remove_node(n)
                self.edge[i]={}
                self.indep_vars+=[i]

        self.SetProbs()

    def MakeMixture(self, other, lamb=0.5):
        mixed = Joint() #mixing the two probability distributions
        for x, p in self.Items():
            mixed.Set(x,lamb * p + (1 - lamb) * other.d[x])
        return mixed

    def KL_divergence(self, other):
        """ Compute KL divergence of two BayesNets."""
        try:
            return sum(p * log((p /other.d[x])) for x, p in self.Items() if p != 0.0 or p != 0)
        except ZeroDivisionError:
            return float("inf")

    def JensenShannonDivergence(self, other):
        JSD = 0.0
        lamb=0.5
        mix=self.MakeMixture(other=other, lamb=0.5)
        JSD=lamb * self.KL_divergence(mix) + lamb * other.KL_divergence(mix)
        return JSD
