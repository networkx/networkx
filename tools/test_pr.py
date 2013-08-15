#!/usr/bin/env python
"""
This is a script for testing pull requests for NetworkX. It merges the pull
request with current master, installs and tests on all available versions of
Python, and posts the results to Gist if any tests fail.

This script is heavily based on IPython's test_pr.py and friends. See:

http://github.com/ipython/ipython/tree/master/tools

Usage:
    python test_pr.py 742
"""
from __future__ import print_function

import errno
from glob import glob
import io
import json
import os
import pickle
import re
import requests
import shutil
import time
from subprocess import call, check_call, check_output, PIPE, STDOUT, CalledProcessError
import sys

import gh_api
from gh_api import Obj

basedir = os.path.join(os.path.expanduser("~"), ".nx_pr_tests")
repodir = os.path.join(basedir, "networkx")
nx_repository = 'git://github.com/networkx/networkx.git'
nx_http_repository = 'http://github.com/networkx/networkx.git'
gh_project="networkx/networkx"

# TODO Add PyPy support
supported_pythons = ['python2.6', 'python2.7', 'python3.2','python3.3']

# Report missing libraries during tests and number of skipped 
# and passed tests.
missing_libs_re = re.compile('SKIP: (\w+) not available')
def get_missing_libraries(log):
    libs = set()
    for line in log.split('\n'):
        m = missing_libs_re.search(line)
        if m:
            libs.add(m.group(1).lower())
    if libs:
        return ", ".join(libs)

skipped_re = re.compile('SKIP=(\d+)')
def get_skipped(log):
    m = skipped_re.search(log)
    if m:
        return m.group(1)

number_tests_re = re.compile('Ran (\d+) tests in')
def get_number_tests(log):
    m = number_tests_re.search(log)
    if m:
        return m.group(1)


class TestRun(object):
    def __init__(self, pr_num):
        self.unavailable_pythons = []
        self.venvs = []
        self.pr_num = pr_num
        
        self.pr = gh_api.get_pull_request(gh_project, pr_num)
        
        self.setup()
        
        self.results = []
    
    def available_python_versions(self):
        """Get the executable names of available versions of Python on the system.
        """
        for py in supported_pythons:
            try:
                check_call([py, '-c', 'import nose'], stdout=PIPE)
                yield py
            except (OSError, CalledProcessError):
                self.unavailable_pythons.append(py)

    def setup(self):
        """Prepare the repository and virtualenvs."""        
        try:
            os.mkdir(basedir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        os.chdir(basedir)
        
        # Delete virtualenvs and recreate
        for venv in glob('venv-*'):
            shutil.rmtree(venv)
        for py in self.available_python_versions():
            check_call(['virtualenv', '-p', py,
                            '--system-site-packages', 'venv-%s' % py])

            self.venvs.append((py, 'venv-%s' % py))
        
        # Check out and update the repository
        if not os.path.exists('networkx'):
            try :
                check_call(['git', 'clone', nx_repository])
            except CalledProcessError:
                check_call(['git', 'clone', nx_http_repository])
        os.chdir(repodir)
        check_call(['git', 'checkout', 'master'])
        try :
            check_call(['git', 'pull', 'origin', 'master'])
        except CalledProcessError:
            check_call(['git', 'pull', nx_http_repository, 'master'])
        self.master_sha = check_output(['git', 'log', '-1', 
                                        '--format=%h']).decode('ascii').strip()
        os.chdir(basedir)
    
    def get_branch(self):
        repo = self.pr['head']['repo']['clone_url']
        branch = self.pr['head']['ref']
        owner = self.pr['head']['repo']['owner']['login']
        mergeable = self.pr['mergeable']
        
        os.chdir(repodir)
        if mergeable:
            merged_branch = "%s-%s" % (owner, branch)
            # Delete the branch first
            call(['git', 'branch', '-D', merged_branch])
            check_call(['git', 'checkout', '-b', merged_branch])
            check_call(['git', 'pull', '--no-ff', '--no-commit', repo, branch])
            check_call(['git', 'commit', '-m', "merge %s/%s" % (repo, branch)])
        else:
            # Fetch the branch without merging it.
            check_call(['git', 'fetch', repo, branch])
            check_call(['git', 'checkout', 'FETCH_HEAD'])
        os.chdir(basedir)
    
    def markdown_format(self):
        def format_result(result):
            s = "* %s: " % result.py
            if result.passed:
                s += "%s OK (SKIP=%s) Ran %s tests" % \
                                        (ok, result.skipped, result.num_tests)
            else:
                s += "%s Failed, log at %s" % (fail, result.log_url)
            if result.missing_libraries:
                s += " (libraries not available: " + result.missing_libraries + ")"
            return s
        pr_num = self.pr_num
        branch = self.pr['head']['ref']
        branch_url = self.pr['head']['repo']['html_url'] + '/tree/' + branch
        owner = self.pr['head']['repo']['owner']['login']
        mergeable = self.pr['mergeable']
        master_sha = self.master_sha
        branch_sha = self.pr['head']['sha'][:7]
        ok = ':eight_spoked_asterisk:'
        fail = ':red_circle:'

        header = "**NetworkX: Test results for pull request #%s " % pr_num
        header += "([%s '%s' branch](%s))**" % (owner, branch, branch_url)
        if mergeable:
            mrg = "%s This pull request can be merged cleanly " % ok
        else:
            mrg = "%s This pull request **cannot** be merged cleanly " % fail
        mrg += "(commit %s into NetworkX master %s)" % (branch_sha, master_sha)
        lines = [header,
                 mrg,
                 "Platform: " + sys.platform,
                 ""] + \
                [format_result(r) for r in self.results]
        if self.unavailable_pythons:
            lines += ["",
                        "Not available for testing: "  \
                            + ", ".join(self.unavailable_pythons)]
        return "\n".join(lines)
    
    def post_results_comment(self):
        body = self.markdown_format()
        gh_api.post_issue_comment(gh_project, self.pr_num, body)
    
    def print_results(self):
        pr_num = self.pr_num
        branch = self.pr['head']['ref']
        branch_url = self.pr['head']['repo']['html_url'] + '/tree/' + branch
        owner = self.pr['head']['repo']['owner']['login']
        mergeable = self.pr['mergeable']
        master_sha = self.master_sha
        branch_sha = self.pr['head']['sha'][:7]
        
        print("\n")
        print("**NetworkX: Test results for pull request %s " % pr_num,
              "(%s '%s' branch at %s)**" % (owner, branch, branch_url))
        if mergeable:
            mrg = "OK: This pull request can be merged cleanly "
        else:
            mrg = "FAIL: This pull request **cannot** be merged cleanly "
        mrg += "(commit %s into NetworkX master %s)" % (branch_sha, master_sha)
        print(mrg)
        print("Platform:", sys.platform)
        for result in self.results:
            if result.passed:
                print(result.py, ":", "OK (SKIP=%s) Ran %s tests" % \
                                        (result.skipped, result.num_tests))
            else:
                print(result.py, ":", "Failed")
                print("    Test log:", result.get('log_url') or result.log_file)
            if result.missing_libraries:
                print("    Libraries not available:", result.missing_libraries)
        if self.unavailable_pythons:
            print("Not available for testing:", 
                    ", ".join(self.unavailable_pythons))

    def dump_results(self):
        with open(os.path.join(basedir, 'lastresults.pkl'), 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_results():
        with open(os.path.join(basedir, 'lastresults.pkl'), 'rb') as f:
            return pickle.load(f)

    def save_logs(self):
        for result in self.results:
            if not result.passed:
                result_locn = os.path.abspath(os.path.join('venv-%s' % result.py,
                                            self.pr['head']['sha'][:7]+".log"))
                with io.open(result_locn, 'w', encoding='utf-8') as f:
                    f.write(result.log)
            
                result.log_file = result_locn

    def post_logs(self):
        for result in self.results:
            if not result.passed:
                result.log_url = gh_api.post_gist(result.log,
                                                description='NetworkX test log',
                                                filename="results.log", auth=True)
    
    def run(self):
        for py, venv in self.venvs:
            tic = time.time()
            passed, log = run_tests(venv)
            elapsed = int(time.time() - tic)
            print("Ran tests with %s in %is" % (py, elapsed))
            missing_libraries = get_missing_libraries(log)
            skipped = get_skipped(log)
            num_tests = get_number_tests(log)
            
            self.results.append(Obj(py=py,
                                    passed=passed,
                                    log=log,
                                    missing_libraries=missing_libraries,
                                    skipped=skipped,
                                    num_tests=num_tests
                                  )
                               )


def run_tests(venv):
    version = venv.split('-')[1]
    py = os.path.join(basedir, venv, 'bin', 'python')
    os.chdir(repodir)
    # cleanup build-dir
    if os.path.exists('build'):
        shutil.rmtree('build')
    #tic = time.time()
    print ("\nInstalling NetworkX with %s" % py)
    logfile = os.path.join(basedir, venv, 'install.log')
    print ("Install log at %s" % logfile)
    with open(logfile, 'wb') as f:
        check_call([py, 'setup.py', 'install'], stderr=STDOUT, stdout=f)
    #toc = time.time()
    #print ("Installed NetworkX in %.1fs" % (toc-tic))
    os.chdir(basedir)

    # Remove PYTHONPATH if present
    os.environ.pop("PYTHONPATH", None)

    # check that the right NetworkX is imported. Also catch exception if
    # the pull request breaks "import networkx as nx"
    try:
        cmd_file = [py, '-c', 'import networkx as nx; print(nx.__file__)']
        nx_file = check_output(cmd_file, stderr=STDOUT)
    except CalledProcessError as e:
        return False, e.output.decode('utf-8')

    nx_file = nx_file.strip().decode('utf-8')
    if not nx_file.startswith(os.path.join(basedir, venv)):
        msg = u"NetworkX does not appear to be in the venv: %s" % nx_file
        msg += u"\nDo you use setupegg.py develop?"
        print(msg, file=sys.stderr)
        return False, msg

    # Run tests: this is different than in ipython's test_pr, they use 
    # a script for running their tests. It gets installed at 
    # os.path.join(basedir, venv, 'bin', 'iptest')
    print("\nRunning tests with %s ..." % version)
    cmd = [py, '-c', 'import networkx as nx; nx.test(verbosity=2,doctest=True)']
    try:
        return True, check_output(cmd, stderr=STDOUT).decode('utf-8')
    except CalledProcessError as e:
        return False, e.output.decode('utf-8')


def test_pr(num, post_results=True):
    # Get Github authorisation first, so that the user is prompted straight away
    # if their login is needed.
    if post_results:
        gh_api.get_auth_token()
    
    testrun = TestRun(num)
    
    testrun.get_branch()
    
    testrun.run()

    testrun.dump_results()
    
    testrun.save_logs()
    testrun.print_results()
    
    if post_results:
        results_urls = testrun.post_logs()
        testrun.post_results_comment()
        print("(Posted to Github)")
    else:
        post_script = os.path.join(os.path.dirname(sys.argv[0]), "post_pr_test.py")
        print("To post the results to Github, run", post_script)
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Test a pull request for NetworkX")
    parser.add_argument('-p', '--publish', action='store_true',
                        help="Publish the results to Github")
    parser.add_argument('number', type=int, help="The pull request number")
    
    args = parser.parse_args()

    # Test for requests version.
    import requests
    major, minor, rev = map(int, requests.__version__.split('.'))
    if major == 0 and minor < 10:
        print("test_pr.py:")
        print("The requests python library must be version 0.10.0",
                "or above, you have version",
                "{0}.{1}.{2} installed".format(major, minor, rev))
        print()
        sys.exit(1)

    test_pr(args.number, post_results=args.publish)
