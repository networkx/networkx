import os
from datetime import date
from sphinx_gallery.sorting import ExplicitOrder, FileNameSortKey
from intersphinx_registry import get_intersphinx_mapping
from warnings import filterwarnings

filterwarnings(
    "ignore", message="Matplotlib is currently using agg", category=UserWarning
)

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
    "texext",
    "numpydoc",
    "matplotlib.sphinxext.plot_directive",
    "myst_nb",
]

# https://github.com/sphinx-gallery/sphinx-gallery
sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": "../examples",
    "subsection_order": ExplicitOrder(
        [
            "../examples/basic",
            "../examples/drawing",
            "../examples/3d_drawing",
            "../examples/graphviz_layout",
            "../examples/graphviz_drawing",
            "../examples/graph",
            "../examples/algorithms",
            "../examples/advanced",
            "../examples/external",
            "../examples/geospatial",
            "../examples/subclass",
        ]
    ),
    "within_subsection_order": "FileNameSortKey",
    # path where to save gallery generated examples
    "gallery_dirs": "auto_examples",
    "backreferences_dir": "modules/generated",
    "image_scrapers": ("matplotlib",),
    "matplotlib_animations": True,
    "plot_gallery": "True",
    "reference_url": {"sphinx_gallery": None},
}
# Add pygraphviz png scraper, if available
try:
    from pygraphviz.scraper import PNGScraper

    sphinx_gallery_conf["image_scrapers"] += (PNGScraper(),)
except ImportError:
    pass

# generate autosummary pages
autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Ignore spurious warnings related to bad interactions between the texmath
# and myst extensions
suppress_warnings = ["ref.citation", "ref.footnote"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
source_encoding = "utf-8"

# Items to exclude during source collection, including release announcement
# template, build outputs, and READMEs (markdown only)
exclude_patterns = ["release/release_template.rst", "build/*", "README.md"]

# General substitutions.
project = "NetworkX"
copyright = f"2004-{date.today().year}, NetworkX Developers"

# Used in networkx.utils.backends for cleaner rendering of functions.
# We need to set this before we import networkx.
os.environ["_NETWORKX_BUILDING_DOCS_"] = "True"
import networkx as nx

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = nx.__version__
# The full version, including dev info
release = nx.__version__.replace("_", "")

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
# unused_docs = ['']

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = 'friendly'
pygments_style = "sphinx"

# A list of prefixes that are ignored when creating the module index. (new in Sphinx 0.6)
modindex_common_prefix = ["networkx."]

# Options for HTML output
# -----------------------

html_baseurl = "https://networkx.org/documentation/stable/"
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "collapse_navigation": True,
    "navigation_depth": 2,
    "show_prev_next": False,
    "icon_links": [
        {"name": "Home Page", "url": "https://networkx.org", "icon": "fas fa-home"},
        {
            "name": "GitHub",
            "url": "https://github.com/networkx/networkx",
            "icon": "fab fa-github-square",
        },
    ],
    "external_links": [{"name": "Guides", "url": "https://networkx.org/nx-guides/"}],
    "navbar_end": ["theme-switcher", "navbar-icon-links", "version-switcher"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "header_links_before_dropdown": 8,
    "switcher": {
        "json_url": (
            "https://networkx.org/documentation/latest/_static/version_switcher.json"
        ),
        "version_match": "latest" if "dev" in version else version,
    },
    "show_version_warning_banner": True,
    "analytics": {
        "plausible_analytics_domain": "networkx.org",
        "plausible_analytics_url": ("https://views.scientific-python.org/js/script.js"),
    },
}
html_sidebars = {
    "**": ["sidebar-nav-bs", "sidebar-ethical-ads"],
    "index": [],
    "install": [],
    "tutorial": [],
    "backends": [],
    "auto_examples/index": [],
}
html_logo = "_static/networkx_banner.svg"
html_favicon = "_static/favicon.ico"

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
# html_style = ''

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Content template for the index page.
# html_index = 'index.html'

# Custom sidebar templates, maps page names to templates.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# templates.
# html_additional_pages = {'': ''}

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = False

html_use_opensearch = "https://networkx.org"

# Output file base name for HTML help builder.
htmlhelp_basename = "NetworkX"

# Options for LaTeX output
# ------------------------

# Use a latex engine that allows for unicode characters in docstrings
latex_engine = "xelatex"
# The paper size ('letter' or 'a4').
latex_paper_size = "letter"

# The font size ('10pt', '11pt' or '12pt').
# latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
    (
        "reference/index",
        "networkx_reference.tex",
        "NetworkX Reference",
        "Aric Hagberg, Dan Schult, Pieter Swart",
        "manual",
        1,
    )
]

latex_appendices = ["tutorial"]

# Intersphinx mapping

intersphinx_mapping = get_intersphinx_mapping(
    packages={
        "python",
        "numpy",
        "neps",
        "matplotlib",
        "scipy",
        "pandas",
        "geopandas",
        "pygraphviz",
        "sphinx-gallery",
        "sympy",
        "nx-guides",
    }
)
# NOTE: generally not relevant, but prevents very long build times when other
# projects' docs sites are not responding
intersphinx_timeout = 0.5

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = "obj"

numpydoc_show_class_members = False

plot_pre_code = """
import networkx as nx
import numpy as np
np.random.seed(42)
"""

plot_formats = [("png", 100)]


def setup(app):
    app.add_css_file("custom.css")
    app.add_js_file("copybutton.js")
    # Workaround to prevent duplicate file warnings from sphinx w/ myst-nb.
    # See executablebooks/MyST-NB#363
    app.registry.source_suffix.pop(".ipynb")


# Monkeypatch numpydoc to show "Backends" section
from numpydoc.docscrape import NumpyDocString

orig_setitem = NumpyDocString.__setitem__


def new_setitem(self, key, val):
    if key != "Backends":
        orig_setitem(self, key, val)
        return
    # Update how we show backend information in the online docs.
    # Start by creating an "admonition" section to make it stand out.
    newval = [".. admonition:: Additional backends implement this function", ""]
    for line in val:
        if line and not line.startswith(" "):
            # This line must identify a backend; let's try to add a link
            backend, *rest = line.split(" ")
            url = nx.utils.backends.backend_info.get(backend, {}).get("url")
            if url:
                line = f"`{backend} <{url}>`_ " + " ".join(rest)
        newval.append(f"   {line}")
    self._parsed_data[key] = newval


NumpyDocString.__setitem__ = new_setitem

from numpydoc.docscrape_sphinx import SphinxDocString

orig_str = SphinxDocString.__str__


def new_str(self, indent=0, func_role="obj"):
    rv = orig_str(self, indent=indent, func_role=func_role)
    if "Backends" in self:
        lines = self._str_section("Backends")
        # Remove "Backends" as a section and add a divider instead
        lines[0] = "----"
        lines = self._str_indent(lines, indent)
        rv += "\n".join(lines)
    return rv


SphinxDocString.__str__ = new_str
