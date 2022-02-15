# https://github.com/networkx/networkx/pull/2542
# https://github.com/scikit-image/scikit-image/blob/main/tools/generate_release_notes.py
from subprocess import check_output
import sys
import string
import shlex

if len(sys.argv) != 2:
    print("Usage: ./contributors.py tag-of-previous-release")
    sys.exit(-1)

tag = sys.argv[1]


def call(cmd):
    return check_output(shlex.split(cmd), universal_newlines=True).split("\n")


tag_date = call(f"git log -n1 --format='%ci' {tag}")[0]
print(f"Release {tag} was on {tag_date}\n")

merges = call(f"git log --since='{tag_date}' --merges --format='>>>%B' --reverse")
merges = [m for m in merges if m.strip()]
merges = "\n".join(merges).split(">>>")
merges = [m.split("\n")[:2] for m in merges]
merges = [m for m in merges if len(m) == 2 and m[1].strip()]

num_commits = call(f"git rev-list {tag}..HEAD --count")[0]
print(f"A total of {num_commits} changes have been committed.\n")

# Use filter to remove empty strings
commits = filter(None, call(f"git log --since='{tag_date}' --pretty=%s --reverse"))
for c in commits:
    print("- " + c)

print(f"\nIt contained the following {len(merges)} merges:\n")
for (merge, message) in merges:
    if merge.startswith("Merge pull request #"):
        PR = f" ({merge.split()[3]})"
    else:
        PR = ""

    print("- " + message + PR)

print("\nMade by the following committers [alphabetical by last name]:\n")

authors = call(f"git log --since='{tag_date}' --format=%aN")
authors = [a.strip() for a in authors if a.strip()]


def key(author):
    author = [v for v in author.split() if v[0] in string.ascii_letters]
    if len(author) > 0:
        return author[-1]


authors = sorted(set(authors), key=key)

for a in authors:
    print("- " + a)
