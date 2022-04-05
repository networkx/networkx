""" Test TempApp, TestApp classes
"""

from os.path import (join as pjoin, isdir)

from sphinxtesters.sphinxutils import TempApp


def assert_contents_equal(fname, contents, mode='t'):
    with open(fname, 'r' + mode) as fobj:
        f_contents = fobj.read()
    assert f_contents == contents


def test_tempapp():
    rst_txt = 'A simple page'
    app = TempApp(rst_txt)
    app.build()
    app_path = app.tmp_dir
    index_fname = pjoin(app_path, app.index_root + '.rst')
    assert_contents_equal(index_fname, rst_txt)
    assert_contents_equal(pjoin(app_path, 'conf.py'), '')
    app.cleanup()
    assert not isdir(app_path)


def test_tempapp_master_doc():
    rst_txt = 'A simple page'
    conf_txt = 'master_doc = "my_master"'
    app = TempApp(rst_txt, conf_txt)
    app.build()
    app_path = app.tmp_dir
    index_fname = pjoin(app_path, 'my_master.rst')
    assert_contents_equal(index_fname, rst_txt)
    assert_contents_equal(pjoin(app_path, 'conf.py'), conf_txt)
    app.cleanup()
    assert not isdir(app_path)
