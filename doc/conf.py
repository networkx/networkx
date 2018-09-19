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
from __future__ import print_function

import sys
import os
from datetime import date

from sphinx_gallery.sorting import ExplicitOrder

# Check Sphinx version
import sphinx
if sphinx.__version__ < "1.3":
    raise RuntimeError("Sphinx 1.3 or newer required")

# Environment variable to know if the docs are being built on rtd.
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
#print
#print("Building on ReadTheDocs: {}".format(on_rtd))
#print
#print("Current working directory: {}".format(os.path.abspath(os.curdir)))
#print("Python: {}".format(sys.executable))

# If your extensions are in another directory, add it here.
# These locations are relative to conf.py

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx_gallery.gen_gallery',
    'nb2plots',
    'texext',
]

# https://github.com/sphinx-gallery/sphinx-gallery
sphinx_gallery_conf = {
    # path to your examples scripts
    'examples_dirs': '../examples',
    'subsection_order': ExplicitOrder(['../examples/basic',
                                       '../examples/drawing',
                                       '../examples/graph',
                                       '../examples/algorithms',
                                       '../examples/advanced',
                                       '../examples/3d_drawing',
                                       '../examples/pygraphviz',
                                       '../examples/javascript',
                                       '../examples/jit',
                                       '../examples/subclass']),
    # path where to save gallery generated examples
    'gallery_dirs': 'auto_examples',
    'backreferences_dir': 'modules/generated',
    'expected_failing_examples': ['../examples/advanced/plot_parallel_betweenness.py']
}

# generate autosummary pages
autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
#templates_path = ['']

suppress_warnings = ['ref.citation', 'ref.footnote']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'NetworkX'
copyright = '2004-{}, NetworkX Developers'.format(date.today().year)

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
import networkx
version = networkx.__version__
# The full version, including dev info
release = networkx.__version__.replace('_', '')

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
# unused_docs = ['']

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
modindex_common_prefix = ['networkx.']

doctest_global_setup = "import networkx as nx"

# treat ``x, y : type`` as vars x and y instead of default ``y(x,) : type``
napoleon_use_param = False

# Options for HTML output
# -----------------------

if not on_rtd:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# html_theme_options = {
#    "rightsidebar": "true",
#    "relbarbgcolor: "black"
#}

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
#html_style = ''

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Content template for the index page.
#html_index = 'index.html'

# Custom sidebar templates, maps page names to templates.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# templates.
#html_additional_pages = {'': ''}

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = False

html_use_opensearch = 'http://networkx.github.io'

# Output file base name for HTML help builder.
htmlhelp_basename = 'NetworkX'

# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [('reference/index', 'networkx_reference.tex',
                    'NetworkX Reference',
                    'Aric Hagberg, Dan Schult, Pieter Swart', 'manual', 1)]

latex_appendices = ['tutorial']

# Intersphinx mapping
intersphinx_mapping = {'https://docs.python.org/2/': None,
                       'https://docs.scipy.org/doc/numpy/': None,
                       }

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'obj'

numpydoc_show_class_members = False

# Add the 'copybutton' javascript, to hide/show the prompt in code
# examples
def setup(app):
    app.add_javascript('copybutton.js')
