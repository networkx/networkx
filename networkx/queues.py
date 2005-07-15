"""
Helper queues for use in graph searching.

 - LIFO:          Last in first out queue (stack)
 - FIFO:          First in first out queue
 - Priority(fcn): Priority queue with items are sorted by fcn
 - Random:        Random queue

 - q.append(item)  -- add an item to the queue
 - q.extend(items) -- equivalent to: for item in items: q.append(item)
 - q.pop()         -- return the top item from the queue
 - len(q)          -- number of items in q (also q.__len())
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-03-30 16:56:28 -0700 (Wed, 30 Mar 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 911 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import bisect
import random

class LIFO(list):
    """
    """
    def __init__(self):
        list.__init__(self)

class FIFO(list):
    """
    """
    def __init__(self):
        list.__init__(self)
    def pop(self):
        item = list.pop(self,0)
        return item

class Random(list):
    """
    """
    def __init__(self):
        list.__init__(self)
    def pop(self):
        index=random.randint(0,len(self)-1)
        item = list.pop(self,index)
        return item


class Priority:
    """
    """
    def __init__(self, f=lambda x: x):
        self.L=[]
        self.f=f
    def append(self, item):
        bisect.insort(self.L, (self.f(item), item))
    def __len__(self):
        return len(self.L)
    def extend(self, items):
        for item in items: self.append(item)
    def pop(self):
        return self.L.pop()[1]
    def smallest(self):
        return self.L.pop(0)[1]


# search queue types
# for the generic search class we need an "update" function so let's
# make a new class that adds an update method to the Queues classes

class DFS(LIFO):
    """
    Depth first search queue
    """
    def __init__(self):
        LIFO.__init__(self)

    def update(self, item):
        # DFS update rule for queue (self is the queue)
        # Find the edge on the fringe with same target and delete
        (source, target)=item 
        olditem=[(u,v) for (u,v) in self if v==target][0]
        list.remove(self,olditem)
        list.append(self,item)


class BFS(FIFO):
    """
    Breadth first search queue
    """
    def __init__(self):
        FIFO.__init__(self)

    def update(self, item):
        # BFS update rule for queue, do nothing
        pass


class RFS(Random):
    """
    Random search queue
    """
    def __init__(self):
        Random.__init__(self)

    def update(self, item):
        # RFS update rule for queue, do nothing
        pass

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('../tests/queues.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
