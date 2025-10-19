#!/usr/bin/env bash
set -e
for dir in repos*/*/
do
    pushd $dir
    echo $dir
    find . -type f -name '*.py' -print0 | xargs -0 grep '\<nx\.[._A-Za-z0-9]*(' | sed -e 's/.*nx\./nx\./g' -e 's/(.*//g' -e 's/, //g' -e 's/).*//g' -e 's/nx\.//g' | sort > .nx1
    find . -type f -name '*.py' -print0 | xargs -0 grep 'from networkx import ' | sed -e 's/.*from networkx import //g' -e 's/#.*//g' -e 's/, /\n/g' -e 's/ as .*//g' -e 's/).*//g' | sort > .nx2
    find . -type f -name '*.ipynb' -print0 | xargs -0 grep '\<nx\.[._A-Za-z0-9]*(' | sed -e 's/.*nx\./nx\./g' -e 's/(.*//g' -e 's/, //g' -e 's/).*//g' -e 's/nx\.//g' | sort > .nx3
    find . -type f -name '*.ipynb' -print0 | xargs -0 grep 'from networkx import ' | sed -e 's/.*from networkx import //g' -e 's/#.*//g' -e 's/, /\n/g' -e 's/ as .*//g' -e 's/"$//g' | sort > .nx4
    find . -type f -name '*.pyx' -print0 | xargs -0 grep '\<nx\.[._A-Za-z0-9]*(' | sed -e 's/.*nx\./nx\./g' -e 's/(.*//g' -e 's/, //g' -e 's/).*//g' -e 's/nx\.//g' | sort > .nx5
    find . -type f -name '*.pyx' -print0 | xargs -0 grep 'from networkx import ' | sed -e 's/.*from networkx import //g' -e 's/#.*//g' -e 's/, /\n/g' -e 's/ as .*//g' -e 's/).*//g' | sort > .nx6
    # nx1: contains graph classes, networkx exceptions, and full paths such as `nx.foo.bar`
    cat .nx1 .nx2 .nx3 .nx4 .nx5 .nx6 | sort | uniq -c | sort -nr > _nx1
    # nx2: remove graph classes and networkx exceptions, and strip paths to functions
    cat .nx1 .nx2 .nx3 .nx4 .nx5 .nx6 | sed 's/.*\.//g' | grep -v '[A-Z]' | grep -v '__' | awk 'NF' | sort | uniq -c | sort -nr > _nx2
    popd
done
# nx1: contains graph classes, networkx exceptions, and full paths such as `nx.foo.bar`
cat repos*/*/.nx1 repos*/*/.nx2 repos*/*/.nx3 repos*/*/.nx4 repos*/*/.nx5 repos*/*/.nx6 | sort | uniq -c | sort -nr > _nx1
# nx2: remove graph classes and networkx exceptions, and strip paths to functions
cat repos*/*/.nx1 repos*/*/.nx2 repos*/*/.nx3 repos*/*/.nx4 repos*/*/.nx5 repos*/*/.nx6 | sed 's/.*\.//g' | grep -v '[A-Z]' | grep -v '__' | awk 'NF' | sort | uniq -c | sort -nr > _nx2
# nx3: how many projects use each function
cat repos*/*/_nx2 | awk '{print $2}' | sort | uniq -c | sort -nr > _nx3
