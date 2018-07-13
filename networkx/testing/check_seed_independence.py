import random
import numpy as np

import networkx as nx
from networkx.algorithms import approximation as approx
from networkx.algorithms import threshold

print(nx.__version__)

np.random.seed(42)
np_rv = np.random.rand()
random.seed(42)
py_rv = random.random()
np.random.seed(42)
random.seed(42)

# choose to test an integer seed, or whether a single RNG can be used everywhere.
np_rng = np.random.RandomState(14)
seed = 14
#seed = np_rng

def d():
    after_np_rv = np.random.rand()
    if np_rv != after_np_rv:
        print(np_rv, after_np_rv, "don't match np!")
    np.random.seed(42)

    after_py_rv = random.random()
    if py_rv != after_py_rv:
        print(py_rv, after_py_rv, "don't match py!")
    random.seed(42)

    print("next")


n=20
m=10
k=l=2
s=v=10
p=q=p1=p2=p_in=p_out=0.4
alpha=radius=theta=0.75
sizes=(20,20,10)
colors=[1,2,3]
G=nx.barbell_graph(12,20)
deg_sequence=in_degree_sequence=w=sequence=aseq=bseq=[3,2,1,3,2,1,3,2,1,2,1,2,1]

print("starting...")
nx.maximal_independent_set(G, seed=seed);d()
nx.rich_club_coefficient(G, seed=seed, normalized=False);d()
nx.random_reference(G, seed=seed);d()
nx.lattice_reference(G, seed=seed);d()
nx.sigma(G, 10, 1, seed=seed);d()
nx.omega(G, 10, 1, seed=seed);d()
#print("out of smallworld.py")
nx.double_edge_swap(G, seed=seed);d()
#print("starting connected_double_edge_swap")
nx.connected_double_edge_swap(nx.complete_graph(9), seed=seed);d()
#print("ending connected_double_edge_swap")
nx.random_layout(G, seed=seed);d()
nx.fruchterman_reingold_layout(G, seed=seed);d()
nx.algebraic_connectivity(G, seed=seed);d()
nx.fiedler_vector(G, seed=seed);d()
nx.spectral_ordering(G, seed=seed);d()
#print('starting average_clustering')
approx.average_clustering(G, seed=seed);d()
nx.betweenness_centrality(G, seed=seed);d()
nx.edge_betweenness_centrality(G, seed=seed);d()
nx.edge_betweenness(G, seed=seed);d()
nx.approximate_current_flow_betweenness_centrality(G, seed=seed);d()
#print("kernighan")
nx.algorithms.community.kernighan_lin_bisection(G, seed=seed);d()
#nx.algorithms.community.asyn_lpa_communities(G, seed=seed);d()
nx.algorithms.tree.greedy_branching(G, seed=seed);d()
nx.algorithms.tree.Edmonds(G, seed=seed);d()
#print('done with graph argument functions')

nx.spectral_graph_forge(G, alpha, seed=seed);d()
nx.algorithms.community.asyn_fluidc(G, k, max_iter=1, seed=seed);d()
nx.algorithms.connectivity.edge_augmentation.greedy_k_edge_augmentation(G, k, seed=seed);d()
nx.algorithms.coloring.strategy_random_sequential(G, colors, seed=seed);d()

cs = ['d', 'i', 'i', 'd', 'd', 'i']
threshold.swap_d(cs, seed=seed);d()
nx.configuration_model(deg_sequence, seed=seed);d()
nx.directed_configuration_model(in_degree_sequence, in_degree_sequence, seed=seed);d()
nx.expected_degree_graph(w, seed=seed);d()
nx.random_degree_sequence_graph(sequence, seed=seed);d()
joint_degrees = {1: {4: 1},
                 2: {2: 2, 3: 2, 4: 2},
                 3: {2: 2, 4: 1},
                 4: {1: 1, 2: 2, 3: 1}}
nx.joint_degree_graph(joint_degrees, seed=seed);d()
joint_degree_sequence = [(1, 0), (1, 0), (1, 0), (2, 0), (1, 0), (2, 1), (0, 1), (0, 1)]
nx.random_clustered_graph(joint_degree_sequence, seed=seed);d()
constructor = [(3, 3, .5), (10, 10, .7)]
nx.random_shell_graph(constructor, seed=seed);d()
mapping = {1: 0.4, 2: 0.3, 3: 0.3}
nx.utils.random_weighted_sample(mapping, k, seed=seed);d()
nx.utils.weighted_choice(mapping, seed=seed);d()
nx.algorithms.bipartite.configuration_model(aseq, bseq, seed=seed);d()
nx.algorithms.bipartite.preferential_attachment_graph(aseq, p, seed=seed);d()
def kernel_integral(u, w, z):
    return (z - w)
nx.random_kernel_graph(n, kernel_integral, seed=seed);d()

sizes = [75, 75, 300]
probs = [[0.25, 0.05, 0.02],
         [0.05, 0.35, 0.07],
         [0.02, 0.07, 0.40]]
nx.stochastic_block_model(sizes, probs, seed=seed);d()
nx.random_partition_graph(sizes, p_in, p_out, seed=seed);d()

#print("starting generator functions")
threshold.random_threshold_sequence(n, p, seed=seed);d()
nx.tournament.random_tournament(n, seed=seed);d()
nx.relaxed_caveman_graph(l, k, p, seed=seed);d()
nx.planted_partition_graph(l, k, p_in, p_out, seed=seed);d()
nx.gaussian_random_partition_graph(n, s, v, p_in, p_out, seed=seed);d()
nx.gn_graph(n, seed=seed);d()
nx.gnr_graph(n, p, seed=seed);d()
nx.gnc_graph(n, seed=seed);d()
nx.scale_free_graph(n, seed=seed);d()
nx.directed.random_uniform_k_out_graph(n, k, seed=seed);d()
nx.random_k_out_graph(n, k, alpha, seed=seed);d()
N=1000
nx.partial_duplication_graph(N, n, p, q, seed=seed);d()
nx.duplication_divergence_graph(n, p, seed=seed);d()
nx.random_geometric_graph(n, radius, seed=seed);d()
nx.soft_random_geometric_graph(n, radius, seed=seed);d()
nx.geographical_threshold_graph(n, theta, seed=seed);d()
nx.waxman_graph(n, seed=seed);d()
nx.navigable_small_world_graph(n, seed=seed);d()
nx.thresholded_random_geometric_graph(n, radius, theta, seed=seed);d()
nx.uniform_random_intersection_graph(n, m, p, seed=seed);d()
nx.k_random_intersection_graph(n, m, k, seed=seed);d()

nx.general_random_intersection_graph(n, 2, [0.1, 0.5], seed=seed);d()
nx.fast_gnp_random_graph(n, p, seed=seed);d()
nx.gnp_random_graph(n, p, seed=seed);d()
nx.dense_gnm_random_graph(n, m, seed=seed);d()
nx.gnm_random_graph(n, m, seed=seed);d()
nx.newman_watts_strogatz_graph(n, k, p, seed=seed);d()
nx.watts_strogatz_graph(n, k, p, seed=seed);d()
nx.connected_watts_strogatz_graph(n, k, p, seed=seed);d()
nx.random_regular_graph(3, n, seed=seed);d()
nx.barabasi_albert_graph(n, m, seed=seed);d()
nx.extended_barabasi_albert_graph(n, m, p, q, seed=seed);d()
nx.powerlaw_cluster_graph(n, m, p, seed=seed);d()
nx.random_lobster(n, p1, p2, seed=seed);d()
nx.random_powerlaw_tree(n, seed=seed, tries=5000);d()
nx.random_powerlaw_tree_sequence(10, seed=seed, tries=5000);d()
nx.random_tree(n, seed=seed);d()
nx.utils.powerlaw_sequence(n, seed=seed);d()
nx.utils.zipf_rv(2.3, seed=seed);d()
nx.utils.discrete_sequence(n, cdistribution=[.2, .4, .5, .7, .9, 1.0], seed=seed);d()
nx.algorithms.bipartite.random_graph(n, m, p, seed=seed);d()
nx.algorithms.bipartite.gnmk_random_graph(n, m, k, seed=seed);d()
tau1=3
tau2=1.5
mu=.1
nx.algorithms.community.LFR_benchmark_graph(241, tau1, tau2, mu, \
            average_degree=5, min_community=20, seed=seed);d()

after_np_rv = np.random.rand()
if np_rv != after_np_rv:
    print(np_rv, after_np_rv, "don't match np!")
after_py_rv = random.random()
if py_rv != after_py_rv:
    print(py_rv, after_py_rv, "don't match py!")
