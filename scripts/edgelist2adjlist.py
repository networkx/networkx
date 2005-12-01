#!/usr/bin/env python
# convert edge list to adjacency list
import fileinput
from string import join,split

alist={}
for line in fileinput.input():
    if line.startswith("#"):
        continue
    vlist=split(line)
    if len(vlist) != 2:
        print >> sys.stderr, "skipping line, possible bad file", line
        continue
    (source,target)=vlist
    if alist.has_key(source):
        alist[source].append(target)
    else:
        alist[source]=[target]

for a in alist:
    print a,join(alist[a]," ")


        
    
