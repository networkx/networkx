VPATH=html

.SUFFIXES: .txt .html

.txt.html:
	rst2html.py --stylesheet-path=nx_doctest.css < $< > html/$*.html

test:
	python test.py


HTML=$(patsubst %.txt,%.html,$(wildcard *.txt))

# you can make html out of all of these tests with rst2html
# type make doc

doc:	directory html

directory:
	mkdir -p html
	cp data/*.png html
	cp data/*.css html


html: $(HTML)


clean:
	/bin/rm -r html
