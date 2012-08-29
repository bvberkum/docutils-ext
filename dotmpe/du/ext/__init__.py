"""
Extensions for docutils reStructuredText.

Upon import, this module registers:

- Margin directive with rSt parser.
- If 'mwlib' is available the 'mediawiki' directive for rST.
- Updated include directive, for use with dotmpe.du.builder
- Register additional writers for use with dotmpe.du.builder

TODO:
- 'dotmpe-htdocs' writer alias for XHTML output with margin support.
- 'rst' writer alias for reStructuredText (lossless?) writer.
"""

__docformat__ = 'reStructuredText'

import sys

import docutils
import docutils.readers
import docutils.writers
import docutils.parsers
import docutils.parsers.rst


import dotmpe.du
from dotmpe.du import comp
import transform
#import extractor
import node
# import and register
import dotmpe.du.ext.parser
import dotmpe.du.ext.reader
import dotmpe.du.ext.writer
from dotmpe.du.ext.parser.rst.directive.margin import Margin
from dotmpe.du.ext.parser.rst.directive.images import Figure


### reStructuredText extensions

"Register left_margin/right_margin directives. "
docutils.parsers.rst.directives.register_directive('margin', Margin)

#"Override include directive registration. "
# FIXME: better use another directive name
#from dotmpe.du.ext.parser.rst.directive.include import Include
#directives.register_directive('include', Include)

"Override figure, enable 'label' for figure directive. "
# FIXME: ugly.. need to dream up new directive names..
del docutils.parsers.rst.directives._directive_registry['figure']
# FIXME: i18n
docutils.parsers.rst.directives.register_directive('figuur', Figure)
docutils.parsers.rst.directives.register_directive('figure', Figure)



### Atlassian Confluence support

try:
    import rst2confluence.confluence

    comp.writers['confluence'] = 'rst2confluence.confluence'

except ImportError, e:
    print >> sys.stderr, "No confluence writer (depends on rst2confluence)"


### Media Wiki support

try:
    # XXX: make an raw block of mediawiki?
    import mwlib

    from dotmpe.du.ext.parser.rst.directive.mediawiki import MediaWiki
    docutils.parsers.rst.directives.register_directive('mediawiki', MediaWiki)
except ImportError, e:
    print >> sys.stderr, "No mediawiki directive (depends on mwlib)"
    pass



#from pub import Publisher
"XXX: see blue-lines.appspot.com"


"""
Override ``docutils.{reader,parser,writer}s.get_*_class`` because these cannot load
from other modules.

See ``dotmpe.du.ext.{reader,parser,writer}`` for the extension components and how
they're loaded (``dotmpe.du.comp``).
"""

_du_get_reader_class = docutils.readers.get_reader_class
def get_reader_class(reader_name):
    if reader_name in dotmpe.du.comp.readers:
        return dotmpe.du.comp.get_reader_class(reader_name)
    else:
        try:
            return _du_get_reader_class(reader_name)
        except AttributeError, e:
            raise Exception("Cannot find reader %s" % reader_name)
docutils.readers.get_reader_class = get_reader_class

_du_get_parser_class = docutils.parsers.get_parser_class
def get_parser_class(parser_name):
    if parser_name in dotmpe.du.comp.parsers:
        return dotmpe.du.comp.get_parser_class(parser_name)
    else:
        try:
            return _du_get_parser_class(parser_name)
        except AttributeError, e:
            raise Exception("Cannot find parser %s" % parser_name)
docutils.parsers.get_parser_class = get_parser_class

_du_get_writer_class = docutils.writers.get_writer_class
def get_writer_class(writer_name):
    if writer_name in dotmpe.du.comp.writers:
        return dotmpe.du.comp.get_writer_class(writer_name)
    else:
        try:
            return _du_get_writer_class(writer_name)
        except AttributeError, e:
            raise Exception("Cannot find writer %s" % writer_name)
docutils.writers.get_writer_class = get_writer_class

