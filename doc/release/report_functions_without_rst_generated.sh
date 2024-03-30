#!/bin/bash
# Authored-by: James Trimble <james.trimble@yahoo.co.uk> 
# expanded beyond /algorithms/ by Dan Schult <dschult@colgate.edu>

echo ALGORITHMS
find networkx/algorithms -name "*.py" | xargs cat | tr -d ' \n' | grep -o '__all__=\[["a-z0-9_,]*\]' | grep -o '"[a-z0-9_]*"' | tr -d '"' | sort | uniq > tmp_funcs.txt
cat doc/reference/algorithms/*.rst | tr -d ' ' | sort | uniq > tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt > functions_possibly_missing_from_doc.txt
for f in $(cat functions_possibly_missing_from_doc.txt); do echo $f; grep -l -r "def ${f}" networkx/algorithms | grep -v ".pyc" | sed 's/^/  /'; done

echo GENERATORS
find networkx/generators -name "*.py" | xargs cat | tr -d ' \n' | grep -o '__all__=\[["a-z0-9_,]*\]' | grep -o '"[a-z0-9_]*"' | tr -d '"' | sort | uniq > tmp_funcs.txt
cat doc/reference/generators.rst | tr -d ' ' | sort | uniq > tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt > functions_possibly_missing_from_doc.txt
for f in $(cat functions_possibly_missing_from_doc.txt); do echo $f; grep -l -r "def ${f}" networkx/generators | grep -v ".pyc" | sed 's/^/  /'; done

echo LINALG
find networkx/linalg -name "*.py" | xargs cat | tr -d ' \n' | grep -o '__all__=\[["a-z0-9_,]*\]' | grep -o '"[a-z0-9_]*"' | tr -d '"' | sort | uniq > tmp_funcs.txt
cat doc/reference/linalg.rst | tr -d ' ' | sort | uniq > tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt > functions_possibly_missing_from_doc.txt
for f in $(cat functions_possibly_missing_from_doc.txt); do echo $f; grep -l -r "def ${f}" networkx/linalg | grep -v ".pyc" | sed 's/^/  /'; done

echo CLASSES
find networkx/classes -name "*.py" | xargs cat | tr -d ' \n' | grep -o '__all__=\[["a-z0-9_,]*\]' | grep -o '"[a-z0-9_]*"' | tr -d '"' | sort | uniq > tmp_funcs.txt
cat doc/reference/{filters,functions,classes/*}.rst | tr -d ' ' | sort | uniq > tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt > functions_possibly_missing_from_doc.txt
for f in $(cat functions_possibly_missing_from_doc.txt); do echo $f; grep -l -r "def ${f}" networkx/classes | grep -v ".pyc" | sed 's/^/  /'; done

echo READWRITE
find networkx/readwrite -name "*.py" | xargs cat | tr -d ' \n' | grep -o '__all__=\[["a-z0-9_,]*\]' | grep -o '"[a-z0-9_]*"' | tr -d '"' | sort | uniq > tmp_funcs.txt
cat doc/reference/readwrite/*.rst | tr -d ' ' | sort | uniq > tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt
comm -2 -3 tmp_funcs.txt tmp_doc.txt > functions_possibly_missing_from_doc.txt
for f in $(cat functions_possibly_missing_from_doc.txt); do echo $f; grep -l -r "def ${f}" networkx/readwrite | grep -v ".pyc" | sed 's/^/  /'; done
