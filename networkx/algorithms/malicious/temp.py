import networkx as nx
from genetic_algorithm_cython import GA_C
from genetic_algorithm import GA
from graph_reduction import build_RG_from_DG
import time
import datetime
import matplotlib.pyplot as plt
from itertools import combinations

def run_test(alpha,graphs):
    ga_times = []
    fga_times = []
    n_values = []
    for i,g in enumerate(graphs):
        print(f'{g[0].number_of_nodes()+g[1].number_of_nodes()} nodes, {datetime.datetime.now()}')
        t2_start = time.time()
        GA_C(g[0],g[1],alpha)
        t2_end = round(time.time() - t2_start,3)
        fga_times.append(t2_end)
        print(f'{i} fast {t2_end}')
        n_values.append(g[0].number_of_nodes() + g[1].number_of_nodes())
        t1_start = time.time()
        GA(g[0],g[1],alpha)
        t1_end = round(time.time() - t1_start,3)
        ga_times.append(t1_end)
        print(f'{i} slow {t1_end}') 
    #n_values.sort()
    return ga_times, fga_times, n_values, alpha

def draw_results(result):
    plt.plot(result[2],result[0], label='GA')
    plt.plot(result[2],result[1], label='Fast GA')
    plt.ylabel('Run time (seconds)')
    plt.xlabel('number of vertexes')
    
    slow = round(sum(result[0]),3)
    fast = round(sum(result[1]),3)
    plt.title(f'{len(graphs)} compars, alpha = {result[3]}\n Cython is {round(slow/fast,4)} times faster')
    title = f'{datetime.datetime.now()}.png'
    print(title)
    plt.legend()
    plt.savefig(title)
    plt.cla()


g1 = build_RG_from_DG(nx.gnm_random_graph(5,8,directed = True))
g3 = build_RG_from_DG(nx.gnm_random_graph(10,19,directed = True))
g4 = build_RG_from_DG(nx.gnm_random_graph(13,20,directed = True))
g5 = build_RG_from_DG(nx.gnm_random_graph(15,25,directed = True))
g6 = build_RG_from_DG(nx.gnm_random_graph(18,28,directed = True))
g7 = build_RG_from_DG(nx.gnm_random_graph(20,31,directed = True))
g8 = build_RG_from_DG(nx.gnm_random_graph(21,36,directed = True))
g9 = build_RG_from_DG(nx.gnm_random_graph(25,35,directed = True))
g10 = build_RG_from_DG(nx.gnm_random_graph(27,41,directed = True))
g11 = build_RG_from_DG(nx.gnm_random_graph(30,40,directed = True))
g12 = build_RG_from_DG(nx.gnm_random_graph(31,45,directed = True))
g13 = build_RG_from_DG(nx.gnm_random_graph(34,53,directed = True))
g14 = build_RG_from_DG(nx.gnm_random_graph(35,55,directed = True))
g15 = build_RG_from_DG(nx.gnm_random_graph(38,60,directed = True))
g16 = build_RG_from_DG(nx.gnm_random_graph(40,62,directed = True))
g17 = build_RG_from_DG(nx.gnm_random_graph(42,68,directed = True))
g18 = build_RG_from_DG(nx.gnm_random_graph(47,71,directed = True))
g19 = build_RG_from_DG(nx.gnm_random_graph(52,80,directed = True))
g20 = build_RG_from_DG(nx.gnm_random_graph(59,87,directed = True))
g21 = build_RG_from_DG(nx.gnm_random_graph(65,100,directed = True))
g22 = build_RG_from_DG(nx.gnm_random_graph(70,115,directed = True))
g23 = build_RG_from_DG(nx.gnm_random_graph(75,135,directed = True))
g24 = build_RG_from_DG(nx.gnm_random_graph(80,160,directed = True))
g25 = build_RG_from_DG(nx.gnm_random_graph(90,200,directed = True))
g26 = build_RG_from_DG(nx.gnm_random_graph(100,220,directed = True))
g27 = build_RG_from_DG(nx.gnm_random_graph(115,250,directed = True))
g28 = build_RG_from_DG(nx.gnm_random_graph(130,290,directed = True))
g29 = build_RG_from_DG(nx.gnm_random_graph(150,330,directed = True))
g30 = build_RG_from_DG(nx.gnm_random_graph(160,380,directed = True))



graphs = [g9,g10,g3,g4,g5,g6,g7,g8,g11,g12,g13,g14,g15,g16,g17]#g18,g19,g20]
graphs = list(combinations(graphs,2))
sorted_graphs = sorted(graphs, key=lambda x:(x[0].number_of_nodes() + x[1].number_of_nodes()))
result = run_test(3,sorted_graphs)

draw_results(result)
