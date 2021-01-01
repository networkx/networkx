"""
======
plotly
======

plotly (https://plotly.com/python/) is a Python plotting library.
"""

import networkx as nx
import plotly.graph_objects as go

# %%
# Read and get layout
# -------------------

G = nx.read_gml("/home/jarrod/netscience.gml")
pos = nx.random_layout(G, seed=42)
# pos = nx.kamada_kawai_layout(G)

# %%
# Get node and edge data for plotly
# ---------------------------------

node_x = [pos[k][0] for k in G]
node_y = [pos[k][1] for k in G]
node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    hoverinfo="text",
    mode="markers",
    marker={
        "symbol": "circle-dot",
        "size": 5,
        "color": "#6959CD",
        "line": {"color": "rgb(50,50,50)", "width": 0.5},
    },
    text=list(G.nodes),
)

edge_x = []
edge_y = []
for edge in G.edges:
    edge_x += [pos[edge[0]][0], pos[edge[1]][0], None]
    edge_y += [pos[edge[0]][1], pos[edge[1]][1], None]
edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    line={"color": "rgb(210,210,210)", "width": 1},
    hoverinfo="none",
    mode="lines",
)

# %%
# Plot
# ----

axis = {
    "showline": False,  # hide axis line, grid, ticklabels and  title
    "zeroline": False,
    "showgrid": False,
    "showticklabels": False,
    "title": "",
}

layout = go.Layout(
    title="Coauthorship network of scientists working on network theory and experiment"
    + "<br> Data source: <a href='http://networkdata.ics.uci.edu/data/netscience/netscience.gml'>"
    + "http://networkdata.ics.uci.edu/data/netscience/netscience.gml</a>",
    font={"size": 16},
    showlegend=False,
    xaxis=axis,
    yaxis=axis,
    margin={"b": 85, "l": 40, "r": 40, "t": 100},
    hovermode="closest",
    annotations=[
        {
            "showarrow": False,
            "text": "This networkx.Graph has the Kamada-Kawai layout",
            "xref": "paper",
            "yref": "paper",
            "x": 0,
            "y": -0.1,
            "xanchor": "left",
            "yanchor": "bottom",
            "font": {"size": 14},
        }
    ],
)

fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
fig
# fig.show()
# fig.write_file("fig.png")
