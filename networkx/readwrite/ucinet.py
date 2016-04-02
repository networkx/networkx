# -*- coding: utf-8 -*-
#
# Authors: Laura Dominé (temigo@gmx.com)

"""
**************
UCINET DL
**************
Read and write graphs in UCINET DL format.

This implementation currently supports only the 'fullmatrix' data format.

Format
------
The UCINET DL format is the most common file format used by UCINET package.

Basic example:

DL N = 5
Data:
0 1 1 1 1
1 0 1 0 0
1 1 0 0 1
1 0 0 0 0
1 0 1 0 0

References
----------
    See UCINET User Guide or http://www.analytictech.com/ucinet/help/hs5000.htm
    for full format information. Short version on http://www.analytictech.com/networks/dataentry.htm
"""
import re
import shlex
import networkx as nx
from networkx.utils import is_string_like, open_file, make_str
from numpy import genfromtxt, reshape, array_str

__all__ = ['generate_ucinet', 'read_ucinet', 'parse_ucinet', 'write_ucinet']


def generate_ucinet(G):
    """Generate lines in UCINET graph format.

    Parameters
    ----------
    G : graph
       A Networkx graph

    Examples
    --------


    Notes
    -----
    The default format 'fullmatrix' is used (for UCINET DL format).
    
    References
    ----------
    See UCINET User Guide or http://www.analytictech.com/ucinet/help/hs5000.htm
    for full format information. Short version on http://www.analytictech.com/networks/dataentry.htm
    """
    n = G.number_of_nodes()
    nodes = sorted(list(G.nodes()))
    yield 'dl n=%i format=fullmatrix' % n

    # Labels
    try:
        int(nodes[0])
    except ValueError:
        s = 'labels:\n'
        for label in nodes:
            s += label + ' '
        yield s

    yield 'data:'

    yield str(nx.to_numpy_matrix(G, nodelist=nodes, dtype=int)).replace('[', ' ').replace(']', ' ').lstrip().rstrip()


@open_file(0, mode='rb')
def read_ucinet(path, encoding='UTF-8'):
    """Read graph in UCINET format from path.

    Parameters
    ----------
    path : file or string
       File or filename to read.
       Filenames ending in .gz or .bz2 will be uncompressed.

    Returns
    -------
    G : NetworkX MultiGraph or MultiDiGraph.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_ucinet(G, "test.dl")
    >>> G=nx.read_ucinet("test.dl")

    To create a Graph instead of a MultiGraph use

    >>> G1=nx.Graph(G)

    See Also
    --------
    parse_ucinet()

    References
    ----------
    See UCINET User Guide or http://www.analytictech.com/ucinet/help/hs5000.htm
    for full format information. Short version on http://www.analytictech.com/networks/dataentry.htm
    """
    lines = (line.decode(encoding) for line in path)
    return parse_ucinet(lines)


@open_file(1, mode='wb')
def write_ucinet(G, path, encoding='UTF-8'):
    """Write graph in UCINET format to path.

    Parameters
    ----------
    G : graph
       A Networkx graph
    path : file or string
       File or filename to write.
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_ucinet(G, "test.net")

    References
    ----------
    See UCINET User Guide or http://www.analytictech.com/ucinet/help/hs5000.htm
    for full format information. Short version on http://www.analytictech.com/networks/dataentry.htm
    """
    for line in generate_ucinet(G):
        line += '\n'
        path.write(line.encode(encoding))


def parse_ucinet(lines):
    """Parse UCINET format graph from string or iterable.

    Currently only the 'fullmatrix' format is supported.

    Parameters
    ----------
    lines : string or iterable
       Data in UCINET format.

    Returns
    -------
    G : NetworkX graph

    See Also
    --------
    read_ucinet()

    References
    ----------
    See UCINET User Guide or http://www.analytictech.com/ucinet/help/hs5000.htm
    for full format information. Short version on http://www.analytictech.com/networks/dataentry.htm
    """
    G = nx.MultiDiGraph()

    if not is_string_like(lines):
        s = ''
        for line in lines:
            if type(line) == bytes:
                s += line.decode('utf-8')
            else:
                s += line
        lines = s
    lexer = shlex.shlex(lines.lower())
    lexer.whitespace += ',='
    lexer.whitespace_split = True

    number_of_nodes = 0
    number_of_matrices = 0
    nr = 0  # number of rows (rectangular matrix)
    nc = 0  # number of columns (rectangular matrix)
    ucinet_format = 'fullmatrix'  # Format by default
    labels = {}  # Contains labels of nodes
    row_labels_embedded = False  # Whether labels are embedded in data or not
    cols_labels_embedded = False
    diagonal = True  # whether the main diagonal is present or absent

    KEYWORDS = ('format', 'data:', 'labels:')  # TODO remove ':' in keywords

    while lexer:
        try:
            token = next(lexer)
        except StopIteration:
            break
        # print "Token : %s" % token
        if token.startswith('n'):
            if token.startswith('nr'):
                nr = int(get_param("\d+", token, lexer))
                number_of_nodes = max(nr, nc)
            elif token.startswith('nc'):
                nc = int(get_param("\d+", token, lexer))
                number_of_nodes = max(nr, nc)
            elif token.startswith('nm'):
                number_of_matrices = int(get_param("\d+", token, lexer))
            else:
                number_of_nodes = int(get_param("\d+", token, lexer))
                nr = number_of_nodes
                nc = number_of_nodes

        elif token.startswith("diagonal"):
            diagonal = get_param("present|absent", token, lexer)

        elif token.startswith("format"):
            ucinet_format = get_param("^(fullmatrix|upperhalf|lowerhalf|nodelist1|nodelist2|nodelist1b|\
                                        edgelist1|edgelist2|blockmatrix|partition)$", token, lexer)

        # TODO : row and columns labels
        elif token.startswith("row"):  # Row labels
            pass
        elif token.startswith("column"):  # Columns labels
            pass

        elif token.startswith("labels"):
            token = next(lexer)
            i = 0
            while token not in KEYWORDS:
                if token == 'embedded':
                    row_labels_embedded = True
                    cols_labels_embedded = True
                    break
                else:
                    labels[i] = token.replace('"', '')  # for labels with embedded spaces
                    i += 1
                    try:
                        token = next(lexer)
                    except StopIteration:
                        break
        elif token.startswith('data'):
            break

    data_lines = lines.lower().split("data:", 1)[1]
    # Generate edges
    params = {}
    if cols_labels_embedded:
        # params['names'] = True
        labels = dict(zip(range(0, nc), data_lines.splitlines()[1].split()))
        params['skip_header'] = 2  # First character is \n
    if row_labels_embedded:  # Skip first column
        # TODO rectangular case : labels can differ from rows to columns
        params['usecols'] = range(1, nc + 1)

    if ucinet_format == 'fullmatrix':
        try:
            data_lines = bytes(data_lines, 'utf-8')
        except TypeError:
            pass
        data = genfromtxt(data_lines.splitlines(), case_sensitive=False, **params)
        mat = reshape(data, (max(number_of_nodes, nr), -1))
        G = nx.from_numpy_matrix(mat, create_using=nx.MultiDiGraph())

    elif ucinet_format in ('nodelist1', 'nodelist1b'):  # Since genfromtxt only accepts square matrix...
        s = ''
        for i, line in enumerate(data_lines.splitlines()):
            row = line.split()
            if row:
                if ucinet_format == 'nodelist1b' and row[0] == '0':
                    pass
                else:
                    for neighbor in row[1:]:
                        if ucinet_format == 'nodelist1':
                            source = row[0]
                        else:
                            source = str(i)
                        s += source + ' ' + neighbor + '\n'
        G = nx.parse_edgelist(s.splitlines(), nodetype=int, create_using=nx.MultiDiGraph())

    # Relabel nodes
    if labels:
        G = nx.relabel_nodes(G, labels)
    return G


def get_param(regex, token, lines):
    """
    Get a parameter value in UCINET DL file
    :param regex: string with the regex matching the parameter value
    :param token: token (string) in which we search for the parameter
    :param lines: to iterate through the next tokens
    :return:
    """
    n = token
    query = re.search(regex, n)
    while query is None:
        try:
            n = next(lines)
        except StopIteration:
            raise Exception("Parameter value not recognized")
        query = re.search(regex, n)
    return query.group()
