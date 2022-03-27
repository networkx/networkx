"""
======================
DAG in Various Layouts
======================

Creates a Directed Acyclic Graph and shows the Graph in various layouts. 
This can give an idea as to which layout can be chosen for these types of datasets.

"""

import networkx as nx
import matplotlib.pyplot as plt

def DAG():
    G = nx.DiGraph()
    G.add_edges_from([("f", "a"), ("a", "b"), ("a", "e"), ("b", "c"), ("b", "d"), ("d", "e"), ("f","c"), ("f", "g"),("h", "f")])
    return(G)

def visualise(G):
    fig, axes = plt.subplots(3, 3, figsize = (25, 12))
    ax = axes.flatten()
    layouts = [None, nx.circular_layout(G),nx.kamada_kawai_layout(G),nx.planar_layout(G),nx.random_layout(G),nx.shell_layout(G),nx.spring_layout(G),
              nx.spectral_layout(G), nx.spiral_layout(G)]
    titles = ["No Layout", "Circular Layout", "Kamada Kawai Layout", "Planar Layout", "Random Layout", "Shell Layout", "Spring Layout", "Spectral Layout", "Spiral Layout"]
    for i in range(9):
        pos = layouts[i]
        nx.draw_networkx(G, ax = ax[i], with_labels = True, node_color = 'maroon' , font_color ='white', node_size = 500, font_size = 14, pos = pos)
        ax[i].set_title(titles[i])
    plt.show()
    
G = DAG()
visualise(G)