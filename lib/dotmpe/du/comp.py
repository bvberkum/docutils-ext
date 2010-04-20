import docutils
from dotmpe.du.ext.reader import mpe
from dotmpe.du.ext.writer import xhtml


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
    'dotmpe-xhtml': xhtml,
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

    if builder_name not in builders:
        mod_name += '.'+builder_name
        module = \
                __import__(mod_name, fromlist=[builder_name], level=0)
        # BVB: dont think this is needed anymore                
        if module.__name__ != mod_name:
            raise ImportError, mod_name
        builders[builder_name] = module
    return getattr(builders[builder_name], klass)
                
