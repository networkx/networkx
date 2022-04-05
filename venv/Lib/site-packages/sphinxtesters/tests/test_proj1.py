""" Tests for proj1 build using sphinx extensions """

from os.path import (join as pjoin, dirname, isdir, exists, splitext)

from sphinxtesters import ModifiedPageBuilder

HERE = dirname(__file__)


class Proj1Builder(ModifiedPageBuilder):
    """ Build using 'proj1' directory as template to modify
    """

    page_source_template = pjoin(HERE, 'proj1')

    # default_page used in 'replace_page' class method
    default_page = 'a_page.rst'


class TestProj1(Proj1Builder):

    def test_basic_build(self):
        assert isdir(self.out_dir)
        assert isdir(self.doctree_dir)
        doctree = self.get_doctree(splitext(self.default_page)[0])
        assert len(doctree.document) == 1
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>A section</title>\n'
            '<paragraph>Some text.</paragraph>\n'
            '<paragraph>More text.</paragraph>\n'
            '<paragraph>Text is endless.</paragraph>')
        assert doctree_str == expected
        assert exists(pjoin(self.doctree_dir, 'index.doctree'))
