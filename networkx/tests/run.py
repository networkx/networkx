#!/usr/bin/env python
from os import path
import sys


def run():
    test_suite=None
    try:
        import nose
    except ImportError:
        print """nose not found, test option not available,
http://somethingaboutorange.com/mrl/projects/nose""" 
        sys.exit(1)
    nose.run()

if __name__ == "__main__":
    run()
