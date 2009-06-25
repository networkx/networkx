#!/usr/bin/env python
"""
generate the rst files for the examples by iterating over the networkx examples
"""
# This code was developed from the Matplotlib gen_rst.py module
# and is distributed with the same license as Matplotlib
import os, glob

import os
import re
import sys
#fileList = []
#rootdir = '../../examples'



def out_of_date(original, derived):
    """
    Returns True if derivative is out-of-date wrt original,
    both of which are full file paths.

    TODO: this check isn't adequate in some cases.  Eg, if we discover
    a bug when building the examples, the original and derived
    will be unchanged but we still want to fource a rebuild.  We can
    manually remove from _static, but we may need another solution
    """
    return (not os.path.exists(derived) or
            os.stat(derived).st_mtime < os.stat(original).st_mtime)

def main(exampledir,sourcedir):    

    noplot_regex = re.compile(r"#\s*-\*-\s*noplot\s*-\*-")

    datad = {}
    for root, subFolders, files in os.walk(exampledir):
        for fname in files:
            if ( fname.startswith('.') or fname.startswith('#') or fname.startswith('_') or
                 fname.find('.svn')>=0 or not fname.endswith('.py') ):
                continue

            fullpath = os.path.join(root,fname)
            contents = file(fullpath).read()
            # indent
            relpath = os.path.split(root)[-1]
            datad.setdefault(relpath, []).append((fullpath, fname, contents))

    subdirs = datad.keys()
    subdirs.sort()
    output_dir=os.path.join(sourcedir,'examples')
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    fhindex = file(os.path.join(sourcedir,'examples','index.rst'), 'w')
    fhindex.write("""\
.. _examples-index:

*****************
NetworkX Examples
*****************

.. only:: html

    :Release: |version|
    :Date: |today|

.. toctree::
    :maxdepth: 2

""")

    for subdir in subdirs:
        output_dir= os.path.join(sourcedir,'examples',subdir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        static_dir = os.path.join(sourcedir, 'static', 'examples')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)


        subdirIndexFile = os.path.join(subdir, 'index.rst')
        fhsubdirIndex = file(os.path.join(output_dir,'index.rst'), 'w')
        fhindex.write('    %s\n\n'%subdirIndexFile)
        #thumbdir = '../_static/plot_directive/mpl_examples/%s/thumbnails/'%subdir
        #for thumbname in glob.glob(os.path.join(thumbdir,'*.png')):
        #    fhindex.write('    %s\n'%thumbname)

        fhsubdirIndex.write("""\
.. _%s-examples-index:


##############################################
%s
##############################################

.. only:: html

    :Release: |version|
    :Date: |today|

.. toctree::
    :maxdepth: 1

"""%(subdir, subdir.title()))


        data = datad[subdir]
        data.sort()

        #parts = os.path.split(static_dir)
        #thumb_dir = ('../'*(len(parts)-1)) + os.path.join(static_dir, 'thumbnails')

        for fullpath, fname, contents in data:
            basename, ext = os.path.splitext(fname)
            static_file = os.path.join(static_dir, fname)
            #thumbfile = os.path.join(thumb_dir, '%s.png'%basename)
            #print '    static_dir=%s, basename=%s, fullpath=%s, fname=%s, thumb_dir=%s, thumbfile=%s'%(static_dir, basename, fullpath, fname, thumb_dir, thumbfile)

            rstfile = '%s.rst'%basename
            outfile = os.path.join(output_dir, rstfile)

            fhsubdirIndex.write('    %s\n'%rstfile)

            if (not out_of_date(fullpath, static_file) and
                not out_of_date(fullpath, outfile)):
                continue

            print '%s/%s'%(subdir,fname)

            fhstatic = file(static_file, 'w')
            fhstatic.write(contents)
            fhstatic.close()

            fh = file(outfile, 'w')
            fh.write('.. _%s-%s:\n\n'%(subdir, basename))
            base=fname.partition('.')[0]
            title = '%s'%(base.replace('_',' ').title())


            #title = '<img src=%s> %s example code: %s'%(thumbfile, subdir, fname)


            fh.write(title + '\n')
            fh.write('='*len(title) + '\n\n')

            pngname=base+".png"
            png=os.path.join(static_dir,pngname)
            linkname = os.path.join('..', '..', 'static', 'examples')
            if os.path.exists(png):
                fh.write('.. image:: %s \n\n'%os.path.join(linkname,pngname))
            linkname = os.path.join('..', '..', '_static', 'examples')
            fh.write("[`source code <%s>`_]\n\n::\n\n" % os.path.join(linkname,fname))

            # indent the contents
            contents = '\n'.join(['    %s'%row.rstrip() for row in contents.split('\n')])
            fh.write(contents)

    #        fh.write('\n\nKeywords: python, matplotlib, pylab, example, codex (see :ref:`how-to-search-examples`)')
            fh.close()

        fhsubdirIndex.close()

    fhindex.close()

if __name__ == '__main__':
    import sys
    try:
        arg0,arg1,arg2=sys.argv[:3]
    except:
        arg0=sys.argv[0]
        print """
Usage:  %s exampledir sourcedir 

    exampledir: a directory containing the python code for the examples.
    sourcedir: a directory to put the generated documentation source for these examples.

        """%arg0
    else:
        main(arg1,arg2)

