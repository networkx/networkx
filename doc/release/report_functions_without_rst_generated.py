import os
import inspect
import networkx as nx

print("Run this script from the doc/ directory of the repository")
funcs = inspect.getmembers(nx, inspect.isfunction)

for n,f in funcs:
    #print(n + ": "+str(f))
    cmd = "find . -name *\."+n+".rst -print"
    #print(cmd)
    result=os.popen(cmd).read()
    #print(result)

    old_names = ('find_cores',
                 'test',
                 'edge_betweenness',
                 'betweenness_centrality_source',
                 'write_graphml_lxml',
                 'write_graphml_xml',
                 'adj_matrix',
                 'project',
                 'fruchterman_reingold_layout',
                 'node_degree_xy',
                 'node_attribute_xy',
                 'find_cliques_recursive',
                 'recursive_simple_cycles',
                 )

    if len(result) == 0 and n not in old_names:
        print("Missing file from docs:  ", n)

print("Done finding functions that are missing from the docs")
