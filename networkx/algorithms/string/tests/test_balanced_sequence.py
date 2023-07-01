"""
Tests for balanced sequences

Command Line
------------
pytest networkx/algorithms/string/tests/test_balanced_sequence.py
"""
from networkx.algorithms.string import balanced_sequence
from networkx.algorithms.string import balanced_embedding
from networkx.algorithms.string import random_balanced_sequence
from networkx.utils import create_py_random_state


def test_all_implementations_are_same():
    """
    Tests several random sequences
    """

    seed = 93024896892223032652928827097264
    rng = create_py_random_state(seed)

    maxsize = 20
    num_trials = 5

    for _ in range(num_trials):
        n1 = rng.randint(1, maxsize)
        n2 = rng.randint(1, maxsize)

        seq1, open_to_close = random_balanced_sequence(n1, seed=rng)
        seq2, open_to_close = random_balanced_sequence(
            n2, open_to_close=open_to_close, seed=rng
        )

        # Note: the returned sequences may be different (maximum embeddings may not
        # be unique), but the values should all be the same.
        results = {}
        impls = balanced_embedding.available_impls_longest_common_balanced_embedding()
        for impl in impls:
            best, val = balanced_embedding.longest_common_balanced_embedding(
                seq1, seq2, open_to_close, node_affinity=None, impl=impl
            )
            results[impl] = val


def test_paper_case():
    # 1-label case from the paper (see Example 5)
    # https://pdfs.semanticscholar.org/0b6e/061af02353f7d9b887f9a378be70be64d165.pdf
    seq1 = "0010010010111100001011011011"
    seq2 = "001000101101110001000100101110111011"
    open_to_close = {"0": "1"}
    best, value = balanced_embedding.longest_common_balanced_embedding(
        seq1, seq2, open_to_close
    )
    subseq1, subseq2 = best
    print("subseq1 = {!r}".format(subseq1))
    assert value == 13
    assert subseq1 == "00100101011100001011011011"


def test_sequence_reencode():
    """
    Test that we can reencode two sequences to determine which indices are part
    of the solution.
    """
    seq1, open_to_close = balanced_sequence.random_balanced_sequence(
        3, item_type="paren"
    )
    seq2, open_to_close = balanced_sequence.random_balanced_sequence(
        3, item_type="paren"
    )

    def reencode_seq(seq, open_to_close, offset=0):
        alt_seq = []
        alt_open_to_close = {}
        for idx, info in enumerate(
            balanced_sequence.generate_balance(seq, open_to_close)
        ):
            flag, token, open_idx = info
            alt_tok = chr(idx + offset)
            alt_seq.append(alt_tok)
            if open_idx is not None:
                alt_open_tok = chr(open_idx + offset)
                alt_open_to_close[alt_open_tok] = alt_tok
        alt_seq = "".join(alt_seq)
        return alt_seq, alt_open_to_close

    alt_seq1, alt_open_to_close1 = reencode_seq(seq1, open_to_close, offset=0)
    offset = ord(alt_seq1[-1]) + 1
    alt_seq2, alt_open_to_close2 = reencode_seq(seq2, open_to_close, offset=offset)

    alt_open_to_close = {}
    alt_open_to_close.update(alt_open_to_close1)
    alt_open_to_close.update(alt_open_to_close2)

    alt_open_to_node = {}
    alt_open_to_node.update(dict(zip(alt_seq1, seq1)))
    alt_open_to_node.update(dict(zip(alt_seq2, seq2)))

    alt_best, alt_value = balanced_embedding.longest_common_balanced_embedding(
        alt_seq1,
        alt_seq2,
        alt_open_to_close,
        open_to_node=alt_open_to_node,
        node_affinity="eq",
        impl="auto",
    )

    alt_subseq1, alt_subseq2 = alt_best

    # decode to positions
    subidxs1 = [ord(c) for c in alt_subseq1]
    subidxs2 = [ord(c) - offset for c in alt_subseq2]

    recon_subseq1 = "".join([seq1[idx] for idx in subidxs1])
    recon_subseq2 = "".join([seq2[idx] for idx in subidxs2])

    indicator1 = [" "] * len(seq1)
    for idx in subidxs1:
        indicator1[idx] = "x"

    indicator2 = [" "] * len(seq2)
    for idx in subidxs2:
        indicator2[idx] = "x"

    print("seq1 = {!r}".format(seq1))
    print("     = {!r}".format("".join(indicator1)))
    print("seq2 = {!r}".format(seq2))
    print("     = {!r}".format("".join(indicator2)))

    best, value = balanced_embedding.longest_common_balanced_embedding(
        seq1, seq2, open_to_close, node_affinity="eq", impl="auto"
    )
    subseq1, subseq2 = best

    print("alt_value = {!r}".format(alt_value))
    print("value     = {!r}".format(value))

    print("recon_subseq1 = {!r}".format(recon_subseq1))
    print("recon_subseq2 = {!r}".format(recon_subseq2))

    print("subseq1       = {!r}".format(subseq1))
    print("subseq2       = {!r}".format(subseq2))

    assert value == alt_value

    # Note that the longest common subsequence is not always unique
    # For instance
    # There are 3 distinct longest common subsequence for
    # seq1 = '({}[])'
    # seq2 = '[{}()]'
    # You have  '{}', '[]', and '()'.
    # assert recon_subseq1 == subseq1
    # assert recon_subseq2 == subseq2
