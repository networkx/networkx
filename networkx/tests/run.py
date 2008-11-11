#!/usr/bin/env python
from os import path
import sys
from nose.config import Config

def run(args=None):
    import networkx
    path=networkx.__path__
#    config = Config()
    test_suite=None
    try:
        import nose
    except ImportError:
        print """nose not found, test option not available,
http://somethingaboutorange.com/mrl/projects/nose""" 
        sys.exit(1)
    print "path",path
    print args
#    print "config",config
#    nose.run(defaultTest=path,config=config)

    nose.run(argv=args)

if __name__ == "__main__":
    import sys
    print sys.argv
    run(sys.argv)
