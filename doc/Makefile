
VPATH=html

.SUFFIXES: .txt .html 

.txt.html:
	rst2html.py --stylesheet-path=data/nx_doc.css < $< > html/$*.html
#	rst2html.py < $< > html/$*.html

.txt.tex:
	rst2latex.py < $< > pdf/$*.tex
	(cd pdf; pdflatex  $*.tex)

all:  html pdf

html: directory htmldoc htmlreference

htmldoc:	Readme.html Legal.html Tutorial.html Quick_ref.html Examples.html Drawing.html Credits.html News.html
	cp -f data/nx_doc.css html
	cp -f data/pydot-quote.patch html
	cp -f data/default.css html/nx_doc.css
	cp -f data/basic-s.png html
	cp -f data/as.png html
	cp -f data/tetrahedral-s.png html
	(cd html; ln -sf Readme.html index.html)

pdf: pdfdoc pdfreference

pdfdoc: directory 
	VPATH=pdf
	cp -f data/basic-s.png pdf
	cp -f data/as.png pdf
	cp -f data/tetrahedral-s.png pdf
	$(MAKE) pdfdocreal
	/bin/rm pdf/*.aux pdf/*.log pdf/*.out pdf/*.tex

pdfdocreal: Readme.tex Legal.tex Tutorial.tex Examples.tex Quick_ref.tex Drawing.tex Credits.tex News.tex

htmlreference:  FORCE
	(cd ../;epydoc -o ./doc/html/Reference/ --ignore-param-mismatch --docformat restructuredtext --css doc/data/blue_restructured.css --no-private -v --inheritance listed -n networkx networkx)

pdfreference:  FORCE
	(cd ../;epydoc --pdf -o ./doc/pdf/Reference/ --ignore-param-mismatch --docformat restructuredtext -v --inheritance listed -n networkx networkx)
	mv pdf/Reference/api.pdf pdf/networkx_api.pdf
	/bin/rm -r pdf/Reference

directory:
	mkdir -p html
	mkdir -p pdf


Drawing.html: Menu.txt

Credits.html: Menu.txt

Readme.html: Menu.txt

Legal.html: Menu.txt

Tutorial.html: Menu.txt

Examples.html: Menu.txt

Quick_ref.html: Menu.txt

Drawing.html: Menu.txt

News.html: Menu.txt

test:
	./test.py *.txt

FORCE:

clean:
	/bin/rm -rf html
	/bin/rm -rf pdf
	/bin/rm tetrahedral.*
