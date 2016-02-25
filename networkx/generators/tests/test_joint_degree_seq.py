import time
from nose.tools import *
from networkx.generators.joint_degree_seq import is_valid_joint_degree, joint_degree_model
from networkx.algorithms.assortativity import degree_mixing_dict
from networkx.generators import powerlaw_cluster_graph

def test_is_valid_joint_degree():
    # valid joint degree that satisfies all five conditions
    nkk = {1: {4: 1},
           2: {2: 2, 3: 2, 4: 2}, 
           3: {2: 2, 4: 1}, 
           4: {1: 1, 2: 2, 3: 1}
           }
    assert_true(is_valid_joint_degree(nkk))
    
    # condition 1
    nkk_1 = {1: {4: 1.5},          # nkk[1][4] not integer
             2: {2: 2, 3: 2, 4: 2}, 
             3: {2: 2, 4: 1}, 
             4: {1: 1.5, 2: 2, 3: 1}
             } 
    assert_false(is_valid_joint_degree(nkk_1))
    
    # condition 2
    nkk_2 = {1: {4: 1},
             2: {2: 2, 3: 2, 4: 3},   # nk[2] = sum(nkk[2][j)/2, is not an intger
             3: {2: 2, 4: 1}, 
             4: {1: 1, 2: 3, 3: 1}    # nk[4] = sum(nkk[4][j)/4, is not an integer
             } 
    assert_false(is_valid_joint_degree(nkk_2))    
    
    # condition 3 and 4
    nkk_3 = {1: {4: 2},              #nkk[1][4]>nk[1][nk[4] (not possible)
             2: {2: 2, 3: 2, 4: 2}, 
             3: {2: 2, 4: 1}, 
             4: {1: 2, 2: 2, 3: 1}
             }
    
    # condition 5
    nkk_5 = {1:{1:9}}   # nkk[1][1] not even    
    assert_false(is_valid_joint_degree(nkk_5))     
    
def test_joint_degree_model(ntimes = 100):
    for i in range(ntimes):
        seed = time.time()   

        n, m, p = 20, 10, 1    
        # generate random graph with model powerlaw_cluster and calculate its joint degree 
        g = powerlaw_cluster_graph(n, m, p, seed=seed)
        nkk_g = degree_mixing_dict(g,normalized=False)
        
        # generate simple undirected graph with given joint degree nkk_g
        G = joint_degree_model(nkk_g)
        nkk_G = degree_mixing_dict(G,normalized=False)
        
        #assert that the given joint degree is equal to the generated graph's joint degree
        assert_true(nkk_g == nkk_G)
