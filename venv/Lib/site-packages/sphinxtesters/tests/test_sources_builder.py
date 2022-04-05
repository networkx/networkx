""" Tests for SourcesBuilder utility
"""

from os.path import (join as pjoin, isdir, exists, dirname)

from sphinxtesters import SourcesBuilder

import pytest

HERE = dirname(__file__)
PROJ1 = pjoin(HERE, 'proj1')

A_PAGE = """\
#########
A section
#########

Some text.

More text.

Text is endless."""

A_DOCTREE = """\
<title>A section</title>
<paragraph>Some text.</paragraph>
<paragraph>More text.</paragraph>
<paragraph>Text is endless.</paragraph>"""

B_PAGE = """\
###############
Another section
###############

Some more text."""

B_DOCTREE = """\
<title>Another section</title>
<paragraph>Some more text.</paragraph>"""

NO_TITLE_PAGE = """\
Just text, no title."""

NO_TITLE_DOCTREE = """\
Just text, no title."""


class CheckSources(SourcesBuilder):
    """ Template for testing some pages
    """

    def test_structure(self):
        assert isdir(self.out_dir)
        assert isdir(self.doctree_dir)
        index_fname = pjoin(self.doctree_dir, self.index_root + '.doctree')
        assert exists(index_fname)
        for page_name in self.rst_sources:
            assert exists(pjoin(self.doctree_dir,
                                page_name + '.doctree'))

    def check_page(self, page_name, expected_doctree):
        doctree = self.get_doctree(page_name)
        assert len(doctree.document) == 1
        doctree_str = self.doctree2str(doctree)
        assert doctree_str == expected_doctree


class TestAPage(CheckSources):

    rst_sources = dict(a_page=A_PAGE)
    expected_doctree = A_DOCTREE

    def test_page(self):
        page_name = list(self.rst_sources)[0]
        self.check_page(page_name, self.expected_doctree)


class TestBPage(TestAPage):

    rst_sources = dict(b_page=B_PAGE)
    expected_doctree = B_DOCTREE


class TestNoTitlePage(TestAPage):

    rst_sources = dict(no_title_page=NO_TITLE_PAGE)
    expected_doctree = NO_TITLE_DOCTREE


class TestTemplateSourcesBuilder(SourcesBuilder):
    # Replace page using rst_sources

    page_source_template = PROJ1
    rst_sources = {'a_page': u"""
Fancy title
+++++++++++

Compelling text
"""}

    def test_a_build(self):
        doctree = self.get_doctree('a_page')
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>Fancy title</title>\n'
            '<paragraph>Compelling text</paragraph>')
        assert doctree_str == expected


def test_bad_souurcesbuilder_with_template():
    """ Tests that warning on build generates error
    """

    class TestBadSourcesBuilder(TestTemplateSourcesBuilder):

        rst_sources = {'a_page': u"""
Fancy title
+++++++++++

:ref:`not-a-target`
"""}

    with pytest.raises(RuntimeError):
        TestBadSourcesBuilder.setup_class()


class TestAppendConf(TestTemplateSourcesBuilder):
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


class TestNoTocTree(SourcesBuilder):
    # Test no toctree write
    rst_sources = dict(a_page=A_PAGE)

    def test_master(self):
        doctree = self.get_doctree(self.index_root)
        assert doctree.document.astext() == ''
        assert len(doctree.document.children) == 0


class TestTocTree(TestNoTocTree):
    # Test toctree write to master_doc

    toctree_pages = ['a_page']
    master_name = TestNoTocTree.index_root

    def test_master(self):
        doctree = self.get_doctree(self.master_name)
        assert len(doctree.document.children) == 1
        toctree = doctree.document.children[0]
        entries = toctree[0]['entries']
        assert entries == [(None, 'a_page')]


class TestFooTocTree(TestTocTree):
    # Test toctree write to another master_doc

    conf_source = 'master_doc = "foo"'
    master_name = 'foo'
