# -*- coding: utf-8 -*-
#
# priorityq: An object-oriented priority queue with updatable priorities.
#
# Copyright 2018 Edward L. Platt
#
# This file is part of NetworkX
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
#
# Authors:
#   Edward L. Platt <ed@elplatt.com>


from networkx.utils.mapped_queue import MappedQueue


class TestMappedQueue(object):

    def setup(self):
        pass

    def _check_map(self, q):
        d = dict((elt, pos) for pos, elt in enumerate(q.h))
        assert d == q.d

    def _make_mapped_queue(self, h):
        q = MappedQueue()
        q.h = h
        q.d = dict((elt, pos) for pos, elt in enumerate(h))
        return q

    def test_heapify(self):
        h = [5, 4, 3, 2, 1, 0]
        q = self._make_mapped_queue(h)
        q._heapify()
        self._check_map(q)

    def test_init(self):
        h = [5, 4, 3, 2, 1, 0]
        q = MappedQueue(h)
        self._check_map(q)

    def test_len(self):
        h = [5, 4, 3, 2, 1, 0]
        q = MappedQueue(h)
        self._check_map(q)
        assert len(q) == 6

    def test_siftup_leaf(self):
        h = [2]
        h_sifted = [2]
        q = self._make_mapped_queue(h)
        q._siftup(0)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftup_one_child(self):
        h = [2, 0]
        h_sifted = [0, 2]
        q = self._make_mapped_queue(h)
        q._siftup(0)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftup_left_child(self):
        h = [2, 0, 1]
        h_sifted = [0, 2, 1]
        q = self._make_mapped_queue(h)
        q._siftup(0)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftup_right_child(self):
        h = [2, 1, 0]
        h_sifted = [0, 1, 2]
        q = self._make_mapped_queue(h)
        q._siftup(0)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftup_multiple(self):
        h = [0, 1, 2, 4, 3, 5, 6]
        h_sifted = [1, 3, 2, 4, 0, 5, 6]
        q = self._make_mapped_queue(h)
        q._siftup(0)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftdown_leaf(self):
        h = [2]
        h_sifted = [2]
        q = self._make_mapped_queue(h)
        q._siftdown(0)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftdown_single(self):
        h = [1, 0]
        h_sifted = [0, 1]
        q = self._make_mapped_queue(h)
        q._siftdown(len(h) - 1)
        assert q.h == h_sifted
        self._check_map(q)

    def test_siftdown_multiple(self):
        h = [1, 2, 3, 4, 5, 6, 7, 0]
        h_sifted = [0, 1, 3, 2, 5, 6, 7, 4]
        q = self._make_mapped_queue(h)
        q._siftdown(len(h) - 1)
        assert q.h == h_sifted
        self._check_map(q)

    def test_push(self):
        to_push = [6, 1, 4, 3, 2, 5, 0]
        h_sifted = [0, 2, 1, 6, 3, 5, 4]
        q = MappedQueue()
        for elt in to_push:
            q.push(elt)
        assert q.h == h_sifted
        self._check_map(q)

    def test_push_duplicate(self):
        to_push = [2, 1, 0]
        h_sifted = [0, 2, 1]
        q = MappedQueue()
        for elt in to_push:
            inserted = q.push(elt)
            assert inserted == True
        assert q.h == h_sifted
        self._check_map(q)
        inserted = q.push(1)
        assert inserted == False

    def test_pop(self):
        h = [3, 4, 6, 0, 1, 2, 5]
        h_sorted = sorted(h)
        q = self._make_mapped_queue(h)
        q._heapify()
        popped = []
        for elt in sorted(h):
            popped.append(q.pop())
        assert popped == h_sorted
        self._check_map(q)

    def test_remove_leaf(self):
        h = [0, 2, 1, 6, 3, 5, 4]
        h_removed = [0, 2, 1, 6, 4, 5]
        q = self._make_mapped_queue(h)
        removed = q.remove(3)
        assert q.h == h_removed

    def test_remove_root(self):
        h = [0, 2, 1, 6, 3, 5, 4]
        h_removed = [1, 2, 4, 6, 3, 5]
        q = self._make_mapped_queue(h)
        removed = q.remove(0)
        assert q.h == h_removed

    def test_update_leaf(self):
        h = [0, 20, 10, 60, 30, 50, 40]
        h_updated = [0, 15, 10, 60, 20, 50, 40]
        q = self._make_mapped_queue(h)
        removed = q.update(30, 15)
        assert q.h == h_updated

    def test_update_root(self):
        h = [0, 20, 10, 60, 30, 50, 40]
        h_updated = [10, 20, 35, 60, 30, 50, 40]
        q = self._make_mapped_queue(h)
        removed = q.update(0, 35)
        assert q.h == h_updated
