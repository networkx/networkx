from networkx import *
import time
import sys, getopt
import pickle
import os
import json


def lap_energy(graph, degrees=None, weight='weight'):    
    if degrees is None:
        degrees = dict(graph.degree(weight=weight))
    d1 = sum(v**2 for i,v in degrees.items())
    wl = 0
    for i in graph.edges(data=True):
        wl += ((i[2].get(weight))**2)
    return [d1,2*wl]

def cw(graph, node, degrees=None, weight='weight'):
    neis = graph.neighbors(node)
    ne = graph [node]
    cw,sub = 0,0
    for i in neis:
        we = ne[i].get(weight)
        od = degrees [i]
        sub += -od**2 + (od - we)**2
        cw += we**2
    return [cw, sub]

def lap_cent_weighted(graph, nbunch=None, degrees=None, norm=False, weight='weight'):
    if nbunch is None:
        vs = graph.nodes()
    else:
        vs = nbunch
    if degrees is None:
         degrees = dict(graph.degree(weight=weight))
    if norm == True:
        fe = lap_energy(graph, degrees=degrees, weight=weight)
        den = float(fe[0]+fe[1])
    else:
        den = 1

    result = {}

    for v in vs:
        d2 = degrees [v]
        w2 = cw(graph, v, degrees=degrees, weight=weight)
        fin = d2**2 - w2[1] + 2*w2[0]
        result [v] = (fin/den)
    return result

def lap_cent_weighted_add_remove_edge(graph, add_list, remove_list, laplacian, degrees=None, norm=False, weight='weight'):

    vs = [];
    for edge in add_list:
        source = edge [0]
        vs.append(source)
        destination = edge [1]
        vs.append(destination) 
        w = edge [2]
        graph.add_edge(source, destination, weight=w)

        if source in degrees:
            degrees[source] = degrees[source] + 1
        else:
            degrees[source] = 1
        if destination in degrees:
            degrees[destination] = degrees[destination] + 1
        else:
            degrees[destination] = 1

    for edge in remove_list:
        source = edge [0]
        vs.append(source)
        destination = edge [1]
        vs.append(destination)

        if source in degrees:
            degrees[source] = degrees[source] - 1
        else:
            degrees[source] = 0
        if destination in degrees:
            degrees[destination] = degrees[destination] - 1
        else:
            degrees[destination] = 0

    vs2 = set(vs)
    for node in set(vs):
        try:
            vs2 |= set(graph.neighbors(node))
        except (networkx.exception.NetworkXError, KeyError) as e:
            continue

    for edge in remove_list:
        source = edge [0]
        destination = edge [1]
        try:
            graph.remove_edge(source, destination)
        except (networkx.exception.NetworkXError, KeyError) as e:
            continue

    if degrees is None:
         degrees = dict(graph.degree(weight=weight))

    if norm == True:
        fe = lap_energy(graph, degrees=degrees, weight=weight)
        den = float(fe[0]+fe[1])
    else:
        den = 1

    result = laplacian

    for v in vs2:    		
        try:
	        d2 = degrees [v]
	        w2 = cw(graph, v, degrees=degrees, weight=weight)
	        fin = d2**2 - w2[1] + 2*w2[0]
	        result [v] = (fin/den)
        except (networkx.exception.NetworkXError, KeyError) as e:
            continue
    return result, len(vs2)

def lap_cent(graph, nbunch=None, degrees=None, norm=False):
    if nbunch is None:
        vs = graph.nodes()
    else:
        vs = nbunch
    if degrees is None:
         degrees = dict(graph.degree(weight=None))
    if norm is True:
        den = sum(v**2 + v for i,v in degrees.items())
        den = float(den)
    else:
        den = 1

    result = {}

    for v in vs:
        neis = graph.neighbors(v)
        loc = degrees[v]
        nei = 2*sum(degrees[i] for i in neis)
        val = (loc**2 + loc + nei)/den
        result[v] = val
    return result

def lap_cent_add_remove_edge(graph, add_list, remove_list, laplacian, degrees=None, norm=False):

    vs = [];
    for edge in add_list:
        source = edge [0]
        vs.append(source)
        destination = edge [1]
        vs.append(destination)  
        graph.add_edge(source, destination)

        if source in degrees:
            degrees[source] = degrees[source] + 1
        else:
            degrees[source] = 1
        if destination in degrees:
            degrees[destination] = degrees[destination] + 1
        else:
            degrees[destination] = 1

    for edge in remove_list:
        source = edge [0]
        vs.append(source)
        destination = edge [1]
        vs.append(destination)

        if source in degrees:
            degrees[source] = degrees[source] - 1
        else:
            degrees[source] = 0
        if destination in degrees:
            degrees[destination] = degrees[destination] - 1
        else:
            degrees[destination] = 0

    vs2 = set(vs)
    for node in set(vs):
        try:
            vs2 |= set(graph.neighbors(node))
        except (networkx.exception.NetworkXError, KeyError) as e:
            continue

    for edge in remove_list:
        source = edge [0]
        destination = edge [1]
        try:
            graph.remove_edge(source, destination)
        except (networkx.exception.NetworkXError, KeyError) as e:
            continue

    if degrees is None:
         degrees = graph.degree(weight=None)
    
    if norm is True:
        den = sum(v**2 + v for i,v in degrees.items())
        den = float(den)
    else:
        den = 1       

    result = laplacian

    for v in vs2:
        try:
            neis = graph.neighbors(v)
            loc = degrees[v]
            nei = 2*sum(degrees[i] for i in neis)
            val = (loc**2 + loc + nei)/den
            result[v] = val        
        except (networkx.exception.NetworkXError, KeyError) as e:
            continue
    return result, len(vs2)

from operator import itemgetter
import copy

def main(inputfile = '', sequencedirectory = '', outputfile = '', weighted_graph = False , norm = False):
    #inputfile = ''
    #outputfile = ''
    #sequencedirectory = ''
    #weighted_graph = False
    #norm = False

    #try:
    #    opts, args = getopt.getopt(argv,"hwni:s:o:",["ifile=","sfile=","ofile="])
    #except getopt.GetoptError:
    #    print('LaplaceDynamic.py [-w] [-n] -i <inputfile> -s <sequences> -o <outputfile>')
    #    sys.exit(2)

    #for opt, arg in opts:
    #    if opt == '-h':
    #        print('LaplaceDynamic.py [-w] [-n] -i <inputfile> -s <sequences> -o <outputfile>')
    #        sys.exit()
    #    elif opt in ("-w"):
    #        weighted_graph = True        
    #    elif opt in ("-n"):
    #        norm = True
    #    elif opt in ("-i", "--ifile"):
    #        inputfile = arg
    #    elif opt in ("-s", "--sfile"):
    #        sequencedirectory = arg
    #    elif opt in ("-o", "--ofile"):
    #        outputfile = arg
    
    print('Input file is "', inputfile, ' weighted = ', weighted_graph)    

    start_time = time.time()

    G = None
    laplacian = None
    number_centralities = 0

    if weighted_graph:
        G = nx.read_weighted_edgelist(inputfile)
        degrees = dict(G.degree(weight='weight'))
    else:
        G = nx.read_edgelist(inputfile)
        degrees = dict(G.degree())


    if weighted_graph:
        laplacian = lap_cent_weighted(G, degrees=degrees, norm=norm)
    else:
        laplacian = lap_cent(G, degrees=degrees, norm=norm)

    elapsed_time = time.time() - start_time

    print ('elapsed_time: ', elapsed_time)
    print ('added_edges: ', G.number_of_edges())
    print ('number_centralities: ', G.number_of_nodes())
    print ('number_of_nodes: ', G.number_of_nodes())
    print ('number_of_edges: ', G.number_of_edges())
    #print ('laplacian: ', laplacian)

    if outputfile != '':
        print ('Output file is "', outputfile)
        with open(outputfile, 'w') as fp:
            fp.write(json.dumps(laplacian))
        #with open(outputfile, 'wb') as fp:
            #pickle.dump(laplacian, fp)
            

    for filename in os.listdir(sequencedirectory):
        if filename.startswith("a") and filename.endswith(".txt"):

            start_time = time.time()

            array_add = []
            print('Input add sequence is: ', os.path.join(sequencedirectory, filename))

            if weighted_graph:
                aux = nx.read_weighted_edgelist(os.path.join(sequencedirectory, filename))
                array_add = [list(elem) for elem in aux.edges(data='weight')]
            else:
                aux = nx.read_edgelist(os.path.join(sequencedirectory, filename))
                array_add = [list(elem) for elem in aux.edges()]

            #with open(os.path.join(sequencedirectory, filename)) as f: 
            #    for line in f:
            #        edge = line.split()
            #        array_add.append([unicode(edge[0]), unicode(edge[1])])

            array_remove = []
            filename = 'r' + filename[1:]
            print('Input remove sequence is: ', os.path.join(sequencedirectory, filename))

            if weighted_graph:
                aux = nx.read_weighted_edgelist(os.path.join(sequencedirectory, filename))
                array_remove = [list(elem) for elem in aux.edges(data='weight')]
            else:
                aux = nx.read_edgelist(os.path.join(sequencedirectory, filename))
                array_remove = [list(elem) for elem in aux.edges()]

            #with open(os.path.join(sequencedirectory, filename)) as f: 
            #    for line in f:
            #        edge = line.split()
            #        array_remove.append([unicode(edge[0]), unicode(edge[1])])

            if weighted_graph:
                laplacian, number_centralities = lap_cent_weighted_add_remove_edge(G, array_add, array_remove, laplacian, degrees=degrees, norm=norm)
            else:
                laplacian, number_centralities = lap_cent_add_remove_edge(G, array_add, array_remove, laplacian, degrees=degrees, norm=norm)

            elapsed_time = time.time() - start_time

            isolates = list(nx.isolates(G))
            for node in isolates:
                G.remove_node(node)

            print ('elapsed_time: ', elapsed_time)
            print ('added_edges: ', len(array_add) - len(array_remove))
            print ('number_centralities: ', number_centralities)
            print ('number_of_nodes: ', G.number_of_nodes())
            print ('number_of_edges: ', G.number_of_edges())
            #print ('laplacian: ', laplacian)
            continue
        else:
            print('skipping: ', os.path.join(sequencedirectory, filename))
            continue


#if __name__ == "__main__":
#    main(sys.argv[1:])


