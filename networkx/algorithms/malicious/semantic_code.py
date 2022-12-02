"""
Converting a program to a code with semantic meaning
"""

__all__ = ["convert_to_semantic"]

def convert_to_semantic(program):
    """Converts the given program parsed and transformed to a code with semantic meaning

    Parameters
    ----------
    program : string
        A path to the file that contains the source code

    Returns
    -------
    sementic_code_file_path : string
        A path to the new file that will contain the semantic code of the original program 

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

    Programmer
    ----------
    Stu L.Akirav & B.Schtalman

    Example 1: valid path
    ----------
    path1 = codes/program1
    >>> convert_to_semantic(path1)
    codes/semantic1

    Example 2: invalid path
    ----------
    path2 = codes/program2 # file does not exist
    >>> convert_to_semantic(path2)
    Exception: NetworkXPathDoesNotExist
    """
