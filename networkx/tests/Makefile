VPATH=html

.SUFFIXES: .txt .html

.txt.html:
	rst2html.py --stylesheet-path=nx_doctest.css < $< > html/$*.html

# test loading module by module

CORE=	base_DiGraph.txt \
	base_Graph.txt \
	centrality.txt \
	cliques.txt \
	cluster.txt \
	cores.txt \
	hybrid.txt \
	io.txt \
	isomorph.txt \
	operators.txt \
	paths.txt \
	queues.txt \
	search_class.txt \
	search.txt \
	spectrum.txt \
	threshold.txt \
	utils.txt \
	xbase_DiGraph.txt \
	xbase_Graph.txt \
	xbase_PseudoGraph.txt


GENERATORS=	\
	generators_atlas.txt \
	generators_classic.txt \
	generators_atlas.txt \
	generators_classic.txt \
	generators_degree_seq.txt \
	generators_geometric.txt \
	generators_random_graphs.txt \
	generators_small.txt 

DRAWING= \
	layout.txt \
	nx_pydot.txt \
	nx_pylab.txt 


core:
	@echo "Testing NetworkX core modules"
	./test_single.py ${CORE}

generators:
	@echo "Testing graph generators"
	./test_single.py ${GENERATORS}

drawing:
	@echo "Testing drawing"
	./test_single.py ${DRAWING}


all: core generators drawing	


# primary test, all modules loaded first

sourcetest:
	./test_all.py


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
