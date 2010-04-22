#!/usr/bin/env python
import sys
from os import path

def run(verbosity=1):
    """Run NetworkX tests.

    Parameters
    ----------
    verbosity: integer, optional
      Level of detail in test reports.  Higher numbers provide  more detail.  
    """
    try:
        import nose
    except ImportError:
        raise ImportError(\
            "The nose package is needed to run the NetworkX tests.")

    sys.stderr.write("Running NetworkX tests:")
    
    nx_install_dir=path.join(path.dirname(__file__), path.pardir)
    argv=[' ','--verbosity=%d'%verbosity,
          '-w',nx_install_dir,
          '--with-doctest',
          '--doctest-extension=txt',
          '--exe']
    nose.run(argv=argv)

if __name__=="__main__":
    run()

