#!/usr/bin/env python
import shlex
import subprocess
import sys
import requests

if len(sys.argv) != 2:
    print("Usage: ./contribs.py tag-of-previous-release")
    sys.exit(-1)

tag = sys.argv[1]

def call(cmd):
    return subprocess.check_output(shlex.split(cmd), universal_newlines=True).split('\n')

tag_date = call("git log -n1 --format='%%ci' %s" % tag)[0]
tag_commit = call("git rev-list -n 1 %s" % tag)
print("Release {} was on {}".format(tag, tag_date))
print("Commit {}\n".format(tag_commit[0]))


# Was
# - Cherry pick missing commits (#2535)

# Now
# - Cherry pick missing commits (#2535) [jarrodmillman in 6287d8f9] []
# - Update graphml to care for a number of issues. (#2515) [dschult in 7be0d8f3] [u'Enhancement', u'Maintenance']

url = "https://api.github.com/repos/networkx/networkx/issues/events?state=merged&per_page=100&page={}"
page = 1
while True:

    r = requests.get(url.format(page))
    page += 1

    for item in r.json():
        if item['commit_id'] == tag_commit:
            print(item['commit_id'])
            break
        if item['event'] == 'merged':
            print('- {} (#{}) [{} {}] {}'.format(item['issue']['title'],
                                                    item['issue']['number'],
                                                    item['actor']['login'],
                                                    item['commit_id'][:8],
                                                    ", ".join([l['name'] for l in item['issue']['labels']])))
