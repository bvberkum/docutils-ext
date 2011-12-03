"""
Extensions for docutils reStructuredText.

Upon import registers:

- Margin directive with rSt parser.
- Updated inlcude directive for use with dotmpe.du.builder
- Register additional writers

TODO:
- 'dotmpe-htdocs' writer alias for XHTML output with margin support.
- 'rst' writer alias for reStructuredText (lossless?) writer.
"""

__docformat__ = 'reStructuredText'


import docutils
import docutils.readers
import docutils.writers
import docutils.parsers
import docutils.parsers.rst

# import and register
import dotmpe.du.ext.writer


"Register left_margin/right_margin directives. "
from dotmpe.du.ext.parser.rst.directive.margin import Margin
docutils.parsers.rst.directives.register_directive('margin', Margin)

#"Override include directive registration. "
# FIXME: better use another directive name
#from dotmpe.du.ext.parser.rst.directive.include import Include
#directives.register_directive('include', Include)

"Override figure, enable 'label' for figure directive. "
from dotmpe.du.ext.parser.rst.directive.images import Figure
# FIXME: ugly.. need to dream up new directive names..
del docutils.parsers.rst.directives._directive_registry['figure']
docutils.parsers.rst.directives.register_directive('figuur', Figure)
docutils.parsers.rst.directives.register_directive('figure', Figure)


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
        return _du_get_reader_class(reader_name)
docutils.readers.get_reader_class = get_reader_class

_du_get_parser_class = docutils.parsers.get_parser_class
def get_parser_class(parser_name):
    if parser_name in dotmpe.du.comp.parsers:
        return dotmpe.du.comp.get_parser_class(parser_name)
    else:
        return _du_get_parser_class(parser_name)
docutils.parsers.get_parser_class = get_parser_class

_du_get_writer_class = docutils.writers.get_writer_class
def get_writer_class(writer_name):
    if writer_name in dotmpe.du.comp.writers:
        return dotmpe.du.comp.get_writer_class(writer_name)
    else:
        return _du_get_writer_class(writer_name)
docutils.writers.get_writer_class = get_writer_class

