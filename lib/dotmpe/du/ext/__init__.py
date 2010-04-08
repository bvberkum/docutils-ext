"""
Extensions for docutils reStructuredText.

Upon import registers:

- Margin directive with rSt parser.

TODO:
- 'dotmpe-htdocs' writer alias for XHTML output with margin support.
- 'rst' writer alias for reStructuredText output.
"""

__docformat__ = 'reStructuredText'

#from pub import Publisher

from docutils.parsers.rst import directives


"Register left_margin/right_margin directives"
from dotmpe.du.ext.node.margin import Margin
directives.register_directive('margin', Margin)


#"Override standard html writer, add margin support"
#docutils.writers._writer_aliases['html'] = 'dotmpe.du.ext.writer.xhtml'

# XXX: docutils.{reader,parser,writer}s.get_*_class
# cannot load modules from other packages
#docutils.writers._writer_aliases.update({
#    'dotmpe-htdocs': 'dotmpe.du.ext.writer.xhtml'})
#docutils.writers._writer_aliases.update({
#    'dotmpe-rst': 'dotmpe.du.ext.writer.rst',
#    'rst': 'dotmpe-rst' })
