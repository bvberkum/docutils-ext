"""
Builders are preconfigured sets of Reader, Parser, Extractor and Writer components.

The goal is to have a component interface for multiple input and output formats,
perhaps to experiment with content-negotiation later. But for now this serves as
a convenient wrapper.
"""
import logging
import StringIO
import docutils.core
import nabu
import nabu.server
import dotmpe
from dotmpe.du import comp


class Builder:
    """
    Each builder is a set configuration of Docutils and Nabu components.
    """

    Reader = comp.get_reader_class('standalone')
    Parser = comp.get_parser_class('restructuredtext')
    "Both Reader and Parser Component classes are described here. "
    "The writer is accessed directly by name for now. "

    settings_overrides = {
            # Within a server, we often would not want to read local files:
            'file_insertion_enabled': False,
            'embed_stylesheet': False,
            '_disable_config': True,
            # If your builder uses the html4css1 writer it needs this file:
            #'template': 'template.txt'
        }

    """
    All overrides, for Reader, Parser, Transforms and Writer settings are put here.
    They could have been the components class for clarity, but this serves too.
    """

    extractors = (
            #(transform, storage),
        )
    """
    Transforms that are run during process. They receive source_id, storage and
    pickle-receiver arguments at apply.
    """

    def initialize(self):
        """
        Prepare builder. This collect all settings overrides for this instance 
        its class inheritance chain. Each subclass can define overrides.
        """
        self.settings_overrides = get_overrides(self.__class__)
        self.docpickled = None
        self.build_warnings = u''
        self.process_messages = u''
        self.writer_parts = {}

    def build(self, source, source_id='<build>', settings_overrides={}):
        """
        Build document from source, returns the document.
        During build, reported messages are kept and afterward made available
        through `builder.build_warnings`. 
        """
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

    def process(self, document, source_id='<process>', settings_overrides={}):
        """
        If there are extractors for this builder, apply them to the document. 
        The source_id should be used by the extractor stores to refer to the
        current document.

        After processing the document is returned, and `builder.docpicked` or
        `builder.process_messages` are made available.
        """
        if not self.extractors:
            self.docpickled = None
            return document

        # Each transform that alters the tree should repickle it
        pickles = []
        pickle_receiver = nabu.server.SimpleAccumulator(pickles)

        # Run extractor transforms on the document tree.
        # XXX: Altered trees should be pickled again.
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
        """
        XXX: Simple interface to writer component..
        """
        #writer_name = writer_name or self.default_writer
        writer = comp.get_writer_class(writer_name)()
        output, pub = self.__publish(source, source_id, writer,
                settings_overrides)
        self.parts = pub.writer.parts
        return ''.join([self.parts.get(part) for part in parts])

    def render_fragment(self, source, source_id='<render_fragment>', settings_overrides={}):
        """
        XXX: HTML only, return body fragment (without body container).
        """
        return self.render(source, source_id, writer_name='html4css1',
                parts=['html_title', 'body'],
                settings_overrides=settings_overrides)

    # HTML-writer parts:                                                         #
    ['subtitle', 'version', 'encoding', 'html_prolog', 'header', 'meta',
     'html_title', 'title', 'stylesheet', 'html_subtitle',
     'html_body', 'body', 'head', 'body_suffix', 'fragment',
     'docinfo', 'html_head', 'head_prefix', 'body_prefix', 'footer',
     'body_pre_docinfo', 'whole']

#        # TODO: move this to XHTML writer
#        script = ''
#        for path in settings_overrides['javascript_paths']:
#            script += "<script type=\"application/javascript\" src=\"%s\"></script>" % path
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


