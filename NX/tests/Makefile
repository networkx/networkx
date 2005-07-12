VPATH=html

.SUFFIXES: .txt .html

.txt.html:
	rst2html.py --stylesheet-path=nx_doctest.css < $< > html/$*.html

test:
	./test.py

test2:
	./test2.py *.txt

HTML=$(patsubst %.txt,%.html,$(wildcard *.txt))

doc:	directory html

directory:
	mkdir -p html
	cp data/*.png html
	cp data/*.css html


html: $(HTML)


clean:
	/bin/rm -r html
