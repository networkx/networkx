"""
Helpers and utilities for balanced sequence problems.
"""

__all__ = [
    "random_balanced_sequence",
]


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
            4. head_tail - the concatenated head and tail

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


def random_balanced_sequence(
    n, seed=None, item_type="chr", container_type="auto", open_to_close=None
):
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

    container_type : str
        Determines the container_type type. Can be "auto", "list", "tuple", or
        "str". If "auto" tries to choose the best given the input data.

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
    seq = '\x00\x02\x04\x05\x03\x06\x07\x01'
    >>> seq, open_to_close = random_balanced_sequence(4, seed=1, item_type="number")
    >>> print("seq = {!r}".format(seq))
    seq = (1, 2, 3, -3, -2, 4, -4, -1)
    >>> seq, open_to_close = random_balanced_sequence(10, seed=1, item_type="paren")
    >>> print("seq = {!r}".format(seq))
    seq = '([[{{[]{[]}}{}()}]])'
    """
    from networkx.algorithms.minors.tree_embedding import tree_to_seq
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
            tree,
            open_to_close=open_to_close,
            item_type="label",
            container_type=container_type,
        )
    else:
        seq, open_to_close, *_ = tree_to_seq(
            tree,
            open_to_close=open_to_close,
            item_type=item_type,
            container_type=container_type,
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
