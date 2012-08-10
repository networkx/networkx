#!/usr/bin/env python
"""Post the results of a pull request test to Github.
"""
from test_pr import TestRun

testrun = TestRun.load_results()
testrun.post_logs()
testrun.print_results()
testrun.post_results_comment()

print()
print("Posted test results to pull request")
print("  " + testrun.pr['html_url'])
