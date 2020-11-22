def test_simple_cases():
    from networkx.algorithms.string.balanced_isomorphism import (
        longest_common_balanced_isomorphism,
    )

    open_to_close = {"{": "}", "(": ")", "[": "]"}
    seq1 = "[[]][]"
    seq2 = "[]{}[]"
    res = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    (subseq1, subseq2), value = res
    print("subseq1 = {!r}".format(subseq1))
    assert subseq1 == "[][]"

    seq1 = "[[]][]"
    seq2 = "[]{}{}{}{}[]"
    res = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    (subseq1, subseq2), value = res
    print("subseq1 = {!r}".format(subseq1))
    assert subseq1 == "[][]"

    seq1 = "[[]]()()()[]"
    seq2 = "[]{}{}{}{}[]"
    res = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    (subseq1, subseq2), value = res
    print("subseq1 = {!r}".format(subseq1))
    assert subseq1 == "[][]"

    seq1 = "[[]](){}()()[]"
    seq2 = "[]{}{}{}{}[]"
    res = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    (subseq1, subseq2), value = res
    print("subseq1 = {!r}".format(subseq1))
    assert subseq1 == "[]{}[]"

    seq1 = "()([])[]"
    seq2 = "[](){}()"
    res = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    (subseq1, subseq2), value = res
    print("subseq1 = {!r}".format(subseq1))
    assert subseq1 == "()()"

    seq1 = "[()([])[]]"
    seq2 = "{[](){}()}"
    res = longest_common_balanced_isomorphism(seq1, seq2, open_to_close)
    (subseq1, subseq2), value = res
    print("subseq1 = {!r}".format(subseq1))
    assert subseq1 == "()()"


def test_all_implementations_are_same():
    """
    Tests several random sequences
    """
    from networkx.algorithms.string import balanced_isomorphism
    from networkx.algorithms.string import random_balanced_sequence
    from networkx.utils import create_py_random_state

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
        longest_common_balanced_sequence = (
            balanced_isomorphism.longest_common_balanced_isomorphism
        )

        # Note: the returned sequences may be different (maximum embeddings may not
        # be unique), but the values should all be the same.
        results = {}
        impls = (
            balanced_isomorphism.available_impls_longest_common_balanced_isomorphism()
        )
        for impl in impls:
            best, val = longest_common_balanced_sequence(
                seq1, seq2, open_to_close, node_affinity=None, impl=impl
            )
            results[impl] = val
        first = next(iter(results.values()))
        if not all(v == first for v in results.values()):
            print("results = {!r}".format(results))
            raise AssertionError("Implementations returned different values")
