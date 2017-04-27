#!/usr/bin/env python
''' Checkout gitwash repo into directory and do search replace on name '''

from __future__ import print_function
import os
from os.path import join as pjoin
import shutil
import sys
import re
import glob
import fnmatch
import tempfile
from subprocess import call
from optparse import OptionParser

verbose = False


def clone_repo(url, branch):
    cwd = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    try:
        cmd = 'git clone %s %s' % (url, tmpdir)
        call(cmd, shell=True)
        os.chdir(tmpdir)
        cmd = 'git checkout %s' % branch
        call(cmd, shell=True)
    except:
        shutil.rmtree(tmpdir)
        raise
    finally:
        os.chdir(cwd)
    return tmpdir


def cp_files(in_path, globs, out_path):
    try:
        os.makedirs(out_path)
    except OSError:
        pass
    out_fnames = []
    for in_glob in globs:
        in_glob_path = pjoin(in_path, in_glob)
        for in_fname in glob.glob(in_glob_path):
            out_fname = in_fname.replace(in_path, out_path)
            pth, _ = os.path.split(out_fname)
            if not os.path.isdir(pth):
                os.makedirs(pth)
            shutil.copyfile(in_fname, out_fname)
            out_fnames.append(out_fname)
    return out_fnames


def filename_search_replace(sr_pairs, filename, backup=False):
    ''' Search and replace for expressions in files

    '''
    in_txt = open(filename, 'rt').read(-1)
    out_txt = in_txt[:]
    for in_exp, out_exp in sr_pairs:
        in_exp = re.compile(in_exp)
        out_txt = in_exp.sub(out_exp, out_txt)
    if in_txt == out_txt:
        return False
    open(filename, 'wt').write(out_txt)
    if backup:
        open(filename + '.bak', 'wt').write(in_txt)
    return True


def copy_replace(replace_pairs,
                 repo_path,
                 out_path,
                 cp_globs=('*',),
                 rep_globs=('*',),
                 renames = ()):
    out_fnames = cp_files(repo_path, cp_globs, out_path)
    renames = [(re.compile(in_exp), out_exp) for in_exp, out_exp in renames]
    fnames = []
    for rep_glob in rep_globs:
        fnames += fnmatch.filter(out_fnames, rep_glob)
    if verbose:
        print('\n'.join(fnames))
    for fname in fnames:
        filename_search_replace(replace_pairs, fname, False)
        for in_exp, out_exp in renames:
            new_fname, n = in_exp.subn(out_exp, fname)
            if n:
                os.rename(fname, new_fname)
                break


def make_link_targets(proj_name,
                      user_name,
                      repo_name,
                      known_link_fname,
                      out_link_fname,
                      url=None,
                      ml_url=None):
    """ Check and make link targets

    If url is None or ml_url is None, check if there are links present for these
    in `known_link_fname`.  If not, raise error.  The check is:

    Look for a target `proj_name`.
    Look for a target `proj_name` + ' mailing list'

    Also, look for a target `proj_name` + 'github'.  If this exists, don't write
    this target into the new file below.

    If we are writing any of the url, ml_url, or github address, then write new
    file with these links, of form:

    .. _`proj_name`
    .. _`proj_name`: url
    .. _`proj_name` mailing list: url
    """
    link_contents = open(known_link_fname, 'rt').readlines()
    have_url = not url is None
    have_ml_url = not ml_url is None
    have_gh_url = None
    for line in link_contents:
        if not have_url:
            match = re.match(r'..\s+_`%s`:\s+' % proj_name, line)
            if match:
                have_url = True
        if not have_ml_url:
            match = re.match(r'..\s+_`%s mailing list`:\s+' % proj_name, line)
            if match:
                have_ml_url = True
        if not have_gh_url:
            match = re.match(r'..\s+_`%s github`:\s+' % proj_name, line)
            if match:
                have_gh_url = True
    if not have_url or not have_ml_url:
        raise RuntimeError('Need command line or known project '
                           'and / or mailing list URLs')
    lines = []
    if not url is None:
        lines.append('.. _`%s`: %s\n' % (proj_name, url))
    if not have_gh_url:
        gh_url = 'http://github.com/%s/%s\n' % (user_name, repo_name)
        lines.append('.. _`%s github`: %s\n' % (proj_name, gh_url))
    if not ml_url is None:
        lines.append('.. _`%s mailing list`: %s\n' % (proj_name, ml_url))
    if len(lines) == 0:
        # Nothing to do
        return
    # A neat little header line
    lines = ['.. %s\n' % proj_name] + lines
    out_links = open(out_link_fname, 'wt')
    out_links.writelines(lines)
    out_links.close()


USAGE = ''' <output_directory> <project_name>

If not set with options, the repository name is the same as the <project
name>

If not set with options, the main github user is the same as the
repository name.'''


GITWASH_CENTRAL = 'git://github.com/matthew-brett/gitwash.git'
GITWASH_BRANCH = 'master'


def main():
    parser = OptionParser()
    parser.set_usage(parser.get_usage().strip() + USAGE)
    parser.add_option("--repo-name", dest="repo_name",
                      help="repository name - e.g. nitime",
                      metavar="REPO_NAME")
    parser.add_option("--github-user", dest="main_gh_user",
                      help="github username for main repo - e.g fperez",
                      metavar="MAIN_GH_USER")
    parser.add_option("--gitwash-url", dest="gitwash_url",
                      help="URL to gitwash repository - default %s"
                      % GITWASH_CENTRAL, 
                      default=GITWASH_CENTRAL,
                      metavar="GITWASH_URL")
    parser.add_option("--gitwash-branch", dest="gitwash_branch",
                      help="branch in gitwash repository - default %s"
                      % GITWASH_BRANCH,
                      default=GITWASH_BRANCH,
                      metavar="GITWASH_BRANCH")
    parser.add_option("--source-suffix", dest="source_suffix",
                      help="suffix of ReST source files - default '.rst'",
                      default='.rst',
                      metavar="SOURCE_SUFFIX")
    parser.add_option("--project-url", dest="project_url",
                      help="URL for project web pages",
                      default=None,
                      metavar="PROJECT_URL")
    parser.add_option("--project-ml-url", dest="project_ml_url",
                      help="URL for project mailing list",
                      default=None,
                      metavar="PROJECT_ML_URL")
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
        sys.exit()
    out_path, project_name = args
    if options.repo_name is None:
        options.repo_name = project_name
    if options.main_gh_user is None:
        options.main_gh_user = options.repo_name
    repo_path = clone_repo(options.gitwash_url, options.gitwash_branch)
    try:
        copy_replace((('PROJECTNAME', project_name),
                      ('REPONAME', options.repo_name),
                      ('MAIN_GH_USER', options.main_gh_user)),
                     repo_path,
                     out_path,
                     cp_globs=(pjoin('gitwash', '*'),),
                     rep_globs=('*.rst',),
                     renames=(('\.rst$', options.source_suffix),))
        make_link_targets(project_name,
                          options.main_gh_user,
                          options.repo_name,
                          pjoin(out_path, 'gitwash', 'known_projects.inc'),
                          pjoin(out_path, 'gitwash', 'this_project.inc'),
                          options.project_url,
                          options.project_ml_url)
    finally:
        shutil.rmtree(repo_path)


if __name__ == '__main__':
    main()
