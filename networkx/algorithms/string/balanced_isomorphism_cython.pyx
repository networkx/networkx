# distutils: language = c++
"""
This module re-implements functions in :module:`balanced_isomorphism` in cython
and obtains 25-35% speedups in common circumstances. There are likely more
speed improvements that could be made.


Issues
------
- [ ] How to deal with cython + networkx? Do we need to fix that skbuild
with pypy?


CommandLine
-----------
# Explicitly build this cython module 
# NOTE: cd to networkx repo root before running
cythonize -a -i networkx/algorithms/string/balanced_isomorphism_cython.pyx

# With xdoctest this should work if networkx is installed (and this file is
# distributed with it)
xdoctest -m networkx.algorithms.string.balanced_isomorphism _cython_lcs_backend

# Which will then let you run these examples and benchmarks
xdoctest -m networkx.algorithms.string.balanced_isomorphism_cython list
xdoctest -m networkx.algorithms.string.balanced_isomorphism_cython __doc__:0 --bench


Example
-------
>>> from networkx.algorithms.string.balanced_isomorphism_cython import _lcsi_iter_cython, IdentityDictCython
>>> from networkx.algorithms.string.balanced_isomorphism import _lcsi_iter
>>> from networkx.algorithms.string.balanced_sequence import random_balanced_sequence
>>> import operator
>>> seq1, open_to_close1 = random_balanced_sequence(300, item_type='paren')
>>> seq2, open_to_close2 = random_balanced_sequence(300, item_type='paren')
>>> open_to_close = {**open_to_close1, **open_to_close2}
>>> full_seq1 = seq1
>>> full_seq2 = seq2
>>> node_affinity = operator.eq
>>> open_to_node = IdentityDictCython()
>>> value2, best2, *_ = _lcsi_iter_cython(full_seq1, full_seq2, open_to_close, node_affinity, open_to_node)
>>> value1, best1, *_ = _lcsi_iter(full_seq1, full_seq2, open_to_close, node_affinity, open_to_node)
>>> assert value1 == value2

Benchmark
---------
>>> # xdoctest: +REQUIRES(--bench)
>>> # xdoctest: +REQUIRES(module:timerit)
>>> print((chr(10) * 3)+ ' --- BEGIN BENCHMARK ---')
>>> import timerit
>>> from networkx.algorithms.string import balanced_sequence as bseq
>>> from networkx.algorithms.string import balanced_isomorphism as biso
>>> seq_len = 200
>>> seq1, open_to_close1 = bseq.random_balanced_sequence(seq_len, item_type='paren', container_type='str')
>>> seq2, open_to_close2 = bseq.random_balanced_sequence(seq_len, item_type='paren', container_type='str')
>>> open_to_close = {**open_to_close1, **open_to_close2}
>>> n = 1
>>> ti = timerit.Timerit(n, bestof=max(2, n), verbose=2)
>>> for timer in ti.reset('impl=iter-cython'):
>>>     with timer:
>>>         biso.longest_common_balanced_isomorphism(seq1, seq2, open_to_close, impl='iter-cython')
>>> for timer in ti.reset('impl=iter'):
>>>     with timer:
>>>         biso.longest_common_balanced_isomorphism(seq1, seq2, open_to_close, impl='iter')
>>> print(ti.summary())

>>> seq_len = 1000
>>> seq1, open_to_close1 = bseq.random_balanced_sequence(seq_len, item_type='chr')
>>> seq2, open_to_close2 = bseq.random_balanced_sequence(seq_len, item_type='chr')
>>> open_to_close = {**open_to_close1, **open_to_close2}
>>> n = 1
>>> ti = timerit.Timerit(n, bestof=max(2, n), verbose=2)
>>> # Following specs are for my machine
>>> for timer in ti.reset('impl=iter-cython'):
>>>     with timer:
>>>         biso.longest_common_balanced_isomorphism(seq1, seq2, open_to_close, impl='iter-cython')
>>> for timer in ti.reset('impl=iter'):
>>>     with timer:
>>>         biso.longest_common_balanced_isomorphism(seq1, seq2, open_to_close, impl='iter')
>>> print(ti.summary())
"""
cimport cython



@cython.boundscheck(False)  # Deactivate bounds checking
def _lcsi_iter_cython(full_seq1, full_seq2, open_to_close, node_affinity, open_to_node):
    """
    Cython implementation of :func:`_lcsi_iter`.
    """
    all_decomp1 = generate_all_decomp_nocat_cython(full_seq1, open_to_close, open_to_node)
    all_decomp2 = generate_all_decomp_nocat_cython(full_seq2, open_to_close, open_to_node)
    key0 = (full_seq1, full_seq2)
    frame0 = key0
    stack = [frame0]

    # Memoize mapping (seq1, seq2) -> best size, embeddings
    _results = {}

    # Populate base cases
    empty1 = type(next(iter(all_decomp1.keys())))()
    empty2 = type(next(iter(all_decomp2.keys())))()
    best = (empty1, empty2)
    base_result = (0, best, 0, best)
    for seq1 in all_decomp1.keys():
        key1 = seq1
        t1, a1, b1, head1, tail1 = all_decomp1[key1]
        _results[(seq1, empty2)] = base_result
        _results[(head1, empty2)] = base_result
        _results[(tail1, empty2)] = base_result

    for seq2 in all_decomp2.keys():
        key2 = seq2
        t2, a2, b2, head2, tail2 = all_decomp2[key2]
        _results[(empty1, seq2)] = base_result
        _results[(empty1, head2)] = base_result
        _results[(empty1, tail2)] = base_result

    cdef double val_any, val_lvl
    cdef double val_any_h1s2, val_any_t1s2, val_any_s1h2, val_any_s1t2
    cdef double val_lvl_t1s2, val_lvl_s1t2
    cdef double pval_lvl_t1t2, pval_lvl_h1h2
    cdef double new_val_lvl
    cdef double affinity

    while stack:
        key = stack[-1]
        if key not in _results:
            seq1, seq2 = key

            t1, a1, b1, head1, tail1 = all_decomp1[seq1]
            t2, a2, b2, head2, tail2 = all_decomp2[seq2]

            best_any = None
            best_lvl = None
            val_any = 0
            val_lvl = 0

            # When using the head part of the decomp, we can only update the "low" candidate
            try_key = (head1, seq2)
            if try_key in _results:
                val_any_h1s2, cand_any_h1s2, _, _ = _results[try_key]
            else:
                stack.append(try_key)
                continue

            try_key = (tail1, seq2)
            if try_key in _results:
                val_any_t1s2, cand_any_t1s2, val_lvl_t1s2, cand_lvl_t1s2 = _results[
                    try_key
                ]
            else:
                stack.append(try_key)
                continue

            try_key = (seq1, head2)
            if try_key in _results:
                val_any_s1h2, cand_any_s1h2, _, _ = _results[try_key]
            else:
                stack.append(try_key)
                continue

            try_key = (seq1, tail2)
            if try_key in _results:
                val_any_s1t2, cand_any_s1t2, val_lvl_s1t2, cand_lvl_s1t2 = _results[
                    try_key
                ]
            else:
                stack.append(try_key)
                continue

            if val_any_h1s2 > val_any:
                val_any = val_any_h1s2
                best_any = cand_any_h1s2

            if val_any_t1s2 > val_any:
                val_any = val_any_t1s2
                best_any = cand_any_t1s2

            if val_any_s1h2 > val_any:
                val_any = val_any_s1h2
                best_any = cand_any_s1h2

            if val_any_s1t2 > val_any:
                val_any = val_any_s1t2
                best_any = cand_any_s1t2

            # The "LVL" case should include the case where any match exists on this
            # level. That means as long as we don't consider the heads, tail
            # matches are fine.
            if val_lvl_s1t2 > val_lvl:
                val_lvl = val_lvl_s1t2
                best_lvl = cand_lvl_s1t2

            if val_lvl_t1s2 > val_lvl:
                val_lvl = val_lvl_t1s2
                best_lvl = cand_lvl_t1s2

            # Case 1: The LCS involves this edge
            affinity = float(node_affinity(t1, t2))
            if affinity:
                try_key = (head1, head2)
                if try_key in _results:
                    _, _, pval_lvl_h1h2, new_lvl_h1h2 = _results[try_key]
                else:
                    stack.append(try_key)
                    continue

                try_key = (tail1, tail2)
                if try_key in _results:
                    _, _, pval_lvl_t1t2, new_lvl_t1t2 = _results[try_key]
                else:
                    stack.append(try_key)
                    continue

                # Add to the best solution at the former level
                new_val_lvl = pval_lvl_h1h2 + pval_lvl_t1t2 + affinity
                if new_val_lvl > val_lvl:
                    val_lvl = new_val_lvl
                    new_head1, new_head2 = new_lvl_h1h2
                    new_tail1, new_tail2 = new_lvl_t1t2
                    subseq1 = a1 + new_head1 + b1 + new_tail1
                    subseq2 = a2 + new_head2 + b2 + new_tail2
                    best_lvl = (subseq1, subseq2)

            # If the current level is better than any of the nestings forget the
            # nestings (we can never improve them) and just use the level
            if val_lvl >= val_any:
                val_any = val_lvl
                best_any = best_lvl

            if best_lvl is None:
                best_lvl = (empty1, empty2)

            if best_any is None:
                best_any = (empty1, empty2)

            # We solved the frame
            found = (val_any, best_any, val_lvl, best_lvl)
            _results[key] = found
        stack.pop()

    found = _results[key0]
    return found


cdef tuple balanced_decomp_unsafe_nocat_cython(sequence, dict open_to_close):
    cdef int stacklen = 1  # always +1 in the first iteration
    cdef int head_stop = 1

    tok_curr = sequence[0]
    want_close = open_to_close[tok_curr]

    # for tok_curr in sequence[1:]:
    for head_stop in range(1, len(sequence)):
        tok_curr = sequence[head_stop]
        stacklen += 1 if tok_curr in open_to_close else -1
        if stacklen == 0 and tok_curr == want_close:
            pop_close = sequence[head_stop:head_stop + 1]
            break

    pop_open = sequence[0:1]
    head = sequence[1:head_stop]
    tail = sequence[head_stop + 1:]
    return pop_open, pop_close, head, tail


cdef dict generate_all_decomp_nocat_cython(seq, open_to_close, open_to_node=None):
    if open_to_node is None:
        open_to_node = IdentityDictCython()
    all_decomp = {}
    stack = [seq]
    while stack:
        seq = stack.pop()
        if seq not in all_decomp and seq:
            (pop_open, pop_close, head, tail) = balanced_decomp_unsafe_nocat_cython(
                seq, open_to_close
            )
            node = open_to_node[pop_open[0]]
            all_decomp[seq] = (node, pop_open, pop_close, head, tail)
            if head:
                if tail:
                    stack.append(tail)
                stack.append(head)
            elif tail:
                stack.append(tail)
    return all_decomp


class IdentityDictCython:
    """ Used when ``open_to_node`` is unspecified """
    def __getitem__(self, key):
        return key
