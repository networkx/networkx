#!/usr/bin/env python
# convert adjacency list to edge list
import fileinput
from string import split

for line in fileinput.input():
    if line.startswith("#"):
        continue
    v=split(line)
    source=v.pop(0)
    for target in v:
        print source,target

        
    
