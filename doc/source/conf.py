# -*- coding: utf-8 -*-
#
# Sphinx documentation build configuration file, created by
# sphinx-quickstart.py on Sat Mar  8 21:47:50 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import sys, os, re

# Check Sphinx version
import sphinx
if sphinx.__version__ < "1.0.1":
    raise RuntimeError("Sphinx 1.0.1 or newer required")

# If your extensions are in another directory, add it here.
sys.path.append(os.path.abspath('../sphinxext'))

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.addons.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 
              'sphinx.ext.pngmath',
              'sphinx.ext.viewcode',
#              'sphinx.ext.mathjax',
              'numpydoc',
              'sphinx.ext.coverage',
              'sphinx.ext.autosummary','sphinx.ext.todo','sphinx.ext.doctest',
              'sphinx.ext.intersphinx', 'customroles']

# generate autosummary pages
autosummary_generate=True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates','../rst_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.                                      
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'contents'

# General substitutions.
project = 'NetworkX'
copyright = '2010, NetworkX Developers'

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
import networkx
version = networkx.__version__
# The full version, including dev info
release = networkx.__version__.replace('_','')

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
# unused_docs = ['examples/index']

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).

add_module_names = False

# show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
#pygments_style = 'friendly'
pygments_style = 'sphinx'

# A list of prefixs that are ignored when creating the module index. (new in Sphinx 0.6)
modindex_common_prefix=['networkx.']

doctest_global_setup="import networkx as nx"


# Options for HTML output
# -----------------------
html_theme = "sphinxdoc"
#html_theme_options = {
#    "rightsidebar": "true",
#    "relbarbgcolor: "black"
#}


# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
html_style = 'networkx.css'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Content template for the index page.
html_index = 'index.html'

# Custom sidebar templates, maps page names to templates.
html_sidebars = {'index': 'indexsidebar.html'}

# Additional templates that should be rendered to pages, maps page names to
# templates.
html_additional_pages = {'index': 'index.html','gallery':'gallery.html'}

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = False

html_use_opensearch = 'http://networkx.lanl.gov'

# Output file base name for HTML help builder.
htmlhelp_basename = 'NetworkX'

pngmath_use_preview = True

# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [('tutorial/index', 'networkx_tutorial.tex', 
                    'NetworkX Tutorial',
                    'Aric Hagberg, Dan Schult, Pieter Swart', 'howto', 1),
                   ('reference/pdf_reference', 'networkx_reference.tex',
                    'NetworkX Reference',
                    'Aric Hagberg, Dan Schult, Pieter Swart', 'manual', 1)]

#latex_appendices = ['installing']#,'legal'],'citing','credits','history']

#latex_appendices = ['credits']

# Intersphinx mapping
intersphinx_mapping = {'http://docs.python.org/': None,
                       'http://docs.scipy.org/doc/numpy/': None,
                      }
                      
# For trac custom roles
trac_url = 'https://networkx.lanl.gov/trac/'

default_role = 'math' 

#mathjax_path = 'http://mathjax.connectmv.com/MathJax.js'

