#!/usr/bin/env python
# generate a thumbnail gallery of examples
template = """\
{%% extends "layout.html" %%}
{%% set title = "Gallery" %%}


{%% block body %%}

<h3>Click on any image to see source code</h3>
<br/>

%s
{%% endblock %%}
"""
link_template = """\
<a href="%s"><img src="%s" border="0" alt="%s"/></a>
"""

import os, glob, re, shutil, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot
import matplotlib.image
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

examples_source_dir = '../examples/drawing'
examples_dir = 'examples/drawing'
template_dir = 'source/templates'
static_dir = 'source/static/examples'
pwd=os.getcwd()
rows = []

if not os.path.exists(static_dir):
    os.makedirs(static_dir)

os.chdir(examples_source_dir)
all_examples=sorted(glob.glob("*.py"))

# check for out of date examples
stale_examples=[]
for example in all_examples:
    png=example.replace('py','png')                             
    png_static=os.path.join(pwd,static_dir,png)
    if (not os.path.exists(png_static) or 
        os.stat(png_static).st_mtime < os.stat(example).st_mtime):
        stale_examples.append(example)

for example in stale_examples:
    print example,
    png=example.replace('py','png')                             
    matplotlib.pyplot.figure(figsize=(6,6))
    stdout=sys.stdout
    sys.stdout=open('/dev/null','w')
    try:
        execfile(example)
        sys.stdout=stdout
        print " OK"
    except ImportError,strerr:
        sys.stdout=stdout
        sys.stdout.write(" FAIL: %s\n"%strerr)
        continue
    matplotlib.pyplot.clf()
    im=matplotlib.image.imread(png)
    fig = Figure(figsize=(2.5, 2.5))
    canvas = FigureCanvas(fig)
    ax = fig.add_axes([0,0,1,1], aspect='auto', frameon=False, xticks=[], yticks
=[])
#    basename, ext = os.path.splitext(basename)
    ax.imshow(im, aspect='auto', resample=True, interpolation='bilinear')
    thumbfile=png.replace(".png","_thumb.png")
    fig.savefig(thumbfile)
    shutil.copy(thumbfile,os.path.join(pwd,static_dir,thumbfile))
    shutil.copy(png,os.path.join(pwd,static_dir,png))
    
    basename, ext = os.path.splitext(example)
    link = '%s/%s.html'%(examples_dir, basename)
    rows.append(link_template%(link, os.path.join('_static/examples',thumbfile), basename))


os.chdir(pwd)
fh = open(os.path.join(template_dir,'gallery.html'), 'w')
fh.write(template%'\n'.join(rows))
fh.close()

