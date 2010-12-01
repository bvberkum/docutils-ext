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
from docutils.parsers.rst import directives

import dotmpe.du.ext.writer


"Register left_margin/right_margin directives. "
from dotmpe.du.ext.parser.rst.directive.margin import Margin
directives.register_directive('margin', Margin)

"Override include directive registration. "
from dotmpe.du.ext.parser.rst.directive.include import Include
directives.register_directive('include', Include)


#from pub import Publisher
"XXX: see blue-lines.appspot.com"


"""
Override docutils.{reader,parser,writer}s.get_*_class because these cannot load
from other modules.
See dotmpe.du.ext.{reader,parser,writer} for additional component aliases.
"""

_du_get_reader_class = docutils.readers.get_reader_class
def get_reader_class(reader_name):
    if reader_name in dotmpe.du.ext.reader._readers:
        return dotmpe.du.ext.reader.get_reader_class(reader_name)
    else:
        return _du_get_reader_class(reader_name)
docutils.readers.get_reader_class = get_reader_class

_du_get_parser_class = docutils.parsers.get_parser_class
def get_parser_class(parser_name):
    if parser_name in dotmpe.du.ext.parser._parsers:
        return dotmpe.du.ext.parser.get_parser_class(parser_name)
    else:
        return _du_get_parser_class(parser_name)
docutils.parsers.get_parser_class = get_parser_class

_du_get_writer_class = docutils.writers.get_writer_class
def get_writer_class(writer_name):
    if writer_name in dotmpe.du.ext.writer._writers:
        return dotmpe.du.ext.writer.get_writer_class(writer_name)
    else:
        return _du_get_writer_class(writer_name)
docutils.writers.get_writer_class = get_writer_class

