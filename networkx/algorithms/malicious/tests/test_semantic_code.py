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
    5:      p = p * i\n\
    6: end for')

    # Variable renaming
    file_name = 'basic-code_v1.txt'
    basic_code_v1 = path + file_name
    with open(basic_code_v1, 'w') as f:
        f.write('1: dim a, b, c\n\
    2: a = 5\n\
    3: b = 1\n\
    4: for c = 1 to a do\n\
    5:      b = b * c\n\
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
    6:      p = p * i\n\
    7: end for')

    # Format alternation
    file_name = 'basic-code_v3.txt'
    basic_code_v3 = path + file_name
    with open(basic_code_v3, 'w') as f:
        f.write('1: dim n, p, i # variables initialization\n\
    2: n = 5\n\
    3: p = 1\n\n\
    5: for i = 1 to n do\n\n\
    7:      p = p * i\n\
    8: end for')

    # Statement replacement
    file_name = 'basic-code_v4.txt'
    basic_code_v4 = path + file_name
    with open(basic_code_v4, 'w') as f:
        f.write('1: dim n, p, i # variables initialization\n\
    2: n = 5\n\
    3: p = n/5\n\
    4: for i = 1 to n do\n\
    5:      p = p * i\n\
    6: end for')

    # Spaghetti code
    file_name = 'basic-code_v5.txt'
    basic_code_v5 = path + file_name
    with open(basic_code_v5, 'w') as f:
        f.write('1: dim n, p, i\n\
    2: goto X\n\
    3: Y\n\
    4: for i = 1 to n do\n\
    5:      p = p * i\n\
    6: end for\n\
    7: goto Z\n\
    8: X\n\
    9: n = 5\n\
    10: p = 1\n\
    11: goto Y\n\
    12: Z   ')
    ###############################################

    #stupid code
    file_name = 'stupid-code.txt'
    stupid_code = path + file_name
    with open(stupid_code, 'w') as f:
        f.write('1: int i, j, k\n\
    2: i = 1\n\
    3: j = 0\n\
    4: k = 3\n')

    #variable renaming
    file_name = 'stupid-code_v1.txt'
    stupid_code_v1 = path + file_name
    with open(stupid_code_v1, 'w') as f:
        f.write('1: int a, b, c\n\
    2: a = 1\n\
    3: b = 0\n\
    4: c = 3\n')
    ###############################################

    #fork code
    file_name = 'fork-code.txt'
    fork_code = path + file_name
    with open(fork_code, 'w') as f:
        f.write('1: int a\n\
    2: a = 0\n\
    3: while(a == 0)\n\
    4:      fork()\n')

    #junk code insertion
    file_name = 'fork-code_v1.txt'
    fork_code_v1 = path + file_name
    with open(fork_code_v1, 'w') as f:
        f.write('1: int a, b, i\n\
    2: a = 0\n\
    3: b = 3\n\
    4: while(a == 0)\n\
    5:      for i = 0 to 5\n\
    6:          b = b +1\n\
    7:          fork()')    


    def test_basic_code(self):
        """
        Checks the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """
        
        expected = '1: dim n\n'\
        '2: dim p\n'\
        '3: dim i\n'\
        '4: n=5\n'\
        '5: p=1\n'\
        '6: i=1\n'\
        '7: if i ≤ n then\n'\
        '8:     p=p * i\n'\
        '9:     i=i + 1\n'\
        '10:    goto 7:\n'\
        '11: end if'

        assert convert_code__to_semantic(self.basic_code) == expected

    def test_basic_code_v1(self):
        """
        Checks the first varient (Variable renaming) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        expected = '1: dim a\n'\
            '2: dim b\n'\
            '3: dim c\n'\
            '4: a=5\n'\
            '5: b=1\n'\
            '6: c=1\n'\
            '7: if c ≤ a then\n'\
            '8:     b=b * c\n'\
            '9:     c=c + 1\n'\
            '10:    goto 7:\n'\
            '11: end if'

        assert convert_code__to_semantic(self.basic_code_v1) == expected

    def test_basic_code_v2(self):
        """
        Checks the second varient (Statement reordering) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        """

        expected = '1: dim p\n'\
            '2: dim i\n'\
            '3: p=1\n'\
            '4: dim n\n'\
            '5: n=5\n'\
            '6: i=1\n'\
            '7: if i ≤ n then\n'\
            '8:     p=p * i\n'\
            '9:     i=i + 1\n'\
            '10:    goto 7:\n'\
            '11: end if'

        assert convert_code__to_semantic(self.basic_code_v2) == expected

    def test_basic_code_v3(self):
        """
        Checks the third varient (Format alternation) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        expected = '1: dim n\n'\
            '2: dim p\n'\
            '3: dim i\n'\
            '4: n=5\n'\
            '5: p=1\n'\
            '6: i=1\n'\
            '7: if i ≤ n then\n'\
            '8:     p=p * i\n'\
            '9:     i=i + 1\n'\
            '10:    goto 7:\n'\
            '11: end if'

        assert convert_code__to_semantic(self.basic_code_v3) == expected

    def test_basic_code_v4(self):
        """
        Checks the fourth varient (Statement replacement) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf
        
        """

        expected = '1: dim n\n'\
            '2: dim p\n'\
            '3: dim i\n'\
            '4: n=5\n'\
            '5: p=n/5\n'\
            '6: i=1\n'\
            '7: if i ≤ n then\n'\
            '8:     p=p * i\n'\
            '9:     i=i + 1\n'\
            '10:    goto 7:\n'\
            '11: end if'

        assert convert_code__to_semantic(self.basic_code_v4) == expected


    def test_basic_code_v5(self):
        """
        Checks the fith varient (Spaghetti code) of the basic original code from the paper:
        http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

        """
        expected = '1: dim n\n'\
            '2: dim p\n'\
            '3: dim i\n'\
            '4: goto 10\n'\
            '5: if i ≤ n then\n'\
            '6:     p=p * i\n'\
            '7:     i=i + 1\n'\
            '8:     goto 5\n'\
            '9: end if\n'\
            '10: n=5\n'\
            '11: p=1\n'\
            '12: i=1 * i\n'\
            '13: goto 5 \n'\

        assert convert_code__to_semantic(self.basic_code_v5) == expected

    def test_stupid_code(self):
        """
        Checks the stupid_code example that we made up:
        """
        
        expected = '1: int i\n'\
        '2: int j\n'\
        '3: int k\n'\
        '4: i=1\n'\
        '5: j=0\n'\
        '6: k=3'

        assert convert_code__to_semantic(self.stupid_code) == expected

    def test_stupid_code_v1(self):
        """
        Checks the first variant of stupid_code:
        """
        
        expected = '1: int a\n'\
        '2: int b\n'\
        '3: int c\n'\
        '4: a=1\n'\
        '5: b=0\n'\
        '6: c=3'

        assert convert_code__to_semantic(self.stupid_code_v1) == expected

    def test_fork_code(self):
        """
        Checks the fork_code virus code:
        """
        
        expected = '1: int a\n'\
        '2: a = 0\n'\
        '3: if a == 0\n'\
        '4:     fork()\n'\
        '5:     goto 3\n'\
        '6: end if'

        assert convert_code__to_semantic(self.fork_code) == expected

    def test_fork_code_v1(self):
        """
        Checks the first variant of fork_code virus code:
        """
        
        expected = '1: int a\n'\
        '2: int b\n'\
        '3: int i\n'\
        '4: a = 0\n'\
        '5: i = 0\n'\
        '6: b = 3\n'\
        '7: if a == 0\n'\
        '8:     if i < 5\n'\
        '9:         fork()\n'\
        '10:        i = i + 1\n'\
        '11:        goto 8\n'\
        '12:    end if\n'\
        '13: goto 7\n'\
        '14: end if'

        assert convert_code__to_semantic(self.fork_code_v1) == expected




