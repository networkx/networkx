"""
Core python implementations for the longest common balanced sequence
subproblem, which is used by
:mod:`networkx.algorithms.minors.tree_embedding`.
"""
import operator
from .balanced_sequence import (
    IdentityDict,
    generate_all_decomp,
    balanced_decomp_unsafe,
)

__all__ = [
    "available_impls_longest_common_balanced_embedding",
    "longest_common_balanced_embedding",
]


def longest_common_balanced_embedding(
    seq1, seq2, open_to_close, open_to_node=None, node_affinity="auto", impl="auto"
):
    """
    Finds the longest common balanced sequence embedding between two sequences

    This is used as a subproblem to solve the maximum common embedded subtree
    problem described in [1].

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
        :func:`available_impls_longest_common_balanced_embedding`. The default
        is "auto", which chooses "iter-cython" if available, otherwise "iter".

    Returns
    -------
    Tuple[Tuple[Sequence[TokT], Sequence[TokT]], Float]
        A tuple indicating the common subsequence embedding of sequence1 and
        sequence2 (usually these are the same) and its value.

    See Also
    --------
    * This function is used to implement :func:`networkx.algorithms.minors.tree_embedding.maximum_common_ordered_subtree_embedding`

    Notes
    -----

    A balanced sequence is a sequence of tokens where there is a valid
    "nesting" of tokens given some relationship between opening and closing
    tokens (e.g. parenthesis, square brackets, and curly brackets). The
    following grammar generates all balanced sequences:

    .. code::

        t -> any opening token
        close(t) -> the closing token for t
        seq -> ''
        seq -> t + seq + close(t) + seq

    Given a balanced sequence s.

    .. code::

        s      = '([()[]])[{}([[]])]'

    We can use the grammar to decompose it as follows:

    .. code::

        s.a    = '('
        s.head =  '[()[]]'
        s.b    =        ')'
        s.tail =         '[{}([[]])]'

    Where s.a is the first token in s, and s.b is the corresponding closing
    token. s.head is everything between s.a and s.b, and s.tail is everything
    after s.b.

    Given two balanced sequences s1 and s2, their longest common subsequence
    embedding (lcse) is the largest common string you can obtain by deleting
    pairs of opening and closing tokens.

    We also define affinity as some degree of agreement between two tokens.
    By default we use an equality check: ``affinity(a1, a2) = (a1 == a2)``.

    The recurrence is defined as follows:

    .. code::

        lcse(s1, '') = 0
        lcse('', s2) = 0
        lcse(s1, s2) = max(
            lcse(s1.head, s2.head) + lcse(s1.tail, s2.tail) + affinity(s1.a, s2.a),
            lcse(s1.head + s1.tail, s2),
            lcse(s1, s2.head + s2.tail),
        )

    For example the longest common subsequence between the following s1 and s2
    are marked:

    .. code::

        seq1 = '([()[]])[{}([[]])]'
        _    = '        x   xxxx x'
        seq2 = '[[([])]]{[]}'
        _    = 'xx xx xx    '

        subseq = '[[[]]]'

    Also notice that '[[]]{}' is another solution to the previous example.
    That the longest common subsequence is not always unique.  For instance,
    consider the following two sequences:

    .. code::

        s1 = '({}[])'
        s2 = '[{}()]'

    They have three distinct longest common subsequences: '{}', '[]', and '()'.

    References
    ----------
    .. [1] Lozano, Antoni, and Gabriel Valiente.
        "On the maximum common embedded subtree problem for ordered trees."
        String Algorithmics (2004): 155-170.
        https://pdfs.semanticscholar.org/0b6e/061af02353f7d9b887f9a378be70be64d165.pdf

    Example
    -------
    >>> # Given two sequences and a mapping between opening and closing tokens
    >>> # we find the longest common subsequence (achievable by repeated
    >>> # balanced decomposition)
    >>> seq1 = "[][[]][]"
    >>> seq2 = "[[]][[]]"
    >>> open_to_close = {"[": "]"}
    >>> best, value = longest_common_balanced_embedding(seq1, seq2, open_to_close)
    ...
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '[][[]]'

    >>> # 1-label case from the paper (see Example 5)
    >>> # https://pdfs.semanticscholar.org/0b6e/061af02353f7d9b887f9a378be70be64d165.pdf
    >>> seq1 = "0010010010111100001011011011"
    >>> seq2 = "001000101101110001000100101110111011"
    >>> open_to_close = {"0": "1"}
    >>> best, value = longest_common_balanced_embedding(seq1, seq2, open_to_close)
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '00100101011100001011011011'
    >>> assert value == 13

    >>> # 3-label case
    >>> seq1 = "{({})([[]([]){(()(({()[]({}{})}))){}}])}"
    >>> seq2 = "{[({{}}{{[][{}]}(()[(({()})){[]()}])})]}"
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> best, value = longest_common_balanced_embedding(seq1, seq2, open_to_close)
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '{{}[][]()(({()})){}}'
    >>> assert value == 10
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
        if _cython_lcse_backend(error="ignore"):
            impl = "iter-cython"
        else:
            impl = "iter"

    if impl == "iter":
        value, best = _lcse_iter(
            full_seq1, full_seq2, open_to_close, node_affinity, open_to_node
        )
    elif impl == "iter-cython":
        balanced_embedding_cython = _cython_lcse_backend(error="raise")
        value, best = balanced_embedding_cython._lcse_iter_cython(
            full_seq1, full_seq2, open_to_close, node_affinity, open_to_node
        )
    elif impl == "recurse":
        _memo = {}
        _seq_memo = {}
        value, best = _lcse_recurse(
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
    return best, value


def available_impls_longest_common_balanced_embedding():
    """
    Returns all available implementations for
    :func:`longest_common_balanced_embedding`.

    Returns
    -------
    List[str]
        the string code for each available implementation
    """
    impls = []
    if _cython_lcse_backend():
        impls += [
            "iter-cython",
        ]

    # Pure python backends
    impls += [
        "iter",
        "recurse",
    ]
    return impls


def _cython_lcse_backend(error="ignore", verbose=0):
    """
    Returns the cython backend if available, otherwise None

    CommandLine
    -----------
    xdoctest -m networkx.algorithms.string.balanced_embedding _cython_lcse_backend
    """
    from networkx.algorithms.string._autojit import import_module_from_pyx
    from os.path import dirname
    import os

    # Toggle comments depending on the desired autojit default
    NETWORKX_AUTOJIT = os.environ.get("NETWORKX_AUTOJIT", "")
    # NETWORKX_AUTOJIT = not os.environ.get("NETWORKX_NO_AUTOJIT", "")

    module = import_module_from_pyx(
        "balanced_embedding_cython.pyx",
        dpath=dirname(__file__),
        error=error,
        autojit=NETWORKX_AUTOJIT,
        verbose=verbose,
    )
    balanced_embedding_cython = module
    return balanced_embedding_cython


def _lcse_iter(full_seq1, full_seq2, open_to_close, node_affinity, open_to_node):
    """
    Depth first stack trajectory and replace try except statements with ifs

    This is the current best pure-python algorithm candidate

    Converts :func:`_lcse_recurse` into an iterative algorithm using a fairly
    straightforward method that effectively simulates callstacks.  Uses a
    breadth-first trajectory and try-except to catch missing memoized results
    (which seems to be slightly faster than if statements).

    Example
    -------
    >>> full_seq1 = "[][[]][]"
    >>> full_seq2 = "[[]][[]]"
    >>> open_to_close = {"[": "]"}
    >>> import operator as op
    >>> node_affinity = op.eq
    >>> open_to_node = IdentityDict()
    >>> res = _lcse_iter(full_seq1, full_seq2, open_to_close, node_affinity,
    ...                 open_to_node)
    >>> val, embeddings = res
    >>> print(embeddings[0])
    [][[]]
    """
    all_decomp1 = generate_all_decomp(full_seq1, open_to_close, open_to_node)
    all_decomp2 = generate_all_decomp(full_seq2, open_to_close, open_to_node)

    key0 = (full_seq1, full_seq2)
    frame0 = key0
    stack = [frame0]

    # Memoize mapping (seq1, seq2) -> best size, embeddings
    _results = {}

    # Populate base cases
    empty1 = type(next(iter(all_decomp1.keys())))()
    empty2 = type(next(iter(all_decomp2.keys())))()
    best = (empty1, empty2)
    base_result = (0, best)
    for seq1 in all_decomp1.keys():
        key1 = seq1
        t1, a1, b1, head1, tail1, head_tail1 = all_decomp1[key1]
        _results[(seq1, empty2)] = base_result
        _results[(head1, empty2)] = base_result
        _results[(tail1, empty2)] = base_result
        _results[(head_tail1, empty2)] = base_result

    for seq2 in all_decomp2.keys():
        key2 = seq2
        t2, a2, b2, head2, tail2, head_tail2 = all_decomp2[key2]
        _results[(empty1, seq2)] = base_result
        _results[(empty1, head2)] = base_result
        _results[(empty1, tail2)] = base_result
        _results[(empty1, head_tail2)] = base_result

    while stack:
        key = stack[-1]
        if key not in _results:
            seq1, seq2 = key

            t1, a1, b1, head1, tail1, head_tail1 = all_decomp1[seq1]
            t2, a2, b2, head2, tail2, head_tail2 = all_decomp2[seq2]

            # Case 2: The current edge in sequence1 is deleted
            try_key = (head_tail1, seq2)
            if try_key in _results:
                cand1 = _results[try_key]
            else:
                stack.append(try_key)
                continue

            # Case 3: The current edge in sequence2 is deleted
            try_key = (seq1, head_tail2)
            if try_key in _results:
                cand2 = _results[try_key]
            else:
                stack.append(try_key)
                continue

            # Case 1: The LCSE involves this edge
            affinity = node_affinity(t1, t2)
            if affinity:
                try_key = (head1, head2)
                if try_key in _results:
                    pval_h, new_heads = _results[try_key]
                else:
                    stack.append(try_key)
                    continue

                try_key = (tail1, tail2)
                if try_key in _results:
                    pval_t, new_tails = _results[try_key]
                else:
                    stack.append(try_key)
                    continue

                new_head1, new_head2 = new_heads
                new_tail1, new_tail2 = new_tails

                subseq1 = a1 + new_head1 + b1 + new_tail1
                subseq2 = a2 + new_head2 + b2 + new_tail2

                res3 = (subseq1, subseq2)
                val3 = pval_h + pval_t + affinity
                cand3 = (val3, res3)
            else:
                cand3 = (-1, None)

            # We solved the frame
            _results[key] = max(cand1, cand2, cand3)
        stack.pop()

    found = _results[key0]
    return found


def _lcse_recurse(
    seq1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
):
    """
    Surprisingly, this recursive implementation is one of the faster
    pure-python methods for certain input types. However, its major drawback is
    that it can raise a RecursionError if the inputs are too deep.

    See also the iterative version :func:`_lcse_iter`
    """
    if not seq1:
        return 0, (seq1, seq1)
    elif not seq2:
        return 0, (seq2, seq2)
    else:
        key1 = hash(seq1)  # using hash(seq) is faster than seq itself
        key2 = hash(seq2)
        key = hash((key1, key2))
        if key in _memo:
            return _memo[key]

        if key1 in _seq_memo:
            a1, b1, head1, tail1, head1_tail1 = _seq_memo[key1]
        else:
            a1, b1, head1, tail1, head1_tail1 = balanced_decomp_unsafe(
                seq1, open_to_close
            )
            _seq_memo[key1] = a1, b1, head1, tail1, head1_tail1

        if key2 in _seq_memo:
            a2, b2, head2, tail2, head2_tail2 = _seq_memo[key2]
        else:
            a2, b2, head2, tail2, head2_tail2 = balanced_decomp_unsafe(
                seq2, open_to_close
            )
            _seq_memo[key2] = a2, b2, head2, tail2, head2_tail2

        # Case 2: The current edge in sequence1 is deleted
        val, best = _lcse_recurse(
            head1_tail1,
            seq2,
            open_to_close,
            node_affinity,
            open_to_node,
            _memo,
            _seq_memo,
        )

        # Case 3: The current edge in sequence2 is deleted
        val_alt, cand = _lcse_recurse(
            seq1,
            head2_tail2,
            open_to_close,
            node_affinity,
            open_to_node,
            _memo,
            _seq_memo,
        )
        if val_alt > val:
            best = cand
            val = val_alt

        # Case 1: The LCSE involves this edge
        t1 = open_to_node[a1[0]]
        t2 = open_to_node[a2[0]]
        affinity = node_affinity(t1, t2)
        if affinity:
            pval_h, new_heads = _lcse_recurse(
                head1,
                head2,
                open_to_close,
                node_affinity,
                open_to_node,
                _memo,
                _seq_memo,
            )
            pval_t, new_tails = _lcse_recurse(
                tail1,
                tail2,
                open_to_close,
                node_affinity,
                open_to_node,
                _memo,
                _seq_memo,
            )

            new_head1, new_head2 = new_heads
            new_tail1, new_tail2 = new_tails

            subseq1 = a1 + new_head1 + b1 + new_tail1
            subseq2 = a2 + new_head2 + b2 + new_tail2

            cand = (subseq1, subseq2)
            val_alt = pval_h + pval_t + affinity
            if val_alt > val:
                best = cand
                val = val_alt

        found = (val, best)
        _memo[key] = found
        return found
