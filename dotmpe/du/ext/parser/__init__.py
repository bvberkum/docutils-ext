"""
There are some experimental parsers, but the parser module really serves to hold
rst extensions (nodes, directives etc.)
"""
from dotmpe.du import comp

from inliner import Inliner


# register all local modules with tag 'mpe' as Parser type
comp.register_extension_components(__name__, 'mpe', 'Parser', __file__)
