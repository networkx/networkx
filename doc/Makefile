# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source

.PHONY: help clean html dirhtml pickle json htmlhelp qthelp latex changes linkcheck doctest epub

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  dirhtml   to make HTML files named index.html in directories"
	@echo "  pickle    to make pickle files"
	@echo "  epub       to make an epub"
	@echo "  json      to make JSON files"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  qthelp    to make HTML files and a qthelp project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"
	@echo "  doctest   to run all doctests embedded in the documentation (if enabled)"


clean:
	-rm -rf build/* source/reference/generated/* source/examples/* source/static/examples


generate: build/generate-stamp
build/generate-stamp: $(wildcard source/reference/*.rst)
	mkdir -p build
	./make_gallery.py 
	./make_examples_rst.py ../examples source
	touch build/generate-stamp


dist: html
	test -d build/latex || make latex
	make -C build/latex all-pdf
	-rm -rf build/dist
	(cd build/html; cp -r . ../../build/dist)
	-rm -f build/dist/_downloads/*
	(cd build/html && zip -9r ../dist/_downloads/networkx-documentation.zip .)
	cp build/latex/*.pdf build/dist/_downloads
	(cd build/dist && ln -s _downloads/* .)
	(cd build/dist && tar czf ../dist.tar.gz .)


html: generate
	touch source/networkx_tutorial.pdf	
	touch source/networkx_reference.pdf	
	touch source/networkx-documentation.zip
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) build/html
	@echo
	@echo "Build finished. The HTML pages are in build/html."

dirhtml: generate
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) build/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in build/dirhtml."

pickle: generate
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) build/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

json: generate
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) build/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp: generate
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) build/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in build/htmlhelp."

qthelp: generate
	$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS) build/qthelp
	@echo
	@echo "Build finished; now you can run "qcollectiongenerator" with the" \
	      ".qhcp project file in build/qthelp, like this:"
	@echo "# qcollectiongenerator build/qthelp/test.qhcp"
	@echo "To view the help file:"
	@echo "# assistant -collectionFile build/qthelp/test.qhc"

epub:
	$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) build/epub
	@echo
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."


latex: generate
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) build/latex
	@echo
	@echo "Build finished; the LaTeX files are in build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) build/changes
	@echo
	@echo "The overview file is in build/changes."

linkcheck: generate
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in build/linkcheck/output.txt."

doctest: generate
	$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) build/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in build/doctest/output.txt."
