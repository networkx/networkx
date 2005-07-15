"""
Threshold Graphs - Creation, manipulation and identification.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-17 08:06:22 -0600 (Fri, 17 Jun 2005) $"
__credits__ = """"""
__version__ = "$Revision: 1049 $"
# $Header$

#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

import random  # for swap_d 
import networkx

def is_threshold_graph(G):
    """
    Returns True if G is a threshold graph.
    """
    return is_threshold_sequence(G.degree())
    
def is_threshold_sequence(degree_sequence):
    """
    Returns True if the sequence is a threshold degree seqeunce.
    
    Uses the property that a threshold graph must be constructed by
    adding either dominating or isolated nodes. Thus, it can be
    deconstructed iteratively by removing a node of degree zero or a
    node that connects to the remaining nodes.  If this deconstruction
    failes then the sequence is not a threshold sequence.
    """
    ds=degree_sequence[:] # get a copy so we don't destroy original 
    ds.sort()
    while ds:     
        if ds[0]==0:      # if isolated node
            ds.pop(0)     # remove it 
            continue
        if ds[-1]!=len(ds)-1:  # is the largest degree node dominating?
            return False       # no, not a threshold degree sequence
        ds.pop()               # yes, largest is the dominating node
        ds=[ d-1 for d in ds ] # remove it and decrement all degrees
    return True


def creation_sequence(degree_sequence,with_labels=False,compact=False):
    """
    Determines the creation sequence for the given threshold degree sequence.

    The creation sequence is a list of single characters 'd'
    or 'i': 'd' for dominating or 'i' for isolated vertices.
    Dominating vertices are connected to all vertices present when it
    is added.  The first node added is by convention 'd'.

    If with_labels==True:
    Returns a list of 2-tuples containing the vertex number 
    and a character 'd' or 'i' which describes the type of vertex.

    If compact==True:
    Returns the creation sequence in a compact form that is the number
    of 'i's and 'd's alternating.
    Examples:
    [1,2,2,3] represents d,i,i,d,d,i,i,i
    [3,1,2] represents d,d,d,i,d,d

    Notice that the first number is the first vertex to be used for
    construction and so is always 'd'.

    with_labels and compact cannot both be True.

    Returns None if the sequence is not a threshold sequence
    """
    if with_labels and compact:
        raise ValueError,"compact sequences cannot be labeled"

    # make an indexed copy
    if isinstance(degree_sequence,dict):   # labeled degree seqeunce
        ds = [ [degree,label] for (label,degree) in degree_sequence.items() ]
    else:
        ds=[ [degree_sequence[i],i+1] for i in xrange(len(degree_sequence)) ] 
    ds.sort()
    cs=[]  # creation sequence
    while ds:
        if ds[0][0]==0:     # isolated node
            (d,v)=ds.pop(0)
            if len(ds)>0:    # make sure we start with a d
                cs.insert(0,(v,'i'))
            else:
                cs.insert(0,(v,'d'))
            continue
        if ds[-1][0]!=len(ds)-1:     # Not dominating node
            return None  # not a threshold degree sequence
        (d,v)=ds.pop()
        cs.insert(0,(v,'d'))
        ds=[ [d[0]-1,d[1]] for d in ds ]   # decrement due to removing node

    if with_labels: return cs
    if compact: return make_compact(cs)
    return [ v[1] for v in cs ]   # not labeled

def make_compact(creation_sequence):
    """
    Returns the creation sequence in a compact form
    that is the number of 'i's and 'd's alternating.
    Examples:
    [1,2,2,3] represents d,i,i,d,d,i,i,i.
    [3,1,2] represents d,d,d,i,d,d.
    Notice that the first number is the first vertex
    to be used for construction and so is always 'd'.
    """
    first=creation_sequence[0]
    if isinstance(first,str):    # creation sequence
        cs = creation_sequence[:]
    elif isinstance(first,tuple):   # labeled creation sequence
        cs = [ s[1] for s in creation_sequence ]
    else:
        raise TypeError, "Not a valid creation sequence type"

    ccs=[]
    count=1 # count the run lengths of d's or i's.
    for i in range(1,len(cs)):
        if cs[i]==cs[i-1]: 
            count+=1
        else:
            ccs.append(count)
            count=1
    ccs.append(count) # don't forget the last one
    return ccs
    
def uncompact(compact_creation_sequence):
    """
    Converts a compact creation sequence for a threshold
    graph to a standard creation sequence (unlabeled).
    See creation_sequence.
    """
    if not isinstance(compact_creation_sequence[0],int):
        raise TypeError, "Not a valid creation sequence type"
    cs = []
    ccscopy=compact_creation_sequence[:]
    while ccscopy:
        cs.extend(ccscopy.pop(0)*['d'])
        if ccscopy:
            cs.extend(ccscopy.pop(0)*['i'])
    return cs


def threshold_graph(creation_sequence):
    """
    Create a threshold graph from the creation sequence or compact
    creation_sequence.

    The input sequence can be a 

    creation sequence (e.g. ['d','i','d','d','d','i'])
    labeled creation sequence (e.g. [(0,'d'),(2,'d'),(1,'i')])
    compact creation sequence (e.g. [2,1,1,2,0])
    
    Use cs=creation_sequence(degree_sequence,labeled=True) 
    to convert a degree sequence to a creation sequence.

    Returns None if the sequence is not valid
    """
    # Turn input sequence into a labeled creation sequence
    first=creation_sequence[0]
    if isinstance(first,str):    # creation sequence
        ci = [(i+1,creation_sequence[i]) for i in xrange(len(creation_sequence))]
    elif isinstance(first,tuple):   # labeled creation sequence
        ci = creation_sequence[:]
    elif isinstance(first,int):  # compact creation sequence
        cs = uncompact(creation_sequence)
        ci = [(i+1,cs[i]) for i in xrange(len(cs))]
    else:
        print "not a valid creation sequence type"
        return None
        
    G=networkx.Graph()
    G.name="Threshold Graph"

    # add nodes and edges
    # if type is 'i' just add nodea
    # if type is a d connect to everything previous
    while ci:
        (v,node_type)=ci.pop(0)
        G.add_node(v)
        if node_type=='d': # dominating type, connect to all existing nodes
            for u in G.nodes(): 
                G.add_edge(v,u) # will silently ignore self loop
    return G


def shortest_path(creation_sequence,u,v):
    """
    Find the shortest path between u and v in a 
    threshold graph G with the given creation_sequence.

    For an unlabeled creation_sequence, the vertices 
    u and v must be integers in (0,len(sequence)) refering 
    to the position of the desired vertices in the sequence.

    For a labeled creation_sequence, u and v are labels of veritices.

    Use cs=creation_sequence(degree_sequence,with_labels=True) 
    to convert a degree sequence to a creation sequence.

    Returns a list of vertices from u to v.
    Example: if they are neighbors, it returns [u,v]
    """
    # Turn input sequence into a labeled creation sequence
    first=creation_sequence[0]
    if isinstance(first,str):    # creation sequence
        cs = [(i,creation_sequence[i]) for i in xrange(len(creation_sequence))]
    elif isinstance(first,tuple):   # labeled creation sequence
        cs = creation_sequence[:]
    elif isinstance(first,int):  # compact creation sequence
        ci = uncompact(creation_sequence)
        cs = [(i,ci[i]) for i in xrange(len(ci))]
    else:
        raise TypeError, "Not a valid creation sequence type"
        
    verts=[ s[0] for s in cs ]
    if v not in verts:
        raise ValueError,"Vertex %s not in graph from creation_sequence"%v
    if u not in verts:
        raise ValueError,"Vertex %s not in graph from creation_sequence"%u
    # Done checking
    if u==v: return [u]

    uindex=verts.index(u)
    vindex=verts.index(v)
    bigind=max(uindex,vindex)
    if cs[bigind][1]=='d':
        return [u,v]
    # must be that cs[bigind][1]=='i'
    cs=cs[bigind:]
    while cs:
        vert=cs.pop()
        if vert[1]=='d':
            return [u,vert[0],v]
    # All after u are type 'i' so no connection
    return -1



def find_alternating_4_cycle(G):
    """
    Returns False if there aren't any alternating 4 cycles.
    Otherwise returns the cycle as [a,b,c,d] where (a,b)
    and (c,d) are edges and (a,c) and (b,d) are not.
    """
    for (u,v) in G.edges():
        for w in G.nodes():
            if not G.has_edge(u,w) and u!=w:
                for x in G.neighbors(w):
                    if not G.has_edge(v,x) and v!=x:
                        return [u,v,w,x]
    return False



def find_threshold_graph(G):
    """
    Return a threshold subgraph that is close to largest in G.
    The threshold graph will contain the largest degree node in G.
    
    If you just want the creation sequence you can use
    creation_sequence(find_threshold_graph(G).degree(with_labels=True),
    labeled=True)
    """
    return threshold_graph(find_creation_sequence(G))


def find_creation_sequence(G):
    """
    Find a threshold subgraph that is close to largest in G.
    Returns the labeled creation sequence of that threshold graph.  
    """
    cs=[]
    # get a local pointer to the working part of the graph
    H=G
    while H.order()>0:
        # get new degree sequence on subgraph
        dsdict=H.degree(with_labels=True)
        ds=[ [dsdict[v],v] for v in dsdict ]
        ds.sort()
        # Update threshold graph nodes
        if ds[-1][0]==0: # all are isolated
            cs.extend( zip( dsdict, ['i']*(len(ds)-1)+['d']) )
            break   # Done!
        # pull off isolated nodes
        while ds[0][0]==0:
            (d,iso)=ds.pop(0)
            cs.append((iso,'i'))
        # find new biggest node
        (d,bigv)=ds.pop()
        # add edges of star to t_g
        cs.append((bigv,'d'))
        # form subgraph of neighbors of big node
        H=H.subgraph(H.neighbors(bigv))
    cs.reverse()
    return cs
    

    
### Properties of Threshold Graphs
def triangles(creation_sequence):
    """
    Compute number of triangles in the threshold graph with the
    given creation sequence.
    """
    # shortcut algoritm that doesn't require computing number
    # of triangles at each node.
    cs=creation_sequence    # alias
    nd=cs.count("d")        # number of d's in sequence
    ntri=nd*(nd-1)*(nd-2)/6 # number of traingles in clique of nd d's
    # now add r choose 2 triangles for every i in sequence where
    # r is the number of d's to the right of the current i
    for i in range(0,len(cs)): 
        if cs[i]=="i":
            r=cs[i:].count("d")
            ntri+=r*(r-1)/2
    return ntri


def triangle_sequence(creation_sequence):
    """
    Build triangle sequence for the given threshold graph creation sequence.

    """
    cs=creation_sequence
    seq=[]
    cs[0]="i"            # the first node is always isolated
    rd=cs.count("d")     # number of d's to the right of the current pos
    dcur=(rd-1)*(rd-2)/2 # number of traingles through a node of clique rd
    irun=0               # number of i's in the last run
    for i in range(0,len(cs)):
        if cs[i]=="d":
            tri=dcur+(rd-1)*irun    # new triangles at this d
        else: # cs[i]="i":
            if cs[i-1]=="d":        # new string of i's
                dcur+=(rd-1)*irun   # accumulate shared shortest paths
                irun=0              # reset i run counter
            irun+=1
            rd=cs[i:].count("d") # number of d's to the right of current pos
            tri=rd*(rd-1)/2      # new triangles at this i
        seq.append(tri)
    return seq


def cluster_sequence(creation_sequence):
    """
    Build cluster sequence from the given threshold graph creation sequence.
    """
    triseq=triangle_sequence(creation_sequence)
    degseq=degree_sequence(creation_sequence)
    cseq=[]
    for i in range(0,len(creation_sequence)):
        tri=triseq[i]
        deg=degseq[i]
        if deg <= 1:    # isolated vertex or single pair gets cc 0
            cseq.append(0)
            continue
        max_size=(deg*(deg-1))/2
        cseq.append(float(tri)/float(max_size))
    return cseq


def degree_sequence(creation_sequence):
    """
    Return degree sequence for the threshold graph with the given
    creation sequence
    """
    cs=creation_sequence  # alias
    seq=[]
    for i in range(0,len(cs)):
        r=cs[i:].count("d")
        if cs[i]=="i":
            seq.append(r)
        else:
            seq.append(r+i-1)
    return seq            

def shortest_path_length(creation_sequence,i):
    """
    Return the shortest path length from the node at index i to
    every other node for the threshold graph with the given
    creation sequence.

    Paths lengths in threshold graphs are either:
    0 - from self to self
    1 - from d to d
    1 - from i to d or d to i
    2 - from i to i
    """
    cs=creation_sequence
    spl=[2]*len(cs) # length 2 to every node
    spl[i]=0        # except self which is 0
    # and 1 for all d's to the right
    for j in range(i,len(spl)):   
        if cs[j]=="d":
            spl[j]=1
    # and -1 for any trailing i to indicate unreachable
    for j in range(len(spl)-1,0,-1):
        if cs[j]=="d":
            break
        spl[j]=-1
    return spl


def betweenness_sequence(creation_sequence):
    """
    Return betweenness for the threshold graph with the given creation
    sequence.  The result is unscaled.  To scale the values
    to the iterval [0,1] divide by (n-1)*(n-2).
    """
    cs=creation_sequence
    seq=[]               # betweenness
    cs[0]="i"            # the first node is always isolated
    dr=float(cs.count("d"))   # total number of d's to the right of curren pos
    irun=0               # number of i's in the last run
    pli=0                # position of last i
    dlast=0              # betweenness of last d
    b=0                  # betweenness of this index
    for i in range(0,len(cs)):
        if cs[i]=="d":
            # betweennees = amt shared with eariler d's and i's
            #             + new isolated nodes covered
            #             + new paths to all previous nodes
            b=dlast + (irun-1)*irun/dr + 2*irun*(pli+1-irun)/dr
        else:      # cs[i]="i":
            if cs[i-1]=="d":  # if this is a new run of i's
                irun=0        # reset counter
                dlast=b       # accumulate betweenness
            b=0      # isolated nodes have zero betweenness 
            irun+=1  # add another i to the run   
            pli=i 
            dr=float(cs[i:].count("d"))  # d's to the right of this position
        seq.append(float(b))
    return seq


def eigenvalues(creation_sequence):
    """
    Return sequence of eigenvalues of the Laplacian of the threshold
    graph for the given creation_sequence.

    Based on the Ferrer's diagram method.  The spectrum is integral
    and is the conjugate of the degree sequence.

    See:: 

      @Article{degree-merris-1994,
       author = 	 {Russel Merris},
       title = 	 {Degree maximal graphs are Laplacian integral},
       journal = 	 {Linear Algebra Appl.},
       year = 	 {1994},
       volume = 	 {199},
       pages = 	 {381--389},
      }

    """
    degseq=degree_sequence(creation_sequence)
    degseq.sort()
    eig=[]
    while 1:
        nzeros=degseq.count(0)
        degseq=degseq[nzeros:] # remove zeros at front
        e=len(degseq)
        if e==0:  # we have all eigenvalues except zero
            eig.append(0)
            return eig
        else:     # subtract 1 from each degree and continue
            eig.append(len(degseq))
            degseq=[i-1 for i in degseq]

    return eig


### Threshold graph creation routines

def random_threshold_sequence(n,p,seed=None):
    """
    Create a random threshold sequence of size n.
    A creation sequence is built by randomly choosing d's with
    probabiliy p and i's with probability 1-p.

    >>> s=random_threshold_sequence(10,0.5)

    returns a threshold sequence of length 10 with equal
    probably of an i or a d at each position.

    A "random" threshold graph can be built with

    >>> G=threshold_graph(random_threshold_sequence(n,p))

    """
    if not seed is None:
        random.seed(seed)

    if not (p<=1 and p>=0):
        raise ValueError,"p must be in [0,1]"

    cs=['d']  # threshold sequences always start with a d
    for i in range(1,n):
        if random.random() < p: 
            cs.append('d')
        else:
            cs.append('i')
    return cs





# maybe *_d_threshold_sequence routines should
# be (or be called from) a single routine with a more descriptive name
# and a keyword parameter?
def right_d_threshold_sequence(n,m):
    """
    Create a skewed threshold graph with a given number
    of vertices (n) and a given number of edges (m).
    
    The routine returns an unlabeled creation sequence 
    for the threshold graph.

    FIXME: describe algorithm

    """
    cs=['d']+['i']*(n-1) # create sequence with n insolated nodes

    #  m <n : not enough edges, make disconnected 
    if m < n: 
        cs[m]='d'
        return cs

    # too many edges 
    if m > n*(n-1)/2:
        raise ValueError,"Too many edges for this many nodes."

    # connected case m >n-1
    ind=n-1
    sum=n-1
    while sum<m:
        cs[ind]='d'
        ind -= 1
        sum += ind
    ind=m-(sum-ind)
    cs[ind]='d'
    return cs

def left_d_threshold_sequence(n,m):
    """
    Create a skewed threshold graph with a given number
    of vertices (n) and a given number of edges (m).

    The routine returns an unlabeled creation sequence 
    for the threshold graph.

    FIXME: describe algorithm

    """
    cs=['d']+['i']*(n-1) # create sequence with n insolated nodes

    #  m <n : not enough edges, make disconnected 
    if m < n: 
        cs[m]='d'
        return cs

    # too many edges 
    if m > n*(n-1)/2:
        raise ValueError,"Too many edges for this many nodes."

    # Connected case when M>N-1
    cs[n-1]='d'
    sum=n-1
    ind=1
    while sum<m:
        cs[ind]='d'
        sum += ind
        ind += 1
    if sum>m:    # be sure not to change the first vertex
        cs[sum-m]='i'
    return cs

def swap_d(cs,p_split=1.0,p_combine=1.0,seed=None):
    """
    Perform a "swap" operation on a threshold sequence.

    The swap preserves the number of nodes and edges
    in the graph for the given sequence.
    The resulting sequence is still a threshold sequence.

    Perform one split and one combine operation on the
    'd's of a creation sequence for a threshold graph.
    This operation maintains the number of nodes and edges
    in the graph, but shifts the edges from node to node
    maintaining the threshold quality of the graph.
    """
    if not seed is None:
        random.seed(seed)

    # preprocess the creation sequence
    dlist= [ i+1 for (i,node_type) in enumerate(cs[1:-1]) if node_type=='d' ]
    # split
    if random.random()<p_split:
        choice=random.choice(dlist)
        split_to=random.choice(range(choice))
        flip_side=choice-split_to
        if split_to!=flip_side and cs[split_to]=='i' and cs[flip_side]=='i':
            cs[choice]='i'
            cs[split_to]='d'
            cs[flip_side]='d'
            dlist.remove(choice)
            # don't add or combine may reverse this action            
            # dlist.extend([split_to,flip_side])
#            print >>sys.stderr,"split at %s to %s and %s"%(choice,split_to,flip_side)
    # combine
    if random.random()<p_combine and dlist:
        first_choice= random.choice(dlist)
        second_choice=random.choice(dlist)
        target=first_choice+second_choice
        if target >= len(cs) or cs[target]=='d' or first_choice==second_choice:
            return cs
        # OK to combine
        cs[first_choice]='i'
        cs[second_choice]='i'
        cs[target]='d'
#        print >>sys.stderr,"combine %s and %s to make %s."%(first_choice,second_choice,target)

    return cs
        


        
def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('../tests/threshold.txt', package='networkx')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
