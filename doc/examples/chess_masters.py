#!/usr/bin/env python

#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

"""
This example shows the usefulness
of the XDiGraph class (used here with 
multiple edges (multiedges=True)).

The function chess_pgn_graph reads a
collection of chess matches stored in 
the specified PGN file (PGN =
"Portable Game Notation")
Here the (compressed) default file ---
 chess_masters_WCC.png.bz2 ---
contains all 685 World Chess matches from 
1886 - 1985.

(data from 
http://chessproblem.my-free-games.com/chess/games/Download-PGN.php)

The chess_pgn_graph() function returns an XDiGraph with 
multiple edges but no self-loops where 
each node is a string representing a 
chess master. Each edge is directed from 
white to black and contains selected game info.

"""


from networkx import *

# tag names specifying what game info should be 
# stored in the dict on digraph edge
game_details=[
              "Event", 
              "Date", 
              "Result", 
              "ECO",
              "Site"
             ]

def chess_pgn_graph(pgn_file="chess_masters_WCC.pgn.bz2"):
    """Read chess games in pgn format in pgn_file.
    
    Filenames ending in .gz or .bz2 will be uncompressed.
    
    Return the XDiGraph of players connected by a chess game.
    Edges contain game data in a dict.

    """
    try:# use networkx.io._get_fh to uncompress
        # pgn file if required
        datafile=io._get_fh(pgn_file,mode='rb')
    except IOError:
        print "Could not read file %s."%(pgn_file)
        raise
    G=XDiGraph(multiedges=True)
    game_info={}
    for line in datafile.read().splitlines():
        # check for tag pairs
        if len(line)>0 and line[0]=='[':
           line=line[1:-1] # remove extra quotes
	   tag = line.split()[0]
           value=line[len(tag)+2:-1]
	   if tag=='White':
              white=value.split(',')[0]
	   elif tag=='Black':
              black=value.split(',')[0]
           elif tag in game_details:
	      game_info[tag]=value
        # empty line after tag set indicates 
        # we finished reading game info
        elif len(line)==0: # empty line
	     if len(game_info)>0: # assume we just read a game
                 G.add_edge(white, black, game_info)
		 game_info={}
    return G


if __name__ == '__main__':
    from networkx import *
    try:
	import pylab as P
    except:
	print "pylab not found: see https://networkx.lanl.gov/Drawing.html for info"
	raise 

    G=chess_pgn_graph()
    ngames=G.number_of_edges()
    nplayers=G.number_of_nodes()
    # edge data are in e[2] for each edge e in G
    # (in this case a dict), for example:
    sites=set([e[2]['Site'] for e in G.edges()]) 
    openings=set([e[2]['ECO'] for e in G.edges()])
    print "Loaded %d chess games between %d players\n"\
                   % (ngames,nplayers)

    # identify connected components
    # of the undirected version
    Gcc=connected_component_subgraphs(G.to_undirected())
    if len(Gcc)>1:
        print "Note the disconnected component consisting of:"
        print Gcc[1].nodes()    

    # find all games with ECO B97 opening
    print "\nThe following games used the Sicilian opening"
    print "with the Najdorff 7...Qb6 variation.\n"
    # each edge e is an arc from e[0] to e[1]
    # with the dict of game data stored in e[2]
    for e in G.edges():
	if e[2]['ECO']=='B97':
	   print e[0],"vs",e[1]
           for k,v in e[2].items():
               print "   ",k,": ",v
           print "\n"



    try: # drawing
        pos=graphviz_layout(G)	
	# nodes
	bluenodes=[n for n in Gcc[0]]
	othernodes=[n for n in G if n not in bluenodes]
	draw_networkx_nodes(G,pos,
                         nodelist=bluenodes,
                         node_color='b',
                         node_shape='s',
                         alpha=0.3,
                         node_size=600,
                         )
	draw_networkx_nodes(G,pos,
                         nodelist=othernodes,
                         node_color='r',
                         node_shape='s',
                         alpha=0.3,
                         node_size=600,
                         )  
	draw_networkx_edges(G,pos,
                         edge_color='b',
                         alpha=0.01,
                         width=6.0
                         )
	draw_networkx_labels(G,pos,
                         font_size='larger',
                         font_famile='cursive',
                         font_weight='bold'
                         )        
 
	P.title("World Chess Championship Games: 1886 - 1985")
	# turn off x and y axes labels in pylab
	P.xticks([])
	P.yticks([])

	P.savefig("chess_masters_graph.png")
        print "Wrote chess_masters_graph.png"
        P.show() # display
    except:
	print "Unable to draw: cannot find graphviz or pylab"
