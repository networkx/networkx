#!/usr/bin/env python

from glob import glob
import os
for filename in glob('*.txt'):
    basename=os.path.splitext(filename)[0]  # get extension
    print filename,basename+'.html'
    os.system("rst2html.py %s > %s.html"%(filename,basename))

os.system("epydoc -v --docformat=restructuredtext -o reference networkx")
