#!/usr/bin/env python
import sys
from os import path

def run():
    try:
        import nose
    except ImportError:
        raise ImportError(\
            "The nose package is needed to run the NetworkX tests.")

    print "Running NetworkX tests:"
    
#    nx_install_dir=path.join(path.dirname(__file__), path.pardir,path.pardir)
    nx_install_dir=path.join(path.dirname(__file__), path.pardir)
    argv=[' ','--verbosity=2',
          '-w',nx_install_dir,
          '--with-doctest',
          '--doctest-extension=txt',
          '--exe']
    nose.run(argv=argv)

if __name__=="__main__":
    run()

