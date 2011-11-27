"""
Registry of component names, for lazy loading, caching.
"""
import logging
import docutils
#from dotmpe.du.ext.reader import mpe
#from dotmpe.du.ext.writer import xhtml, html, htmlform


logger = logging.getLogger(__name__)

readers = {
    'dotmpe': 'dotmpe.du.ext.reader.mpe',
    #    'dotmpe-v5': mpe,
}
_readers = {}

def get_reader_class(reader_name, klass='Reader'):
    if reader_name not in _readers:
        reader_mod = reader_name
        if reader_mod in readers:
            reader_mod = readers[reader_mod]
            _readers[reader_name] = load_module(reader_mod)
        else:
            assert klass == 'Reader'
            return docutils.readers.get_reader_class(reader_name)
    return getattr(_readers[reader_name], klass)


parsers = {
}
_parsers = {}

def get_parser_class(parser_name, klass='Parser'):
    if parser_name not in _parsers:
        parser_mod = parser_name
        if parser_mod in parsers:
            parser_mod = parsers[parser_mod]
            _parsers[parser_name] = load_module(parser_mod)
        else:
            assert klass == 'Parser'
            return docutils.parsers.get_parser_class(parser_name)
    return getattr(_parsers[parser_name], klass)


writers = {
    'xhtml': 'dotmpe.du.ext.writer.xhtml',
    'dotmpe-html': 'dotmpe.du.ext.writer.html',
    'htmlform': 'dotmpe.du.ext.writer.htmlform',
}
_writers = {}

def get_writer_class(writer_name, klass='Writer'):
    if writer_name not in _writers:
        writer_mod = writer_name
        if writer_mod in writers:
            writer_mod = writers[writer_mod]
            _writers[writer_name] = load_module(writer_mod)
        else:
            assert klass == 'Writer'
            return docutils.writers.get_writer_class(writer_name)
    return getattr(_writers[writer_name], klass)

                

ERR_MISSING_BUILDER_MODNAME = "Missing builder module name. "

builders = { }

def get_builder_class(mod_name, class_name='Builder'):
    global builders
    assert mod_name, ERR_MISSING_BUILDER_MODNAME
    #if not class_name or (restrict and class_name not in restrict):
    #    class_name = 'Builder'
    if mod_name not in builders:
        logger.debug("Loading builder package %s ", mod_name)
        module = load_module(mod_name)
        builders[mod_name] = module
    else:
        module = builders[mod_name]
    return getattr(module, class_name)


ERR_MISSING_EXTRACTOR_MODNAME = "Missing extractor module name. "

extractors = { }

def get_extractor_class(mod_name, class_name='Extractor'):
    global extractors
    assert mod_name, ERR_MISSING_EXTRACTOR_MODNAME
    #if not class_name or (restrict and class_name not in restrict):
    #    class_name = 'Extractor'
    if mod_name not in extractors:
        logger.debug("Loading extractor package %s ", mod_name)
        module = load_module(mod_name)
        extractors[mod_name] = module
    else:
        module = extractors[mod_name]
    return getattr(module, class_name)


ERR_MISSING_EXTRACTOR_STORAGE_MODNAME = "Missing extractor_storage module name. "

extractor_storages = { }

def get_extractor_storage_class(mod_name, class_name='Storage'):
    global extractor_storages
    assert mod_name, ERR_MISSING_EXTRACTOR_STORAGE_MODNAME
    #if not class_name or (restrict and class_name not in restrict):
    #    class_name = 'Storage'
    if mod_name not in extractor_storages:
        logger.debug("Loading extractor_storage package %s ", mod_name)
        module = load_module(mod_name)
        extractor_storages[mod_name] = module
    else:
        module = extractor_storages[mod_name]
    return getattr(module, class_name)


def get_extractor_pair(mod_name):
    return get_extractor_class(mod_name), get_extractor_storage_class(mod_name)


## Util

def load_module(mod_name):
    p = mod_name.rfind('.')+1
    builder_name = mod_name[p:]
    try:
        module = __import__(mod_name, fromlist=[builder_name], level=0)
        return module    
    except ImportError, e:
        logger.critical('Failed importing builder module %s from %s.  ',
                builder_name, mod_name)
        raise e



