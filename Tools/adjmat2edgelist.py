#!/usr/bin/env python
# convert adjacency matrix of 0 and not 0 to edge list
import fileinput
from string import split

row=0
for line in fileinput.input():
    if line.startswith("#"):
        continue
    vlist=split(line)
    for col in xrange(0,len(vlist)):
        if vlist[col]!="0":
            print row,col
    row=row+1


        
    
