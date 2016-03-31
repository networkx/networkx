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
    yield 'dl n=%i format=fullmatrix' % n

    yield 'data:'

    for node in G:
        neighbors = list(G.neighbors(node))
        s = ''
        for node2 in G:
            if node2 in neighbors:
                s += '1 '
            else:
                s += '0 '
        yield s[:-1]  # Remove last space


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
            s += line
        lines = s

    lines = shlex.shlex(lines)
    lines.whitespace += ','
    lines.whitespace_split = True

    number_of_nodes = 0
    number_of_matrices = 0
    nr = 0  # number of rows (rectangular matrix)
    nc = 0  # number of columns (rectangular matrix)
    ucinet_format = 'fullmatrix'  # Format by default
    labels = []  # Contains labels of nodes

    KEYWORDS = ('format', 'data:', 'labels:')  # TODO remove ':' in keywords

    while lines:
        try:
            token = next(lines).lower()
        except StopIteration:
            break
        # print "Token : %s" % token
        if token.startswith('n'):
            if token.startswith('nr'):
                nr = int(get_param("\d+", token, lines))
                number_of_nodes = max(nr, nc)
            elif token.startswith('nc'):
                nc = int(get_param("\d+", token, lines))
                number_of_nodes = max(nr, nc)
            elif token.startswith('nm'):
                number_of_matrices = int(get_param("\d+", token, lines))
            else:
                number_of_nodes = int(get_param("\d+", token, lines))

        elif token.startswith("format"):
            ucinet_format = get_param("fullmatrix|upperhalf|lowerhalf|nodelist1|nodelist2|nodelist1b|\
                                        edgelist1|edgelist2|blockmatrix|partition", token, lines)

        elif token.startswith("labels"):
            token = next(lines).lower()
            i = 0
            while token not in KEYWORDS:
                labels.append(token)
                i += 1
                try:
                    token = next(lines).lower()
                except StopIteration:
                    break

        if token.startswith('data'):  # data
            # Generate nodes
            if not labels:
                labels = range(0, number_of_nodes)
            G.add_nodes_from(labels)

            # Generate edges
            j = 0
            while lines:
                try:
                    token = next(lines).lower()
                except StopIteration:
                    break
                if ucinet_format == 'fullmatrix':
                    i = j / number_of_nodes
                    k = j % number_of_nodes
                    source = labels[i]
                    target = labels[k]
                    if token != '0':
                        if token != '1':  # Weighted edge
                            G.add_weighted_edges_from([(source, target, float(token))])
                        else:
                            G.add_edge(source, target)
                else:
                    raise NotImplementedError("UCINET DL data format %s not yet implemented in Networkx"
                                            % ucinet_format)
                j += 1
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
        n = next(lines).lower()
        query = re.search(regex, n)
    return query.group()
