*********************************
Version 1.9 notes and API changes
*********************************

This page reflects API changes from networkx-1.8 to networkx-1.9.

Please send comments and questions to the networkx-discuss mailing list:
http://groups.google.com/group/networkx-discuss .

* The functions in the components package algorithms/components/ such as, connected_components, connected_components_subgraph, and similar, now return generators instead of lists.  In order to recover the earlier behavior use e.g. list(connected_components(G)).



