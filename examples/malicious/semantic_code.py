"""
Converting a program to a code with semantic meaning
"""

__all__ = ["convert_code__to_semantic"]

def convert_code__to_semantic(program):
    """
    Converts the given program parsed and transformed to a code with semantic meaning.
    The function returns a string with the semantic code.

    Parameters
    ----------
    program : string
        The source code

    Returns
    -------
    sementic_code : string
        A string that will contain the semantic code of the original program 

    Raises
    ------
    NetworkXPathDoesNotExist
        If the given path does not exist.

    Notes
    -----
    Sementic refers to the meaning associated with the statement in a programming language.
    It is all about the meaning of the statement which interprets the program easily.
    Errors are handled at runtime.

    https://www.geeksforgeeks.org/difference-between-syntax-and-semantics/

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example : valid path
    ---------------------
    >>> source_code1 = '1: dim n, p, i\n\
    >>> 2: n = 5\n\
    >>> 3: p = 1\n\
    >>> 4: for i = 1 to n do\n\
    >>> 5: p = p * i\n\
    >>> 6: end for'

    >>> convert_code__to_semantic(source_code1)
        '1: dim n\n'\
        '2: dim p\n'\
        '3: dim i\n'\
        '4: n=5\n'\
        '5: p=1\n'\
        '6: i=1\n'\
        '7: if i ≤ n then\n'\
        '8: p=p * i\n'\
        '9: i=i + 1\n'\
        '10: goto 7:\n'\
        '11: end if'
    """
    return 0  # Empty implementation
