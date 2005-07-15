VPATH=html

.SUFFIXES: .txt .html

.txt.html:
	rst2html.py --stylesheet-path=nx_doctest.css < $< > html/$*.html

# primary test, all modules loaded first

test:
	./test_all.py

# an alternate way to test, loading module by module

test2:
	./test_single.py *.txt

HTML=$(patsubst %.txt,%.html,$(wildcard *.txt))

# you can make html out of all of these tests with rst2html
# make doc

doc:	directory html

directory:
	mkdir -p html
	cp data/*.png html
	cp data/*.css html


html: $(HTML)


clean:
	/bin/rm -r html
