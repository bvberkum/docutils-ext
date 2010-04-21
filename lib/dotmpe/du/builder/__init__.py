"""
Builders are preconfigured sets of Reader, Parser and Writer components.
"""
import logging
import StringIO
import docutils.core
import nabu
import dotmpe
from dotmpe.du import comp


class Builder:
    """
    Each builder is a set configuration of Docutils and Nabu components.
    """

    Reader = comp.get_reader_class('standalone')
    Parser = comp.get_parser_class('restructuredtext')
    "Both Reader and Parser Component classes are described here. "
    "The writer is accessed difrectly by name for now. "

    settings_overrides = {
        # within a server, do not read local files:
        'file_insertion_enabled': False,
        'embed_stylesheet': False,
        '_disable_config': True,
        # if your builder uses the html4css1 writer it needs this file:
        #'template': 'template.txt'
        'strip_comments': 1,
        'stylesheet_path':'/media/style/default.css',
#            'template': os.path.join(conf.ROOT, 'du-template.txt'),
        'strip_substitution_definitions': True,
        'strip_anonymous_targets': True,
        'spec_names': ['cc-license','generator','timestamp','source-link'],
        'strip_spec_names': ['cc-license','generator','timestamp','source-link'],
    }
    """
    All overrides, for Reader, Parser, Transforms and Writer settings are put here.
    Perhaps they should be at the components class.
    """

    extractors = (
            #(transform, storage),
            )
    """
    Transforms that are run during process, and receive unid, storage and pickle
    receiver at apply.     
    """

    def initialize(self):
        self.docpickled = None
        self.build_warnings = u''
        self.process_messages = u''
        self.writer_parts = {}
        # collect overrides for instance from inheritance chain:
        self.settings_overrides = get_overrides(self.__class__)

    def build(self, source, source_id='<build>', settings_overrides={}):
        "Build document from source. "
        warnings = StringIO.StringIO()
        overrides = self.settings_overrides
        overrides.update( {
            'error_encoding': 'UTF-8',
            'halt_level': 100, # never halt
            'report_level': 1,
            'warning_stream': warnings, })
        overrides.update(settings_overrides)
        output, self.publisher = self.__publish(source, source_id, None, overrides)
        # Errors from conversion to document tree.
        self.build_warnings = warnings.getvalue().decode('UTF-8')
        return self.publisher.document

    def process(self, document, source_id, settings_overrides={}):
        if not self.extractors:
            self.docpickled = None
            return document

        # Each transform that alters the tree should repickle it
        pickles = []
        pickle_receiver = nabu.server.SimpleAccumulator(pickles)

        # Transform the document tree.
        # Note: we apply the transforms before storing the document tree.
        report_level = settings_overrides.get('report_level', 1)
        self.process_messages = nabu.process.transform_doctree(
            source_id, document, 
            self.extractors, pickle_receiver, report_level)

        if pickles:
            self.docpickled = pickles[-1]
        else:
            self.docpickled = None
    
        return document

    def render(self, source, source_id='<render>', writer_name='html4css1',
            parts=['whole'], settings_overrides={}):
        writer_name = writer_name or self.default_writer
        writer = comp.get_writer_class(writer_name)()
        output, pub = self.__publish(source, source_id, writer,
                settings_overrides)
        self.parts = pub.writer.parts
        return ''.join([self.parts.get(part) for part in parts])

    def render_fragment(self, source, source_id='<render_fragment>', settings_overrides={}):
        return self.render(source, source_id, writer_name='html4css1',
                parts=['html_title', 'body'],
                settings_overrides=settings_overrides)

    # HTML-writer parts:                                                         #
    ['subtitle', 'version', 'encoding', 'html_prolog', 'header', 'meta',
     'html_title', 'title', 'stylesheet', 'html_subtitle',
     'html_body', 'body', 'head', 'body_suffix', 'fragment',
     'docinfo', 'html_head', 'head_prefix', 'body_prefix', 'footer',
     'body_pre_docinfo', 'whole']

#        script = ''
#        for path in settings_overrides['javascript_paths']:
#            script += "<script type=\"application/javascript\" src=\"%s\"></script>" % path
#        # TODO: move this to XHTML writer if possible
#        parts['head'] += script
#        #import pprint
#        #print pprint.pformat(parts.keys())
#        for p in ['whole',]:
#            parts[p] = parts[p].replace('</head>', script+'\n</head>')

    def __publish(self, source, source_path, writer, settings_overrides={}):
        if isinstance(source, docutils.nodes.document):
            source_class = docutils.io.DocTreeInput
            parser = comp.get_parser_class('null')()
            reader = comp.get_reader_class('doctree')()
        else:
            source_class = docutils.io.StringInput 
            reader = self.Reader()
            parser = self.Parser()
        if not writer:
            writer = comp.get_writer_class('null')()
        destination_class = docutils.io.StringOutput
        overrides = self.settings_overrides
        overrides.update(settings_overrides)
        output, pub = docutils.core.publish_programmatically(
            source_class, source, source_path, 
            destination_class, None, None,
            reader, None,
            parser, None,
            writer, None,
            None, None,
            overrides, None, None)
        return output, pub


def get_overrides(klass, **settings):
    "Walk inheritance chain top down, updating settings with found overrides. "
    "FIXME: rewrite single level update to tree merge. "
    c = klass
    bases = [c]
    while c != Builder:
        c = c.__bases__[0]
        bases.append(c)
    while bases:
        c = bases.pop()
        settings.update(c.settings_overrides)
    return settings


