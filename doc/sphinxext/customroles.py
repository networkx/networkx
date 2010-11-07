"""
    Custom Roles
"""

from docutils import nodes, utils
from docutils.parsers.rst import roles

from sphinx import addnodes
from sphinx.util import ws_re, caption_ref_re

# http://www.doughellmann.com/articles/how-tos/sphinx-custom-roles/index.html
def sample_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Custom role.
   
    Parameters
    ----------
    name : str
        The name of the role, as used in the document.
    rawtext : str
        The markup, including the role declaration.
    text : str
        The text to be marked up by the role.
    lineno : int
        The line number where `rawtext` appears.
    inliner : Inliner
        The instance that called the role.
    options : dict
        Directive options for customizatoin.
    content : list
        The directive content for customization.
        
    Returns
    -------
    nodes : list
        The list of nodes to insert into the document.
    msgs : list
        The list of system messages, perhaps an error message.
        
    """
    pass
    
    
##################   
    
    
prefixed_roles = {
    # name: (prefix, baseuri)
    'arxiv': ('arXiv:', 'http://arxiv.org/abs/'),
    'doi': ('doi:', 'http://dx.doi.org/'),
}

no_text_roles = [
    'url',
    'pdf',
]

def prefixed_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    prefix, baseuri = prefixed_roles[name]
    uri = baseuri + text
    display = utils.unescape(text)
    node = nodes.literal(prefix, prefix)
    ref = nodes.reference(rawtext, display, refuri=uri, **options)
    node += ref # keep it in the 'literal' background
    return [node], []
    
def url_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    uri = text
    display = 'url'
    node = nodes.literal('', '')
    node += nodes.reference(rawtext, name, refuri=uri, **options)
    return [node], []
    
def trac_ticket_role(name, rawtext, text, lineno, inliner, 
                     options={}, content=[]):
    app = inliner.document.settings.env.app
    try:
        base = app.config.trac_url
        if not base:
            raise AttributeError
    except AttributeError, err:
        msg = 'trac_url configuration value is not set (%s)'
        raise ValueError(msg % str(err))

    slash = '/' if base[-1] != '/' else ''
    prefix = 'ticket '
    node = nodes.literal(prefix, prefix)
    display = utils.unescape(text)
    uri = base + slash + 'ticket/' + text
    node += nodes.reference(rawtext, display, refuri=uri, **options)
    return [node], []  

def trac_changeset_role(name, rawtext, text, lineno, inliner, 
                        options={}, content=[]):
    app = inliner.document.settings.env.app
    try:
        base = app.config.trac_url
        if not base:
            raise AttributeError
    except AttributeError, err:
        msg = 'trac_url configuration value is not set (%s)'
        raise ValueError(msg % str(err))    

    slash = '/' if base[-1] != '/' else ''
    unescaped = utils.unescape(text)
    prefix = 'changeset '
    node = nodes.literal(prefix, prefix)

    # Hard-coded for NetworkX
    if unescaped.endswith('networkx-svn-archive'):
        # Use the integer
        display = unescaped.split('/')[0]
    else:
        # hg: use the first 12 hash characters
        display = unescaped[:12]
        
    uri = base + slash + 'changeset/' + text
    node += nodes.reference(rawtext, display, refuri=uri, **options)
    return [node], []

active_roles = {
    'arxiv': prefixed_role,
    'doi': prefixed_role,
    'pdf': url_role,
    'url': url_role,
    'ticket': trac_ticket_role,
    'changeset': trac_changeset_role,
}

# Add a generic docstring.
for role in active_roles.values():
    role.__doc__ = sample_role.__doc__

def setup(app):
    for role, func in active_roles.iteritems():
        roles.register_local_role(role, func)
    app.add_config_value('trac_url', None, 'env')
        

