import operator
from networkx.algorithms.string.balanced_sequence import (
    generate_balance_unsafe,
    IdentityDict,
)


def available_impls_longest_common_balanced_isomorphism():
    """
    Returns all available implementations for
    :func:`longest_common_balanced_isomorphism`.

    Returns
    -------
    List[str]
        the string code for each available implementation
    """
    impls = ["recurse", "iter"]
    if _cython_lcsi_backend():
        impls += [
            "iter-cython",
        ]
    return impls


def longest_common_balanced_isomorphism(
    seq1, seq2, open_to_close, open_to_node=None, node_affinity="auto", impl="auto"
):
    r"""
    Finds the longest common balanced sequence isomorphism between two
    sequences.

    Parameters
    ----------
    seq1, seq2: Sequence[TokT]
        two input balanced sequences

    open_to_close : Dict[TokT, TokT]
        a mapping from opening to closing tokens in the balanced sequence

    open_to_node : Dict[TokT, Any] | None
        If unspecified an identity mapping is assumed. Otherwise this is a
        dictionary that maps a sequence token to a value which is used in the
        ``node_affinity`` comparison.  Typically these are values corresponding
        to an original problem (e.g. a tree node).  This should only used in
        the case where the tokens in each sequence ``seq1`` and ``seq2`` are
        unique. NOTE: in the case where sequence tokens are not unique,
        sequences can always be re-encoded to differentiate between the same
        token at different indices without loss of generality.

    node_affinity : None | str | callable
        Function for to determine if two nodes can be matched. The function
        should take two arguments `node1` and `node2` and return a non-negative
        affinity score that is zero if the nodes are not allowed to match and
        some positive value indicating the strength of the match.  The return
        is interpreted as a weight that is used to break ties. If
        ``node_affinity=None`` then any node can match any other node and only
        the topology is important.  The default is "auto", which will use
        ``operator.eq`` to do a simple equality test on the nodes.

    impl : str
        Determines the backend implementation. Available choices are given by
        :func:`available_impls_longest_common_balanced_isomorphism`.
        The default is "auto", which chooses "iter-cython" if available,
        otherwise "iter".

    Returns
    -------
    Tuple[Tuple[Sequence[TokT], Sequence[TokT]], Float]
        A tuple indicating the common subsequence isomorphism of sequence1 and
        sequence2 (usually these are the same) and its value.

    See Also
    --------
    * This function is used to implement :func:`networkx.algorithms.minors.tree_isomorphism.maximum_common_ordered_subtree_isomorphism`
    * A similar function that relaxes isomorphisms to embeddings is :func:`networkx.algorithms.strength.balanced_sequence.longest_common_balanced_sequence`

    Example
    -------
    >>> # Given two sequences and a mapping between opening and closing tokens
    >>> # we find the longest common subsequence (achievable by repeated
    >>> # balanced decomposition)
    >>> seq1 = "[][[]][]"
    >>> seq2 = "[[]][[]]"
    >>> open_to_close = {"[": "]"}
    >>> best, value = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    ...
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '[[]][]'

    >>> # 1-label case from the paper (see Example 5)
    >>> # https://pdfs.semanticscholar.org/0b6e/061af02353f7d9b887f9a378be70be64d165.pdf
    >>> seq1 = "0010010010111100001011011011"
    >>> seq2 = "001000101101110001000100101110111011"
    >>> open_to_close = {"0": "1"}
    >>> best, value = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '001000101111000010111011'
    >>> assert value == 12

    >>> # 3-label case
    >>> seq1 = "{({})([[]([]){(()(({()[]({}{})}))){}}])}"
    >>> seq2 = "{[({{}}{{[][{}]}(()[(({()}[])){[]()}])})]}"
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> best, value = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '{([(){()}])}'
    >>> assert value == 6
    """
    if node_affinity == "auto" or node_affinity == "eq":
        node_affinity = operator.eq
    if node_affinity is None:

        def _matchany(a, b):
            return True

        node_affinity = _matchany
    if open_to_node is None:
        open_to_node = IdentityDict()
    full_seq1 = seq1
    full_seq2 = seq2
    if impl == "auto":
        if _cython_lcsi_backend(error="ignore"):
            impl = "iter-cython"
        else:
            impl = "iter"

    if impl == "iter":
        val_any, best_any, val_lvl, best_lvl = _lcsi_iter(
            full_seq1,
            full_seq2,
            open_to_close,
            node_affinity,
            open_to_node,
        )
    elif impl == "iter-cython":
        balanced_isomorphism_cython = _cython_lcsi_backend(error="raise")
        (
            val_any,
            best_any,
            val_lvl,
            best_lvl,
        ) = balanced_isomorphism_cython._lcsi_iter_cython(
            full_seq1, full_seq2, open_to_close, node_affinity, open_to_node
        )
    elif impl == "recurse":
        _memo = {}
        _seq_memo = {}
        val_any, best_any, val_lvl, best_lvl = _lcsi_recurse(
            full_seq1,
            full_seq2,
            open_to_close,
            node_affinity,
            open_to_node,
            _memo,
            _seq_memo,
        )
    else:
        raise KeyError(impl)

    best = best_any
    value = val_any

    return best, value


def _lcsi_iter(full_seq1, full_seq2, open_to_close, node_affinity, open_to_node):
    """
    Converts :func:`_lcsi_recurse` into an iterative algorithm.

    Example
    -------
    >>> import operator as op
    >>> seq1 = full_seq1 = '[[]][]'
    >>> seq2 = full_seq2 = '[]{}[]'
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> node_affinity = op.eq
    >>> _memo, _seq_memo = {}, {}
    >>> open_to_node = IdentityDict()
    >>> res = _lcsi_iter(full_seq1, full_seq2, open_to_close, node_affinity,
    ...                 open_to_node)
    >>> value, best, *_ = _lcsi_iter(
    ...     full_seq1, full_seq2, open_to_close, node_affinity, open_to_node)
    >>> print('value = {!r}, best = {!r}'.format(value, best[0]))
    value = 2, best = '[][]'
    """
    all_decomp1 = generate_all_decomp_nocat(full_seq1, open_to_close, open_to_node)
    all_decomp2 = generate_all_decomp_nocat(full_seq2, open_to_close, open_to_node)
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
            affinity = node_affinity(t1, t2)
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


def _lcsi_recurse(
    seq1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
):
    """
    Recursive implementation of longest common substring isomorphism.

    Notes
    -----

    Recall a balanced sequence ``s`` can be decomposed as follows:

    .. code::
        # Input balanced sequence s
        s      = '([()[]])[{}([[]])]'

        # Its decomposition into a head and tail
        s.a    = '('
        s.head =  '[()[]]'
        s.b    =        ')'
        s.tail =         '[{}([[]])]'


        # A recursive tail decomposition of a sequence


    The recurrence returns two values: (0) the best isomorphism that includes
    the start of one of the input sequences and (1) the best isomorphism at a
    deeper location in the sequence.  Is defined as follows:

    .. code::

        Let lcsi(s1, s2, LVL) be the best isoseq between s1 and s2 that includes
            either the token at s1[0] and s2[0] or some token in the recursive
            tail decomposition of each sequence. (i.e. the lsci begins at some
            node at the current outermost level of nesting)

        Let lcsi(s1, s2, ANY) be the best overall isoseq between s1 and s2 that
            might exist in the head of one of the sequences in the recursive
            tail decompositions of s1 and s2. (i.e. the lsci might begin at
            some deeper nesting level in either sequence).

        lcsi(s1, '', ANY) = 0
        lcsi(s1, '', LVL) = 0
        lcsi('', s2, ANY) = 0
        lcsi('', s2, LVL) = 0

        # The value of the LCSI including the a first token match is 0 if the
        # tokens dont match otherwise it is the affinity plus the LCSI that
        # includes the next token in both the head and tail of the balanced
        # sequence.
        #
        # IT CAN ALSO be the case that one string matches the tail of another
        lcsi(s1, s2, LVL) = max(
            lcsi(s1, s2.tail, LVL) + lcsi(s1.tail, s2, LVL)
            lcsi(s1.head, s2.head, LVL) + lcsi(s1.tail, s2.tail, LVL) + affinity(s1.a, s2.a) if affinity(s1.a, s2.a) else 0
        )
        # Note that we cannot consider any exclusion cases because we are not
        # allowed to "skip" edges like we are in the "subsequence embedding"
        # problem.

        # For the LCSI that excludes the current matching token, we peel that
        # token off of the first and second sequence and subproblems that
        # compare the head or tail of one sequence to the entire other
        # sequence. Because the current leading token is discarded in at least
        # one of the input sequences we consider the include and exclude case
        # for all subproblems here.
        lcsi(s1, s2, ANY) = max(
            #
            lcsi(s1, s2, LVL)

            # The case where we only consider the head/tail of s1
            lcsi(s1.head, s2, ANY),
            lcsi(s1.tail, s2, ANY),

            # The case where we only consider the head/tail of s1
            lcsi(s1.head, s2, ANY),
            lcsi(s1.tail, s2, ANY),
        )

        # Note that by the way the recurrence is defined, s1.head will be
        # compared to s2.head in subsequent subproblems, so explicitly adding
        # that decomposition here is not necessary.

        The final lcsi for s1 and s2 is

        lcsi(s1, s2) = lcsi(s1, s2, ANY)

    Example
    -------
    >>> import operator as op
    >>> node_affinity = op.eq
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> open_to_node = IdentityDict()
    >>> # ---
    >>> seq1 = full_seq1 = "[][[]][]"
    >>> seq2 = full_seq2 = "[[]][[]]"
    >>> _memo, _seq_memo = {}, {}
    >>> value, best, *_ = _lcsi_recurse(
    ...     full_seq1, full_seq2, open_to_close, node_affinity, open_to_node,
    ...     _memo, _seq_memo)
    >>> print('value = {!r}, best = {!r}'.format(value, best[0]))
    value = 3, best = '[[]][]'
    >>> # ---
    >>> seq1 = full_seq1 = "[{[[]]}]"
    >>> seq2 = full_seq2 = "[[{[[]]}]]"
    >>> _memo, _seq_memo = {}, {}
    >>> value, best, *_ = _lcsi_recurse(
    ...     full_seq1, full_seq2, open_to_close, node_affinity, open_to_node,
    ...     _memo, _seq_memo)
    >>> print('value = {!r}, best = {!r}'.format(value, best[0]))
    value = 4, best = '[{[[]]}]'
    >>> # ---
    >>> seq1 = full_seq1 = '({{{[]}}})'
    >>> seq2 = full_seq2 = '[{{([()])}}]'
    >>> _memo, _seq_memo = {}, {}
    >>> value, best, *_ = _lcsi_recurse(
    ...     full_seq1, full_seq2, open_to_close, node_affinity, open_to_node,
    ...     _memo, _seq_memo)
    >>> print('value = {!r}, best = {!r}'.format(value, best[0]))
    value = 2, best = '{{}}'
    >>> # ---
    >>> full_seq1 = '[[]][]'
    >>> full_seq2 = '[]{}[]'
    >>> _memo, _seq_memo = {}, {}
    >>> value, best, *_ = _lcsi_recurse(
    ...     full_seq1, full_seq2, open_to_close, node_affinity, open_to_node,
    ...     _memo, _seq_memo)
    >>> print('value = {!r}, best = {!r}'.format(value, best[0]))
    value = 2, best = '[][]'
    >>> # ---
    >>> full_seq1 = '[[]][]'
    >>> full_seq2 = '[]{}{}{}{}[]'
    >>> _memo, _seq_memo = {}, {}
    >>> value, best, *_ = _lcsi_recurse(
    ...     full_seq1, full_seq2, open_to_close, node_affinity, open_to_node,
    ...     _memo, _seq_memo)
    >>> print('value = {!r}, best = {!r}'.format(value, best[0]))
    value = 2, best = '[][]'
    """
    if not seq1:
        return 0, (seq1, seq1), 0, (seq1, seq1)
    elif not seq2:
        return 0, (seq2, seq2), 0, (seq2, seq2)
    else:
        key1 = hash(seq1)
        key2 = hash(seq2)
        key = hash((key1, key2))
        if key in _memo:
            return _memo[key]

        if key1 in _seq_memo:
            a1, b1, head1, tail1 = _seq_memo[key1]
        else:
            a1, b1, head1, tail1 = balanced_decomp_unsafe_nocat(seq1, open_to_close)
            _seq_memo[key1] = a1, b1, head1, tail1

        if key2 in _seq_memo:
            a2, b2, head2, tail2 = _seq_memo[key2]
        else:
            a2, b2, head2, tail2 = balanced_decomp_unsafe_nocat(seq2, open_to_close)
            _seq_memo[key2] = a2, b2, head2, tail2

        # TODO: IS THIS THE CORRECT MODIFICATION TO THE RECURRANCE TO
        # ACHIEVE A SUBTREE ISOMORPHISM INSTEAD OF AN EMBEDDING?
        r"""
        We return two solutions at each step: the solution value at
        this level if one exists, and the solution value at any other depth.
        We are allowed to add to the first, but can take the second if we want
        to.

        This should work because we know a solution that skipped a layer will
        never be added to, and we are always keeping track of the solution that
        might change. By the time we get to the root level, we have enough info
        to know which is better.
        """

        # Consider the case where the best isoseq does not include the leading
        # tokens of s1 and s2.
        best_any = None
        best_lvl = None
        val_any = 0
        val_lvl = 0

        # When using the head part of the decomp, we can only update the "low" candidate
        val_any_h1s2, cand_any_h1s2, _, _, = _lcsi_recurse(
            head1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
        )
        val_any_t1s2, cand_any_t1s2, val_lvl_t1s2, cand_lvl_t1s2 = _lcsi_recurse(
            tail1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
        )
        val_any_s1h2, cand_any_s1h2, _, _ = _lcsi_recurse(
            seq1, head2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
        )
        val_any_s1t2, cand_any_s1t2, val_lvl_s1t2, cand_lvl_s1t2 = _lcsi_recurse(
            seq1, tail2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
        )

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

        # Consider the case where the best isoseq does include the leading
        # tokens of s1 and s2.
        t1 = open_to_node[a1[0]]
        t2 = open_to_node[a2[0]]
        affinity = node_affinity(t1, t2)
        if affinity:

            # Note, the "ex" portions of the LCSI don't matter because val_any
            # and best_any will already contain them if they matter We only care
            # about extending the current "in" case.
            # (Actually this is wrong)
            _, _, pval_lvl_h1h2, new_lvl_h1h2 = _lcsi_recurse(
                head1,
                head2,
                open_to_close,
                node_affinity,
                open_to_node,
                _memo,
                _seq_memo,
            )

            _, _, pval_lvl_t1t2, new_lvl_t1t2 = _lcsi_recurse(
                tail1,
                tail2,
                open_to_close,
                node_affinity,
                open_to_node,
                _memo,
                _seq_memo,
            )

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
            best_lvl = (type(seq1)(), type(seq2)())

        if best_any is None:
            best_any = (type(seq1)(), type(seq2)())

        # We return two solutions:
        # the best that includes any token at this level (lvl)
        # the best overall that could be at a deeper nesting (nst)
        found = (val_any, best_any, val_lvl, best_lvl)
        _memo[key] = found
        return found


def balanced_decomp_unsafe_nocat(sequence, open_to_close):
    """
    Similar to :func:`balanced_decomp` but assumes that ``sequence`` is valid
    balanced sequence in order to execute faster. Also does not return
    the concatenated head_tail as it is unused in the isomorphim problem.

    SeeAlso
    -------
    balanced_decomp, balanced_decomp_unsafe
    """
    gen = generate_balance_unsafe(sequence, open_to_close)

    bal_curr, tok_curr = next(gen)
    pop_open = sequence[0:1]
    want_close = open_to_close[tok_curr]

    head_stop = 1
    for head_stop, (bal_curr, tok_curr) in enumerate(gen, start=1):
        if bal_curr and tok_curr == want_close:
            pop_close = sequence[head_stop : head_stop + 1]
            break
    head = sequence[1:head_stop]
    tail = sequence[head_stop + 1 :]
    return pop_open, pop_close, head, tail


def generate_all_decomp_nocat(seq, open_to_close, open_to_node=None):
    """
    Generates all decompositions of a single balanced sequence by recursive
    decomposition of the head, tail.

    Parameters
    ----------
    seq : Tuple | str
        a tuple of hashable items or a string where each character is an item

    open_to_close : Dict
        a dictionary that maps opening tokens to closing tokens in the balanced
        sequence problem.

    open_to_node : Dict
        a dictionary that maps a sequence token to a token corresponding to an
        original problem (e.g. a tree node)

    Returns
    -------
    Dict :
        mapping from a sub-sequence to its decomposition

    SeeAlso
    -------
    generate_balance_unsafe, generate_balance

    Example
    -------
    >>> import pprint
    >>> seq = '{{(){}}}'
    >>> open_to_close = {'[': ']', '{': '}', '(': ')'}
    >>> all_decomp = generate_all_decomp_nocat(seq, open_to_close)
    >>> print('all_decomp = {}'.format(pprint.pformat(all_decomp)))
    all_decomp = {'(){}': ('(', '(', ')', '', '{}'),
     '{(){}}': ('{', '{', '}', '(){}', ''),
     '{{(){}}}': ('{', '{', '}', '{(){}}', ''),
     '{}': ('{', '{', '}', '', '')}

    """
    if open_to_node is None:
        open_to_node = IdentityDict()
    all_decomp = {}
    stack = [seq]
    while stack:
        seq = stack.pop()
        if seq not in all_decomp and seq:
            (pop_open, pop_close, head, tail) = balanced_decomp_unsafe_nocat(
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


def _cython_lcsi_backend(error="ignore", verbose=0):
    """
    Returns the cython backend if available, otherwise None

    CommandLine
    -----------
    xdoctest -m networkx.algorithms.string.balanced_isomorphism _cython_lcsi_backend
    """
    from networkx.algorithms.string._autojit import import_module_from_pyx
    from os.path import dirname
    import os

    # Toggle comments depending on the desired autojit default
    NETWORKX_AUTOJIT = os.environ.get("NETWORKX_AUTOJIT", "")
    # NETWORKX_AUTOJIT = not os.environ.get("NETWORKX_NO_AUTOJIT", "")

    module = import_module_from_pyx(
        "balanced_isomorphism_cython.pyx",
        dpath=dirname(__file__),
        error=error,
        autojit=NETWORKX_AUTOJIT,
        verbose=verbose,
    )
    balanced_embedding_cython = module
    return balanced_embedding_cython
