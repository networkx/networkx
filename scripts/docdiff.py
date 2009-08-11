#!/usr/bin/env python
import inspect, sys
from difflib import unified_diff

def named_methods(class1):
    result={}
    for m in dir(class1):
        item=eval( '.'.join([class1.__module__, class1.__name__, m]) )
        if inspect.ismethod(item): 
            result[m]=DocBlock(item)
    return result

def methods_in_common(class1,class2):
    m1=named_methods(class1)
    m2=named_methods(class2)
    return (set(m1) & set(m2), m1, m2)

def methods_not_in_common(class1,class2):
    m1=set(named_methods(class1))
    m2=set(named_methods(class2))
    return m1.symmetric_difference(m2)


class DocBlock(object):
    """An object to hold docstrings and code snippets for an object."""
    def __init__(self, obj):
        self.name=obj.__name__
        self.filename=inspect.getsourcefile(obj)
        codelines, lineno=inspect.getsourcelines(obj)
        newcodelines=[]
        ccc=iter(codelines)
        for c in ccc:
            while c[-2:]=='\\\n':
                c=c[:-2]+ccc.next()
            newcodelines.append(c.strip('\n'))
        codelines=newcodelines
        self.sig = codelines[0]
        self.lineno = lineno
        self.obj = obj
        # docstring
        doc = obj.__doc__
        if doc is None:
            self.docstring = []
            self.margin = 0
            return
        docstring = doc.split('\n') 
        # find margin for docstring
        if len(docstring)==1:
            # one line docstring
            line=docstring[0]
            cline=codelines[1]
            margin = len(cline) - len(cline.lstrip())
            docstring[0] = ' '*margin +'"""'+ line +'"""'
        else:
            # multiline docstring
            margin = sys.maxint
            for line in docstring[1:]:
                content = len(line.lstrip())
                if content:
                    indent = len(line) - content
                    margin = min(margin, indent)
            if margin == sys.maxint:
                margin=0
            self.margin=margin
            docstring[0] = ' '*margin +'"""'+ docstring[0]
            docstring[-1] = docstring[-1] +'"""'
        if codelines[1:len(docstring)+1] != docstring:
            print "Something is funny with the __doc__ attribute for %s."%self.name
            print "Perhaps it was added after defined by original source code?"""
            print [(u,v) for u,v in zip(codelines[1:len(docstring)+1],docstring) if u!=v]
#            print "Source Code:"
#            print codelines[1:len(docstring)+1]
#            print "\n".join(codelines[1:len(docstring)+1])
#            print
#            print "__doc__: (margin=%i)"%margin
#            print docstring
#            print "\n".join(docstring)
            raise ValueError("Docstring for %s doesn't match source code docstring."%self.name)
        self.docstring=docstring
        self.codelines=codelines

    def get_doc_diff(self, other):
        """Return the diff of this object's docstring with another.""" 
        docdiff=unified_diff(self.docstring, \
                other.docstring,\
                lineterm='', \
                n=5, \
                fromfile=self.filename, tofile=other.filename)
        docdiff=list(docdiff)
        return docdiff

    def get_source_diff(self, other):
        """Return diff comparing two objects with line numbers adjusted for source files."""
        docdiff = self.get_doc_diff(other)
        newdiff=[]
        for line in docdiff:
            if line[:2]=='@@' and line[-2:]=='@@': 
                # pull out line numbers from diff
                ol,os,nl,ns=[int(n) for ss in line[3:-3].split(' ') \
                                    for n in ss.split(',')]
                # If first line in docstring, add signature
                if ol==-1 and self.sig == other.sig:
                    ol=self.lineno
                    nl=nl+other.lineno-1
                    os+=1
                    ns+=1
                    newline = '@@ -%i,%i +%i,%i @@'%(ol,os,nl,ns)
                    newdiff.append(newline)
                    newdiff.append(' '+self.sig)
                else:
                    ol = abs(ol)+self.lineno
                    nl += other.lineno
                    if os==0:
                        ol-=1
                    if ns==0:
                        nl-=1
                    newline = '@@ -%i,%i +%i,%i @@'%(ol,os,nl,ns)
                    newdiff.append(newline)
            else:
                newdiff.append(line)
        return newdiff

    def showme(self):
        print "name:",self.name
        print "filename:",self.filename
        print "docstring:",self.docstring
        print "lineno:",self.lineno
        print "object:",self.obj


def create_method_diff(method1, method2, output=True, exclude=None):
    bigdiff = report_method_diff(method1, method2, False, exclude)
    bigdiff=[ line for line in bigdiff if line[:5]!="*****" ]
    if output:
        print '\n'.join(bigdiff)
    return bigdiff

def report_method_diff(method1, method2, output=True, exclude=None):
    if exclude is None:
        exclude=[]
    assert inspect.ismethod(method1)
    assert inspect.ismethod(method2)
    M1=DocBlock(method1)
    file1=M1.filename
    M2=DocBlock(method2)
    file2=M2.filename
    # diff method docs
    bigdiff=["************** Report of docdiff for:",\
             "************** "+M1.name,\
             "************** "+M2.name,\
             "***************************************",\
             "***** Method Document String",\
             "********************************"]
    bigdiff.extend( M1.get_source_diff(M2) )
    if output:
        print '\n'.join(bigdiff)
    return bigdiff


def create_class_diff(class1, class2, output=True, exclude=None):
    bigdiff = report_class_diff(class1, class2, False, exclude)
    bigdiff=[ line for line in bigdiff if line[:5]!="*****" ]
    if output:
        print '\n'.join(bigdiff)
    return bigdiff


def report_class_diff(class1, class2, output=True, exclude=None):
    if exclude is None:
        exclude=[]
    assert inspect.isclass(class1)
    assert inspect.isclass(class2)
    C1=DocBlock(class1)
    file1=C1.filename
    C2=DocBlock(class2)
    file2=C2.filename
    # diff class docs
    bigdiff=["************** Report of docdiff for:",\
             "************** "+C1.name,\
             "************** "+C2.name,\
             "***************************************",\
             "***** Class Document String",\
             "********************************"]
    bigdiff.extend( C1.get_source_diff(C2) )
    # now diff methods
    bigdiff.extend( ["**********************************",\
             "***** Class Methods",\
             "*****************************"] )
    mic,mc1,mc2 = methods_in_common(class1,class2)
    mic=sorted( (mc1[m].lineno,m) for m in mic )
    for i,m in mic:
        if m in exclude: continue
        mc1_block=mc1[m]
        mc2_block=mc2[m]
        if mc1_block.filename == file1 and \
                mc2_block.filename == file2:
            newdiff = mc1_block.get_source_diff(mc2_block)
            bigdiff.append("******** Method: "+m)
            bigdiff.extend(newdiff[2:])
            bigdiff.append("***************")
    if output:
        print '\n'.join(bigdiff)
    return bigdiff

    

if __name__ == '__main__':
    import sys
    import networkx
    usage= """Usage:
    docdiff.py object1 object2 [-e|--exclude method1 [method2 ...]]

    Create a report of the docstring differences between two 
    classes or methods.  If classes, the methods of the classes
    will be compared as well, excluding any methods listed after 
    the optional exclude switch.

    To use the results as a diff file, it may be useful to
    pipe through grep as:
    cat output | grep -v '^\*\*\*\*\*' >diff_file
    """
    nargin=len(sys.argv)
    if nargin<3 or (nargin>3 and sys.argv[3] not in ['-e','--exclude']):
        print usage
        sys.exit()
    if nargin>3:
        exclude=sys.argv[4:]
    else:
        exclude=[]
#    exclude=['neighbors','neighbors_iter',\
#            'delete_node','delete_nodes_from',\
#            'delete_edge','delete_edges_from',\
#            'out_edges','out_edges_iter',\
#            ]
    obj1=eval(sys.argv[1])
    obj2=eval(sys.argv[2])
    if inspect.isclass(obj1) and inspect.isclass(obj2):
        report_class_diff(obj1,obj2,exclude=exclude)
    elif inspect.ismethod(obj1) and inspect.ismethod(obj2):
        report_method_diff(obj1,obj2,exclude=exclude)
    else:
        print
        print "Objects were not recognized as classes or methods."
        print "Did you forget to capitalize the class name correctly?"
        print 
        print usage
