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

try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
# don't prevent use of paste if pkg_resources isn't installed
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

try:
    import modulefinder
except ImportError:
    pass
else:
    for p in __path__:
        modulefinder.AddPackagePath(__name__, p)
    del p



import docutils
import docutils.readers
import docutils.writers
import docutils.parsers
import docutils.parsers.rst


import dotmpe.du
from dotmpe.du.util import get_log
import transform
#import extractor
import node
# import and register
import dotmpe.du.ext.parser
import dotmpe.du.ext.reader
import dotmpe.du.ext.writer
from dotmpe.du.ext.parser.rst.directive.margin import Margin
from dotmpe.du.ext.parser.rst.directive.images import Figure


logger = get_log(__name__)

""

"Register left_margin/right_margin directives. "
docutils.parsers.rst.directives.register_directive('margin', Margin)

#"Override include directive registration. "
# FIXME: better use another directive name
#from dotmpe.du.ext.parser.rst.directive.include import Include
#directives.register_directive('include', Include)

"Override figure, enable 'label' for figure directive. "
# FIXME: ugly.. need to dream up new directive names..
if 'figure' in docutils.parsers.rst.directives._directive_registry:
    del docutils.parsers.rst.directives._directive_registry['figure']
# FIXME: i18n
docutils.parsers.rst.directives.register_directive('figuur', Figure)
docutils.parsers.rst.directives.register_directive('figure', Figure)


try:
    import mwlib

    from dotmpe.du.ext.parser.rst.directive.mediawiki import MediaWiki
    docutils.parsers.rst.directives.register_directive('mediawiki', MediaWiki)
except ImportError, e:
    pass


# XXX: Cruft
#from pub import Publisher
"XXX: see blue-lines.appspot.com"

"""
Override ``docutils.{reader,parser,writer}s.get_*_class`` because these cannot load
from other modules.

See ``dotmpe.du.ext.{reader,parser,writer}`` for the extension components and how
they're loaded (``dotmpe.du.comp``).
"""

"""
if not hasattr(docutils, 'ext'):

    _du_get_reader_class = docutils.readers.get_reader_class
    def get_reader_class(reader_name):
        if reader_name in dotmpe.du.comp.readers:
            reader = dotmpe.du.comp.get_reader_class(reader_name)
        else:
            try:
                reader = _du_get_reader_class(reader_name)
            except ( RuntimeError, ImportError ), e:
                logger.warn("No Du Reader for name '%s'" % reader_name)
                #print 'Failed getting reader %r' % reader_name
                #print 'Components:', dir(dotmpe.du.comp)
                #print 'Readers:', dotmpe.du.comp.readers
                raise e
        assert issubclass(reader, docutils.readers.Reader), reader
        return reader
    docutils.readers.get_reader_class = get_reader_class

    _du_get_parser_class = docutils.parsers.get_parser_class
    def get_parser_class(parser_name):
        if parser_name in dotmpe.du.comp.parsers:
            parser = dotmpe.du.comp.get_parser_class(parser_name)
        else:
            parser = _du_get_parser_class(parser_name)
        assert issubclass(parser, docutils.parsers.Parser), parser
        return parser
    docutils.parsers.get_parser_class = get_parser_class

    _du_get_writer_class = docutils.writers.get_writer_class
    def get_writer_class(writer_name):
        if writer_name in dotmpe.du.comp.writers:
            writer = dotmpe.du.comp.get_writer_class(writer_name)
        else:
            writer = _du_get_writer_class(writer_name)
        assert issubclass(writer, docutils.writers.Writer), writer
        return writer
    docutils.writers.get_writer_class = get_writer_class

    setattr(docutils, 'ext', 'mpe')

"""
