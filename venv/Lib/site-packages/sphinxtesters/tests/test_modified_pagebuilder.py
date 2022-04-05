""" Test ModifiedPageBuilder
"""

from io import StringIO
from os.path import dirname, join as pjoin

from sphinxtesters.sphinxutils import ModifiedPageBuilder
from sphinxtesters.tmpdirs import in_dtemp

import pytest

HERE = dirname(__file__)
PROJ1 = pjoin(HERE, 'proj1')


class TestModifiedPageBuilder(ModifiedPageBuilder):
    # Replace page with file-like object

    page_source_template = PROJ1
    default_page = 'a_page'
    _new_page = u"""
Fancy title
+++++++++++

Compelling text
"""

    @classmethod
    def modify_source(cls):
        page_fobj = StringIO(cls._new_page)
        cls.replace_page(page_fobj)

    def test_a_build(self):
        doctree = self.get_doctree(self.default_page)
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>Fancy title</title>\n'
            '<paragraph>Compelling text</paragraph>')
        assert doctree_str == expected


class TestFModifiedPageBuilder(TestModifiedPageBuilder):
    # Replace page, but with filename

    @classmethod
    def modify_source(cls):
        with in_dtemp():
            with open('test.txt', 'wt') as fobj:
                fobj.write(cls._new_page)
            cls.replace_page('test.txt')


def test_bad_pagebuilder():
    """ Tests that warning on build generates error
    """

    class TestBadPageBuilder(TestModifiedPageBuilder):

        _new_page = u"""
Fancy title
+++++++++++

:ref:`not-a-target`
"""

    with pytest.raises(RuntimeError):
        TestBadPageBuilder.setup_class()


class TestAppendConf(TestModifiedPageBuilder):
    # Test append_conf method

    @classmethod
    def modify_source(cls):
        super(TestAppendConf, cls).modify_source()
        cls.append_conf('# Spurious comment')

    def test_append_conf(self):
        with open(pjoin(PROJ1, 'conf.py'), 'rt') as fobj:
            before_contents = fobj.read()
        with open(pjoin(self.page_source, 'conf.py'), 'rt') as fobj:
            after_contents = fobj.read()
        assert (after_contents == before_contents + '# Spurious comment')


class TestAddPage(TestModifiedPageBuilder):
    # Test ability to add a page

    @classmethod
    def modify_source(cls):
        page_fobj = StringIO(cls._new_page)
        cls.add_page(page_fobj, 'b_page')

    def test_a_build(self):
        doctree = self.get_doctree(self.default_page)
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>A section</title>\n'
            '<paragraph>Some text.</paragraph>\n'
            '<paragraph>More text.</paragraph>\n'
            '<paragraph>Text is endless.</paragraph>')
        assert doctree_str == expected
        expected = (
            '<title>Fancy title</title>\n'
            '<paragraph>Compelling text</paragraph>')
        doctree = self.get_doctree('b_page')
        doctree_str = self.doctree2str(doctree)
        assert doctree_str == expected


class TestAddFPage(TestAddPage):
    # Test ability to add a page as filename

    @classmethod
    def modify_source(cls):
        with in_dtemp():
            with open('test.txt', 'wt') as fobj:
                fobj.write(cls._new_page)
            cls.add_page('test.txt', 'b_page')
