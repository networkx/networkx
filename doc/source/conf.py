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

# If your extensions are in another directory, add it here.
#sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath('../sphinxext'))
sys.path.append(os.path.abspath('../sphinxext/numpyext'))

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.addons.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.pngmath', 'numpydoc',
              'phantom_import', 'autosummary',
              'sphinx.ext.coverage',
              'only_directives',
#              'plot_directive',
              ]
#extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest','numpydoc']
#extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest']
#extensions = [#'mathmpl',
#              'ipython_console_highlighting', 'sphinx.ext.autodoc',
#              'inheritance_diagram', 'only_directives', 'plot_directive',
#              'sphinx.ext.pngmath',
#              ]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.                                      
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'contents'

# General substitutions.
project = 'NetworkX'
copyright = '2008, Aric Hagberg'

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
import networkx
version = networkx.__version__
# The full version, including alpha/beta/rc tags.
release = version

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'friendly'


# Options for HTML output
# -----------------------

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
html_style = 'sphinxdoc.css'

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
latex_documents = [('contents', 'networkx.tex', 'NetworkX Documentation',
                    'Aric Hagberg, Dan Schult, Pieter Swart', 'manual', 1)]

#latex_logo = 'static/networkx.png'

#latex_use_parts = True

# Additional stuff for the LaTeX preamble.
latex_elements = {
    'fontpkg': '\\usepackage{palatino}'
}

# Documents to append as an appendix to all manuals.
#latex_appendices = []


# Extension interface
# -------------------

from sphinx import addnodes

dir_sig_re = re.compile(r'\.\. ([^:]+)::(.*)$')

def parse_directive(env, sig, signode):
    if not sig.startswith('.'):
        dec_sig = '.. %s::' % sig
        signode += addnodes.desc_name(dec_sig, dec_sig)
        return sig
    m = dir_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    dec_name = '.. %s::' % name
    signode += addnodes.desc_name(dec_name, dec_name)
    signode += addnodes.desc_addname(args, args)
    return name


def parse_role(env, sig, signode):
    signode += addnodes.desc_name(':%s:' % sig, ':%s:' % sig)
    return sig


event_sig_re = re.compile(r'([a-zA-Z-]+)\s*\((.*)\)')

def parse_event(env, sig, signode):
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(','):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name


def setup(app):
    from sphinx.ext.autodoc import cut_lines
    app.connect('autodoc-process-docstring', cut_lines(4, what=['module']))
    app.add_description_unit('directive', 'dir', 'pair: %s; directive', parse_directive)
    app.add_description_unit('role', 'role', 'pair: %s; role', parse_role)
    app.add_description_unit('confval', 'confval', 'pair: %s; configuration value')
    app.add_description_unit('event', 'event', 'pair: %s; event', parse_event)
