"""
    Tests for semantic_code.
"""

import pytest
import networkx as nx
from networkx.algorithms.malicious.semantic_code import convert_code__to_semantic


class TestSemanticCode:
    path = '/Users/liozakirav/Documents/computer-science/fourth-year/Research-Algorithms/networkx/networkx/algorithms/malicious/code-examples/'
    file_name = 'basic-code.txt'
    basic_code = path + file_name
    with open(basic_code, 'w') as f:
        f.write('1: dim n, p, i\n\
    2: n = 5\n\
    3: p = 1\n\
    4: for i = 1 to n do\n\
    5: p = p * i\n\
    6: end for')

    # Variable renaming
    file_name = 'basic-code_v1.txt'
    basic_code_v1 = path + file_name
    with open(basic_code_v1, 'w') as f:
        f.write('1: dim a, b, c\n\
    2: a = 5\n\
    3: b = 1\n\
    4: for c = 1 to a do\n\
    5: b = b * c\n\
    6: end for')


    # Statement reordering
    file_name = 'basic-code_v2.txt'
    basic_code_v2 = path + file_name
    with open(basic_code_v2, 'w') as f:
        f.write('1: dim p, i\n\
    2: p = 1\n\
    3: dim n\n\
    4: n = 5\
    5: for i = 1 to n do\n\
    6: p = p * i\n\
    7: end for')

    # Format alternation
    file_name = 'basic-code_v3.txt'
    basic_code_v3 = path + file_name
    with open(basic_code_v3, 'w') as f:
        f.write('1: dim n, p, i # variables initialization\n\
    2: n = 5\n\
    3: p = 1\n\n\
    5: for i = 1 to n do\n\n\
    7: p = p * i\n\
    8: end for')

    def test_basic_code(self):
        """
        Cheks the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        
        expected = '1: dim n\n'\
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

        assert convert_code__to_semantic(self.basic_code) == expected

    def test_basic_code_v1(self):
        """
        Cheks the first varient (Variable renaming) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        expected = '1: dim a\n'\
            '2: dim b\n'\
            '3: dim c\n'\
            '4: a=5\n'\
            '5: b=1\n'\
            '6: c=1\n'\
            '7: if c ≤ a then\n'\
            '8: b=b * c\n'\
            '9: c=c + 1\n'\
            '10: goto 7:\n'\
            '11: end if'

        assert convert_code__to_semantic(self.basic_code_v1) == expected

    def test_basic_code_v2(self):
        """
        Cheks the second varient (Statement reordering) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        expected = '1: dim p\n'\
            '2: dim i\n'\
            '3: p=1\n'\
            '4: dim n\n'\
            '5: n=5\n'\
            '6: i=1\n'\
            '7: if i ≤ n then\n'\
            '8: p=p * i\n'\
            '9: i=i + 1\n'\
            '10: goto 7:\n'\
            '11: end if'

        assert convert_code__to_semantic(self.basic_code_v2) == expected

    def test_basic_code_v3(self):
        """
        Cheks the third varient (Format alternation) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        expected = '1: dim n\n'\
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

        assert convert_code__to_semantic(self.basic_code) == expected


