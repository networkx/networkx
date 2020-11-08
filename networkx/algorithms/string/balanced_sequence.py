"""
Core python implementations for the longest common balanced sequence
subproblem, which is used by
:mod:`networkx.algorithms.embedding.tree_embedding`.
"""
import operator

__all__ = [
    "available_impls_longest_common_balanced_sequence",
    "longest_common_balanced_sequence",
    "random_balanced_sequence",
]


def longest_common_balanced_sequence(
    seq1, seq2, open_to_close, open_to_node=None, node_affinity="auto", impl="auto"
):
    """
    Finds the longest common balanced sequence embedding between two sequences

    This is used as a subproblem to solve the maximum common enbedded subtree
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
        sequences can always be re-encoded to differentitate between the same
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
        :func:`available_impls_longest_common_balanced_sequence`. The default
        is "auto", which chooses "iter-cython" if available, otherwise "iter".

    Returns
    -------
    Tuple[Tuple[Sequence[TokT], Sequence[TokT]], Float]
        A tuple indicating the common subsequence embedding of sequence1 and
        sequence2 (usually these are the same) and its value.

    See Also
    --------
    * This function is used to implement :func:`networkx.algorithms.embedding.tree_embedding.maximum_common_ordered_tree_embedding`

    Notes
    -----

    A balanced sequence is a sequence of tokens where there is a valid
    "nesting" of tokens given some relationship between opening and closing
    tokens (e.g. parethesis, square brackets, and curly brackets). The
    following grammar generates all balanced sequences:

    .. code::

        t -> any opening token
        close(t) -> the closing token for t
        seq -> ''
        seq -> t + seq + close(t) + seq

    Given a balanced sequence s.

    .. code::

        s      = '([()[]])[{}([[]])]'

    We can use the grammar to decomose it as follows:

    .. code::

        s.a    = '('
        s.head =  '[()[]]'
        s.b    =        ')'
        s.tail =         '[{}([[]])]'

    Where s.a is the first token in s, and s.b is the corresponding closing
    token. s.head is everything between s.a and s.b, and s.tail is everything
    after s.b.

    Given two balanced sequences s1 and s2, their longest common subsequence
    (lcs) is the largest common string you can obtain by deleting any pair of
    opening and closing tokens that you would like.

    We also define affinity as some degree of agreement between two tokens.
    By default we use an equality check: ``affinity(a1, a2) = (a1 == a2)``.

    The recurrence is defined as follows:

    .. code::

        lcs(s1, '') = 0
        lcs('', s2) = 0
        lcs(s1, s2) = max(
            lcs(s1.head, s2.head) + lcs(s1.tail, s2.tail) + affinity(s1.a, s2.a),
            lcs(s1.head + s1.tail, s2),
            lcs(s1, s2.head + s2.tail),
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
    >>> best, value = longest_common_balanced_sequence(seq1, seq2, open_to_close)
    ...
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '[][[]]'

    >>> # 1-label case from the paper (see Example 5)
    >>> # https://pdfs.semanticscholar.org/0b6e/061af02353f7d9b887f9a378be70be64d165.pdf
    >>> seq1 = "0010010010111100001011011011"
    >>> seq2 = "001000101101110001000100101110111011"
    >>> open_to_close = {"0": "1"}
    >>> best, value = longest_common_balanced_sequence(seq1, seq2, open_to_close)
    >>> subseq1, subseq2 = best
    >>> print("subseq1 = {!r}".format(subseq1))
    subseq1 = '00100101011100001011011011'
    >>> assert value == 13

    >>> # 3-label case
    >>> seq1 = "{({})([[]([]){(()(({()[]({}{})}))){}}])}"
    >>> seq2 = "{[({{}}{{[][{}]}(()[(({()})){[]()}])})]}"
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> best, value = longest_common_balanced_sequence(seq1, seq2, open_to_close)
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
        if _cython_lcs_backend(error="ignore"):
            impl = "iter-cython"
        else:
            impl = "iter"

    if impl == "iter":
        best, value = _lcs_iter(
            full_seq1, full_seq2, open_to_close, node_affinity, open_to_node
        )
    elif impl == "iter-cython":
        balanced_sequence_cython = _cython_lcs_backend(error="raise")
        best, value = balanced_sequence_cython._lcs_iter_cython(
            full_seq1, full_seq2, open_to_close, node_affinity, open_to_node
        )
    elif impl == "recurse":
        _memo = {}
        _seq_memo = {}
        best, value = _lcs_recurse(
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


def available_impls_longest_common_balanced_sequence():
    """
    Returns all available implementations for
    :func:`longest_common_balanced_sequence`.

    Returns
    -------
    List[str]
        the string code for each available implementation
    """
    impls = []
    if _cython_lcs_backend():
        impls += [
            "iter-cython",
        ]

    # Pure python backends
    impls += [
        "iter",
        "recurse",
    ]
    return impls


def _platform_pylib_exts():  # nocover
    """
    Returns .so, .pyd, or .dylib depending on linux, win or mac.
    Returns the previous with and without abi (e.g.
    .cpython-35m-x86_64-linux-gnu) flags.
    """
    import sysconfig

    valid_exts = []
    # handle PEP 3149 -- ABI version tagged .so files
    base_ext = "." + sysconfig.get_config_var("EXT_SUFFIX").split(".")[-1]
    # ABI = application binary interface
    tags = [
        sysconfig.get_config_var("SOABI"),
        "abi3",  # not sure why this one is valid, but it is
    ]
    tags = [t for t in tags if t]
    for tag in tags:
        valid_exts.append("." + tag + base_ext)
    # return with and without API flags
    valid_exts.append(base_ext)
    valid_exts = tuple(valid_exts)
    return valid_exts


def _autojit_cython(pyx_fpath, verbose=1):
    """
    This idea is that given a pyx file, we try to compile it

    Parameters
    ----------
    pyx_fpath : str
        path to the pyx file

    verbose : int
        higher is more verbose.
    """
    from os.path import dirname, join, basename, splitext
    import os
    import shutil

    # TODO: move necessary ubelt utilities to nx.utils?
    # Separate this into its own util?
    if shutil.which("cythonize"):
        pyx_dpath = dirname(pyx_fpath)

        # Check if the compiled library exists
        pyx_base = splitext(basename(pyx_fpath))[0]

        SO_EXTS = _platform_pylib_exts()
        so_fname = False
        for fname in os.listdir(pyx_dpath):
            if fname.startswith(pyx_base) and fname.endswith(SO_EXTS):
                so_fname = fname
                break

        try:
            # Currently this functionality depends on ubelt.
            # We could replace ub.cmd with subprocess.check_call and ub.augpath
            # with os.path operations, but hash_file and CacheStamp are harder
            # to replace. We can use "liberator" to statically extract these
            # and add them to nx.utils though.
            import ubelt as ub
        except Exception:
            return False
        else:
            if so_fname is False:
                # We can compute what the so_fname will be if it doesnt exist
                so_fname = pyx_base + SO_EXTS[0]

            so_fpath = join(pyx_dpath, so_fname)
            depends = [ub.hash_file(pyx_fpath, hasher="sha1")]
            stamp_fname = ub.augpath(so_fname, ext=".jit.stamp")
            stamp = ub.CacheStamp(
                stamp_fname,
                dpath=pyx_dpath,
                product=so_fpath,
                depends=depends,
                verbose=verbose,
            )
            if stamp.expired():
                ub.cmd("cythonize -i {}".format(pyx_fpath), verbose=verbose, check=True)
                stamp.renew()
            return True


def _autojit_this():
    import networkx as nx
    from os.path import dirname, join

    pyx_suffix = "algorithms/string/balanced_sequence_cython.pyx"
    mod_dpath = dirname(nx.__file__)
    pyx_fpath = join(mod_dpath, pyx_suffix)
    _autojit_cython(pyx_fpath)


AUTOJIT_TRIES = 0


def _cython_lcs_backend(error="ignore"):
    """
    Returns the cython backend if available, otherwise None

    CommandLine
    -----------
    xdoctest -m networkx.algorithms.string.balanced_sequence _cython_lcs_backend
    """
    global AUTOJIT_TRIES
    MAX_AUTOJIT_TRIES = 1

    # TODO: Could we try to JIT the cython module if we ship the pyx without
    # the compiled library.
    import os
    import warnings

    # Toggle comments depending on the desired autojit default
    # NETWORKX_AUTO_JIT = os.environ.get("NETWORKX_AUTOJIT", "")
    NETWORKX_AUTO_JIT = not os.environ.get("NETWORKX_NO_AUTOJIT", "")

    if NETWORKX_AUTO_JIT:
        AUTOJIT_TRIES += 1
        if AUTOJIT_TRIES <= MAX_AUTOJIT_TRIES:
            try:
                _autojit_this()
            except Exception as ex:
                warnings.warn("Cython autojit failed: ex={!r}".format(ex))
                if error == "raise":
                    raise

    try:
        from networkx.algorithms.string import balanced_sequence_cython
    except Exception:
        if error == "ignore":
            return None
        elif error == "raise":
            raise
        else:
            raise KeyError(error)
    else:
        return balanced_sequence_cython


def _lcs_iter(full_seq1, full_seq2, open_to_close, node_affinity, open_to_node):
    """
    Depth first stack trajectory and replace try except statements with ifs

    This is the current best pure-python algorithm candidate

    Converts :func:`_lcs_recurse` into an iterative algorithm using a fairly
    straightforward method that effectivly simulates callstacks.  Uses a
    breadth-first trajectory and try-except to catch missing memoized results
    (which seems to be slightly faster than if statements).

    Example
    -------
    >>> full_seq1 = "{({})([[]([]){(()(({()[]({}{})}))){}}])}"
    >>> full_seq2 = "{[({{}}{{[][{}]}(()[(({()})){[]()}])})]}"
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> full_seq1 = "[][[]][]"
    >>> full_seq2 = "[[]][[]]"
    >>> open_to_close = {"[": "]"}
    >>> import operator as op
    >>> node_affinity = op.eq
    >>> open_to_node = IdentityDict()
    >>> res = _lcs_iter(full_seq1, full_seq2, open_to_close, node_affinity,
    ...                 open_to_node)
    >>> val, embeddings = res
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

            # Case 1: The LCS involves this edge
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

    val, best = _results[key0]
    found = (best, val)
    return found


def _lcs_recurse(
    seq1, seq2, open_to_close, node_affinity, open_to_node, _memo, _seq_memo
):
    """
    Surprisingly, this recursive implementation is one of the faster
    pure-python methods for certain input types. However, its major drawback is
    that it can raise a RecurssionError if the inputs are too deep.
    """
    if not seq1:
        return (seq1, seq1), 0
    elif not seq2:
        return (seq2, seq2), 0
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
        best, val = _lcs_recurse(
            head1_tail1,
            seq2,
            open_to_close,
            node_affinity,
            open_to_node,
            _memo,
            _seq_memo,
        )

        # Case 3: The current edge in sequence2 is deleted
        cand, val_alt = _lcs_recurse(
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

        # Case 1: The LCS involves this edge
        t1 = open_to_node[a1[0]]
        t2 = open_to_node[a2[0]]
        affinity = node_affinity(t1, t2)
        if affinity:
            new_heads, pval_h = _lcs_recurse(
                head1,
                head2,
                open_to_close,
                node_affinity,
                open_to_node,
                _memo,
                _seq_memo,
            )
            new_tails, pval_t = _lcs_recurse(
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

        found = (best, val)
        _memo[key] = found
        return found


class UnbalancedException(Exception):
    """
    Denotes that a sequence was unbalanced
    """

    pass


class IdentityDict:
    """
    Used when ``open_to_node`` is unspecified
    """

    def __getitem__(self, key):
        return key


def generate_all_decomp(seq, open_to_close, open_to_node=None):
    """
    Generates all decompositions of a single balanced sequence by
    recursive decomposition of the head, tail, and head|tail.

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

    Notes
    -----
    In the paper: See Definition 2, 4, Lemma, 1, 2, 3, 4.

    Example
    -------
    >>> # Example 2 in the paper (one from each column)
    >>> seq = "00100100101111"
    >>> open_to_close = {"0": "1"}
    >>> all_decomp = generate_all_decomp(seq, open_to_close)
    >>> assert len(all_decomp) == len(seq) // 2
    >>> import pprint
    >>> pprint.pprint(all_decomp)
    {'00100100101111': ('0', '0', '1', '010010010111', '', '010010010111'),
     '0010010111': ('0', '0', '1', '01001011', '', '01001011'),
     '001011': ('0', '0', '1', '0101', '', '0101'),
     '01': ('0', '0', '1', '', '', ''),
     '010010010111': ('0', '0', '1', '', '0010010111', '0010010111'),
     '01001011': ('0', '0', '1', '', '001011', '001011'),
     '0101': ('0', '0', '1', '', '01', '01')}

    Example
    -------
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> seq = "({[[]]})[[][]]{{}}"
    >>> all_decomp = generate_all_decomp(seq, open_to_close)
    >>> node, *decomp = all_decomp[seq]
    >>> pop_open, pop_close, head, tail, head_tail = decomp
    >>> print("node = {!r}".format(node))
    node = '('
    >>> print("pop_open = {!r}".format(pop_open))
    pop_open = '('
    >>> print("pop_close = {!r}".format(pop_close))
    pop_close = ')'
    >>> print("head = {!r}".format(head))
    head = '{[[]]}'
    >>> print("tail = {!r}".format(tail))
    tail = '[[][]]{{}}'
    >>> print("head_tail = {!r}".format(head_tail))
    head_tail = '{[[]]}[[][]]{{}}'
    >>> decomp_alt = balanced_decomp(seq, open_to_close)
    >>> assert decomp_alt == tuple(decomp)

    Example
    -------
    >>> seq, open_to_close = random_balanced_sequence(10)
    >>> all_decomp = generate_all_decomp(seq, open_to_close)
    """
    if open_to_node is None:
        open_to_node = IdentityDict()
    all_decomp = {}
    stack = [seq]
    while stack:
        seq = stack.pop()
        if seq not in all_decomp and seq:
            (pop_open, pop_close, head, tail, head_tail) = balanced_decomp_unsafe(
                seq, open_to_close
            )
            node = open_to_node[pop_open[0]]
            all_decomp[seq] = (node, pop_open, pop_close, head, tail, head_tail)
            if head:
                if tail:
                    stack.append(head_tail)
                    stack.append(tail)
                stack.append(head)
            elif tail:
                stack.append(tail)
    return all_decomp


def balanced_decomp(sequence, open_to_close):
    """
    Generates a decomposition of a balanced sequence.

    Parameters
    ----------
    sequence : str | Tuple
        balanced sequence to be decomposed

    open_to_close: dict
        a dictionary that maps opening tokens to closing tokens in the balanced
             sequence problem.

    Returns
    -------
    : tuple[SeqT, SeqT, SeqT, SeqT, SeqT]
        where ``SeqT = type(sequence)``
        Contents of this tuple are:

            0. a1 - a sequence of len(1) containing the current opening token
            1. b1 - a sequence of len(1) containing the current closing token
            2. head - head of the sequence
            3. tail - tail of the sequence
            4. head_tail - the concatanted head and tail

    Example
    -------
    >>> # Example 3 from the paper
    >>> sequence = "001000101101110001000100101110111011"
    >>> open_to_close = {"0": "1"}
    >>> a1, b1, head, tail, head_tail = balanced_decomp(sequence, open_to_close)
    >>> print("head = {!r}".format(head))
    head = '010001011011'
    >>> print("tail = {!r}".format(tail))
    tail = '0001000100101110111011'

    Example
    -------
    >>> open_to_close = {0: 1}
    >>> sequence = [0, 0, 0, 1, 1, 1, 0, 1]
    >>> a1, b1, head, tail, head_tail = balanced_decomp(sequence, open_to_close)
    >>> print("a1 = {!r}".format(a1))
    a1 = [0]
    >>> print("b1 = {!r}".format(b1))
    b1 = [1]
    >>> print("head = {!r}".format(head))
    head = [0, 0, 1, 1]
    >>> print("tail = {!r}".format(tail))
    tail = [0, 1]
    >>> print("head_tail = {!r}".format(head_tail))
    head_tail = [0, 0, 1, 1, 0, 1]
    >>> a2, b2, tail1, tail2, head_tail2 = balanced_decomp(tail, open_to_close)

    Example
    -------
    >>> open_to_close = {"{": "}", "(": ")", "[": "]"}
    >>> sequence = "({[[]]})[[][]]"
    >>> a1, b1, head, tail, head_tail = balanced_decomp(sequence, open_to_close)
    >>> print("a1 = {!r}".format(a1))
    a1 = '('
    >>> print("b1 = {!r}".format(b1))
    b1 = ')'
    >>> print("head = {!r}".format(head))
    head = '{[[]]}'
    >>> print("tail = {!r}".format(tail))
    tail = '[[][]]'
    >>> print("head_tail = {!r}".format(head_tail))
    head_tail = '{[[]]}[[][]]'
    >>> a2, b2, tail1, tail2, head_tail2 = balanced_decomp(tail, open_to_close)
    >>> print("a2 = {!r}".format(a2))
    a2 = '['
    >>> print("b2 = {!r}".format(b2))
    b2 = ']'
    >>> print("tail1 = {!r}".format(tail1))
    tail1 = '[][]'
    >>> print("tail2 = {!r}".format(tail2))
    tail2 = ''
    >>> print("head_tail2 = {!r}".format(head_tail2))
    head_tail2 = '[][]'
    """
    gen = generate_balance(sequence, open_to_close)

    bal_curr, tok_curr, _ = next(gen)
    pop_open = sequence[0:1]
    want_close = open_to_close[tok_curr]

    head_stop = 1
    for head_stop, (bal_curr, tok_curr, _) in enumerate(gen, start=1):
        if tok_curr is None:
            break
        elif bal_curr and tok_curr == want_close:
            pop_close = sequence[head_stop : head_stop + 1]
            break
    head = sequence[1:head_stop]
    tail = sequence[head_stop + 1 :]
    head_tail = head + tail
    return pop_open, pop_close, head, tail, head_tail


def generate_balance(sequence, open_to_close):
    r"""
    Iterates through a balanced sequence and reports if the sequence-so-far
    is balanced at that position or not.

    Parameters
    ----------
    sequence: Iterable[TokT]:
        an input balanced sequence

    open_to_close : Dict[TokT, TokT]
        a mapping from opening to closing tokens in the balanced sequence

    Yields
    ------
    Tuple[bool, TokT, int]:
        boolean indicating if the sequence is balanced at this index, and the
        current token, and the index of the matching opening token.

    Raises
    ------
    UnbalancedException - if the input sequence is not balanced

    Example
    -------
    >>> open_to_close = {0: 1}
    >>> sequence = [0, 0, 0, 1, 1, 1]
    >>> gen = list(generate_balance(sequence, open_to_close))
    >>> for flag, token, idx in gen:
    ...     print("flag={:d}, token={}, prev_idx={}".format(flag, token, idx))
    flag=0, token=0, prev_idx=None
    flag=0, token=0, prev_idx=None
    flag=0, token=0, prev_idx=None
    flag=0, token=1, prev_idx=2
    flag=0, token=1, prev_idx=1
    flag=1, token=1, prev_idx=0

    Example
    -------
    >>> sequence, open_to_close = random_balanced_sequence(4, seed=0)
    >>> gen = list(generate_balance(sequence, open_to_close))
    """
    stack = []
    # Traversing the Expression
    for idx, token in enumerate(sequence):

        if token in open_to_close:
            # Push opening elements onto the stack
            stack.append((token, idx))
            prev_idx = None
        else:
            # Check that closing elements
            if not stack:
                raise UnbalancedException
            prev_open, prev_idx = stack.pop()
            want_close = open_to_close[prev_open]

            if token != want_close:
                raise UnbalancedException

        # If the stack is empty the sequence is currently balanced
        currently_balanced = not bool(stack)
        yield currently_balanced, token, prev_idx

    if stack:
        raise UnbalancedException


def balanced_decomp_unsafe(sequence, open_to_close):
    """
    Similar to :func:`balanced_decomp` but assumes that ``sequence`` is valid
    balanced sequence in order to execute faster.
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
    head_tail = head + tail
    return pop_open, pop_close, head, tail, head_tail


def generate_balance_unsafe(sequence, open_to_close):
    """
    Similar to :func:`generate_balance` but assumes that ``sequence`` is valid
    balanced sequence in order to execute faster.
    """
    stacklen = 0
    for token in sequence:
        if token in open_to_close:
            stacklen += 1
        else:
            stacklen -= 1
        yield stacklen == 0, token


def random_balanced_sequence(n, seed=None, item_type="chr", open_to_close=None):
    r"""
    Creates a random balanced sequence for testing / benchmarks

    Parameters
    ----------
    n : int
        A positive integer representing the number of nodes in the tree.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    open_to_close : dict | None
        if specified, updates existing open_to_close with tokens from this
        sequence.

    item_type: str
        the type of sequence returned (see `item_type` in :func:`tree_to_seq`
        for details) can also be "paren", which is a special case that returns
        a nested set of parenthesis.

    Returns
    -------
    Tuple[(str | Tuple), Dict[str, str]]
        The first item is the sequence itself
        the second item is the open_to_close mappings.

    Example
    -------
    >>> # Demo the various sequence encodings that we might use
    >>> seq, open_to_close = random_balanced_sequence(4, seed=1, item_type="chr")
    >>> print("seq = {!r}".format(seq))
    seq = '\x00\x02\x04\x06\x07\x05\x03\x01'
    >>> seq, open_to_close = random_balanced_sequence(4, seed=1, item_type="number")
    >>> print("seq = {!r}".format(seq))
    seq = (1, 2, 3, 4, -4, -3, -2, -1)
    >>> seq, open_to_close = random_balanced_sequence(10, seed=1, item_type="paren")
    >>> print("seq = {!r}".format(seq))
    seq = '([[[]{{}}](){{[]}}])'
    """
    from networkx.algorithms.embedding.tree_embedding import tree_to_seq
    from networkx.generators.random_graphs import random_ordered_tree
    from networkx.utils import create_py_random_state

    # Create a random otree and then convert it to a balanced sequence
    rng = create_py_random_state(seed)

    if open_to_close is None:
        open_to_close = {}

    # To create a random balanced sequences we simply create a random ordered
    # tree and convert it to a sequence
    tree = random_ordered_tree(n, seed=rng, directed=True)
    if item_type == "paren":
        # special case
        pool = "[{("
        for node in tree.nodes:
            tree.nodes[node]["label"] = rng.choice(pool)
        open_to_close.update({"[": "]", "{": "}", "(": ")"})
        seq, open_to_close, *_ = tree_to_seq(
            tree, open_to_close=open_to_close, item_type="label", container_type="str"
        )
    else:
        seq, open_to_close, *_ = tree_to_seq(
            tree,
            open_to_close=open_to_close,
            item_type=item_type,
        )
    return seq, open_to_close


if __name__ == "__main__":
    """
    CommandLine
    ------------
    xdoctest -m networkx.algorithms.string.balanced_sequence all
    """
    import xdoctest

    xdoctest.doctest_module(__file__)
