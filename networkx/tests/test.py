#!/usr/bin/env python
import sys
import os
import subprocess

def run():
    """Run NetworkX tests.
    
    """
    try:
        import nose
    except ImportError:
        raise ImportError(\
            "The nose package is needed to run the NetworkX tests.")

    import networkx
    olddir = os.path.abspath(os.path.curdir)
    newdir = os.path.dirname(networkx.__file__)
    try:
        # Go to where NetworkX was imported
        os.chdir(newdir)
        # We still have trouble running nose.run().
        # Instead, we call nosetests via subprocess.
        try:
            subprocess.call(['nosetests'])
        except OSError:
            print "'nosetests' must be in PATH"
    finally:
        os.chdir(olddir)

if __name__=="__main__":
    run()

