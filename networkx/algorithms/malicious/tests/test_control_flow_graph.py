"""
    Tests for control_flow_graph(CFG).
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.control_flow_graph import build_CFG


class TestControlFlowGraph:
    path = '/Users/liozakirav/Documents/computer-science/fourth-year/Research-Algorithms/networkx/networkx/algorithms/malicious/code-examples/'
    file_name = 'basic-code.txt'
    basic_code = path + file_name
    with open(basic_code, 'w') as f:
        f.write('1: dim n\n\
        2: dim p\n\
        3: dim i\n\
        4: n=5\n\
        5: p=1\n\
        6: i=1\n\
        7: if i ≤ n then\n\
        8:     p=p * i\n\
        9:     i=i + 1\n\
        10:    goto 7:\n\
        11: end if')

    # Variable renaming
    file_name = 'basic-code_v1.txt'
    basic_code_v1 = path + file_name
    with open(basic_code_v1, 'w') as f:
        f.write('1: dim a\n\
        2: dim b\n\
        3: dim c\n\
        4: a=5\n\
        5: b=1\n\
        6: c=1\n\
        7: if c ≤ a then\n\
        8:     b=b * c\n\
        9:     c=c + 1\n\
        10:    goto 7:\n\
        11: end if')


    # Statement reordering
    file_name = 'basic-code_v2.txt'
    basic_code_v2 = path + file_name
    with open(basic_code_v2, 'w') as f:
        f.write('1: dim p\n\
        2: dim i\n\
        3: p=1\n\
        4: dim n\n\
        5: n=5\n\
        6: i=1\n\
        7: if i ≤ n then\n\
        8:     p=p * i\n\
        9:     i=i + 1\n\
        10:    goto 7:\n\
        11: end if')

    # Format alternation
    file_name = 'basic-code_v3.txt'
    basic_code_v3 = path + file_name
    with open(basic_code_v3, 'w') as f:
        f.write('1: dim n\n\
        2: dim p\n\
        3: dim i\n\
        4: n=5\n\
        5: p=1\n\
        6: i=1\n\
        7: if i ≤ n then\n\
        8:     p=p * i\n\
        9:     i=i + 1\n\
        10:    goto 7:\n\
        11: end if')

    # Statement replacement
    file_name = 'basic-code_v4.txt'
    basic_code_v4 = path + file_name
    with open(basic_code_v4, 'w') as f:
        f.write('1: dim n\n\
        2: dim p\n\
        3: dim i\n\
        4: n=5\n\
        5: p=n/5\n\
        6: i=1\n\
        7: if i ≤ n then\n\
        8:     p=p * i\n\
        9:     i=i + 1\n\
        10:    goto 7:\n\
        11: end if')

    # Spaghetti code
    file_name = 'basic-code_v5.txt'
    basic_code_v5 = path + file_name
    with open(basic_code_v5, 'w') as f:
        f.write('1: dim n\n\
        2: dim p\n\
        3: dim i\n\
        4: goto 10\n\
        5: if i ≤ n then\n\
        6:      p=p * i\n\
        7:      i=i + 1\n\
        8:      goto 5\n\
        9:end if\n\
        10:n=5\n\
        11:p=1\n\
        12:i=1\n\
        13:goto 5')
    ###############################################

    #stupid code
    file_name = 'stupid-code.txt'
    stupid_code = path + file_name
    with open(stupid_code, 'w') as f:
        f.write('1: int i\n\
    2: int j\n\
    3: int k\n\
    4: i = 1\n\
    5: j = 0\n\
    6: k = 3\n')

    #variable renaming
    file_name = 'stupid-code_v1.txt'
    stupid_code_v1 = path + file_name
    with open(stupid_code_v1, 'w') as f:
        f.write('1: int a\n\
    2: int b\n\
    3: int c\n\
    4: a = 1\n\
    5: b = 0\n\
    6: c = 3\n')
    ###############################################

    #fork code
    file_name = 'fork-code.txt'
    fork_code = path + file_name
    with open(fork_code, 'w') as f:
        f.write('1: int a\n\
    2: a = 0\n\
    3: if a == 0\n\
    4:      fork()\n\
    5:      goto 3\n\
    4: end if')

    #junk code insertion
    file_name = 'fork-code_v1.txt'
    fork_code_v1 = path + file_name
    with open(fork_code_v1, 'w') as f:
        f.write('1: int a\n\
    2: int b\n\
    3: int i\n\
    4: a = 0\n\
    5: i = 0\n\
    6: b = 3\n\
    7: if a == 0\n\
    8:     if i < 5\n\
    9:          fork()\n\
    10:          i = i + 1\n\
    11:          goto 8\n\
    12:    end if\n\
    13 goto 7\n\
    14:end if')  


    def test_basic_code(self):
        """
        Checks the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_basic_code_v1(self):
        """
        Checks the first varient (Variable renaming) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_basic_code_v2(self):
        """
        Checks the second varient (Statement reordering) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_basic_code_v3(self):
        """
        Checks the third varient (Format alternation) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_basic_code_v4(self):
        """
        Checks the fourth varient (Statement replacement) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,12))
        edges = [(edge, edge+1) for edge in range(1, 11)]
        edges.append((7,11))
        edges.append((10, 7))
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG


    def test_basic_code_v5(self):
        """
        Checks the fith varient (Spaghetti code) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

        """
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,14))
        CFG.add_edge_from((1,2),(2,3),(3,4),(4,10),(10,11),(11,12),(12,13),(13,5),(5,6),(6,7),(7,8),(8,5)(8,9),(5,9))

        assert build_CFG(self.basic_code) == CFG

    def test_stupid_code(self):
        """
        Checks the stupid_code example that we made up:
        """
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,7))
        edges = [(edge, edge+1) for edge in range(1, 7)]
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_stupid_code_v1(self):
        """
        Checks the first variant of stupid_code:
        """
        
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,7))
        edges = [(edge, edge+1) for edge in range(1, 7)]
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_fork_code(self):
        """
        Checks the fork_code virus code:
        """
        
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,7))
        edges = [(edge, edge+1) for edge in range(1, 5)]
        edges.append((5,3),(3,6))
        CFG.add_edges_from(edges)

        assert build_CFG(self.basic_code) == CFG

    def test_fork_code_v1(self):
        """
        Checks the first variant of fork_code virus code:
        """
        
        CFG = nx.diGraph()
        CFG.add_nodes_from(range(1,15))
        edges = [(edge, edge+1) for edge in range(1, 15)]
        edges.append((8,12),(11,8),(13,7),(7,14))
        CFG.add_edges_from(edges)
        assert build_CFG(self.basic_code) == CFG





