import logging
import docutils
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.writer import xhtml


logger = logging.getLogger(__name__)

readers = {
    'dotmpe': mpe,
    'dotmpe-v5': mpe,
}

def get_reader_class(reader_name, klass='Reader'):
    if reader_name in readers:
        return getattr(readers[reader_name], klass)
    else:
        assert klass == 'Reader'
        return docutils.readers.get_reader_class(reader_name)

parsers = {
}

def get_parser_class(parser_name, klass='Parser'):
    if parser_name in parsers:
        return getattr(parsers[parser_name], klass)
    else:
        assert klass == 'Parser'
        return docutils.parsers.get_parser_class(parser_name)

writers = {
    'xhtml': xhtml,
    'dotmpe-html': xhtml,
}

def get_writer_class(writer_name, klass='Writer'):
    if writer_name in writers:
        return getattr(writers[writer_name], klass)
    else:
        assert klass == 'Writer'
        return docutils.writers.get_writer_class(writer_name)


builders = {
}

def get_builder_class(builder_name, 
        klass='Builder', 
        mod_name='dotmpe.du.builder', restrict=[]):

    global builders
    assert builder_name

    if builder_name not in builders:
        mod_name += '.'+builder_name
        import logging
        logging.info('get_builder_class %s %s', mod_name, klass)
        try:
            module = \
                    __import__(mod_name, fromlist=[builder_name], level=0)
        except ImportError, e:
            logger.error('Failed importing builder module %s from %s.  ', builder_name, mod_name)
            raise e
        # BVB: dont think this is needed anymore                
        if module.__name__ != mod_name:
            raise ImportError, mod_name
        logger.info(('get_builder_class',builders, builder_name, 
            mod_name,
            getattr(module, klass)))
        builders[builder_name] = module
    return getattr(builders[builder_name], klass)
                
