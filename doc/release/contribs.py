#!/usr/bin/env python
# https://github.com/scikit-image/scikit-image/blob/master/doc/release/contribs.py
import subprocess
import sys
import string
import shlex

if len(sys.argv) != 2:
    print("Usage: ./contributors.py tag-of-previous-release")
    sys.exit(-1)

tag = sys.argv[1]

def call(cmd):
    return subprocess.check_output(shlex.split(cmd), universal_newlines=True).split('\n')

tag_date = call("git log -n1 --format='%%ci' %s" % tag)[0]
print("Release %s was on %s\n" % (tag, tag_date))

merges = call("git log --since='%s' --merges --format='>>>%%B' --reverse" % tag_date)
merges = [m for m in merges if m.strip()]
merges = '\n'.join(merges).split('>>>')
merges = [m.split('\n')[:2] for m in merges]
merges = [m for m in merges if len(m) == 2 and m[1].strip()]

num_commits = call("git rev-list %s..HEAD --count" % tag)[0]
print("A total of %s changes have been committed.\n" % num_commits)

print("It contained the following %d merges:\n" % len(merges))
for (merge, message) in merges:
    if merge.startswith('Merge pull request #'):
        PR = ' (%s)' % merge.split()[3]
    else:
        PR = ''

    print('- ' + message + PR)

print("\nMade by the following committers [alphabetical by last name]:\n")

authors = call("git log --since='%s' --format=%%aN" % tag_date)
authors = [a.strip() for a in authors if a.strip()]

def key(author):
    author = [v for v in author.split() if v[0] in string.ascii_letters]
    if len(author) > 0:
        return author[-1]

authors = sorted(set(authors), key=key)

for a in authors:
    print('- ' + a)
