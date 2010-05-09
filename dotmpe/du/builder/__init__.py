"""
Builders are preconfigured sets of Reader, Parser, Extractor and Writer components.

The goal is to have a component interface for multiple input and output formats,
perhaps to experiment with content-negotiation later. But for now this serves as
a convenient wrapper.
"""
import logging
import types
import StringIO
import docutils.core
import nabu
import nabu.server
import dotmpe
from docutils import SettingsSpec
from dotmpe.du import comp


logger = logging.getLogger(__name__)

class Builder(SettingsSpec):

    """
    Each builder is a configuration of Docutils and Nabu components.

    It is a facade to build document tree's from source, and to render or process
    these. Behind it are the Du Publisher and Nabu's data extraction routines.
    """

    Reader = comp.get_reader_class('standalone')
    Parser = comp.get_parser_class('restructuredtext')
    """
    Both Du Reader and Parser Component classes are described here. 
    The writer is accessed directly by name for now.
    """

    settings_spec = (
    )
    """
    Additional frontend settings-spec used besides those on Reader, Parser and
    Writer by Du Publisher. Use e.g. for those defined by extractors.
    """

    settings_overrides = {
        # Within a server, we often would not want to read local files:
        'file_insertion_enabled': False,
        'embed_stylesheet': False,
        '_disable_config': True,
        # If your builder uses the html4css1 writer it needs this file:
        #'template': 'template.txt'
        'error_encoding': 'UTF-8',
        'halt_level': 100, # never halt
        'report_level': 1,
    }
    """
    All overrides, for Reader, Parser, Transforms and Writer settings are lumped
    together at the builder class. 
    """

    def get_overrides(self, **settings):
        """
        Get merged settings_overrides from builder class down to current.
        "FIXME: rewrite single level update to tree merge. "
        """
        for c in self.__base():
            settings.update(c.settings_overrides)
        return settings

    relative_path_settings = ()
    " XXX: Some pair of keynames used to lookup paths? "

    extractors = [] # list of (transform, storage) type pairs
    """
    Transforms that are run during `process`. They receive source_id, storage and
    pickle-receiver arguments at apply. These may modify the tree but usually
    extract data for storage. The stores may be left uninitialized until `prepare`.
    """

    def initialize(self, **settings_overrides):
        """
        Reloads overrides from class onto instance and prepare builder before use. 
        Resets builder (but not extractor) instance(s). 
        """
        logger.debug("Initializing %s. ", self)
        # get overrides
        self.overrides = self.get_overrides()
        self.overrides.update(settings_overrides)
        # build attributes:
        self.docpickled = None
        self.build_warnings = StringIO.StringIO()
        # for process attributes see self.prepare
        # writers attributes:
        self.writer_parts = {}

    def build(self, source, source_id='<build>'):
        """
        Build document from source, returns the document.
        """
        logging.debug("Building %s (%s).", source_id, self)
        # Errors from conversion to document tree.
        if 'warning_stream' not in self.overrides:
            self.overrides['warning_stream'] = self.build_warnings
        else:
            logging.info("TODO: open or keep filelike warning_stream %s",
                    self.overrides['warning_stream'])
        output, self.publisher = self.__publish(source, source_id, None,
                self.overrides)
        return self.publisher.document

    def prepare(self, **store_params):
        """
        Initialize or reset the extractors and storages. `store_params` provides
        arguments for constructing the storages by type. Note that storages per
        definition work on multiple documents. So only use this to reset in-memory
        stores or before calling `process` the first time.
        """
        logger.debug("Builder prepare.")
        self.process_messages = u''
        for idx, (xcls, xstore) in enumerate(self.extractors):
            # initialize extractor
            #xcls.init_parser(xcls)
            # reinitialize store
            if type(xstore) != type:
                if type(xstore) == types.InstanceType:
                    xstore = xstore.__class__
                assert isinstance(xstore, types.ClassType)                    
                args, kwds = store_params.get(xstore, ((),{}))
                try:
                    xstore = xstore(*args, **kwds)
                except TypeError, e:
                    logging.error(e)
                    raise TypeError, "Error instantiating storage %r "  % xstore
            # keep prepared extractor pairs:
            self.extractors[idx] = (xcls, xstore)

    def process(self, document, source_id='<process>', settings_overrides={}):
        """
        If there are extractors for this builder, apply them to the document. 

        Given source_id is used in the extractor stores to refer to the current
        document. `prepare` should have been run if stores need specific instance
        arguments. The extractor-types are instantiated later on, by Nabu using
        the document as argument.

        Afterward the document is returned, and `builder.docpickled` and
        `builder.process_messages` are available.
        """
        if not self.extractors:
            logging.info("No extractors to run. ")
            self.docpickled = None
            return document
        
        logging.debug("Processing %s (%s). ", source_id, self)
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

    def render(self, source, source_id='<render>', writer_name='xhtml',
            parts=['whole']):
        """
        XXX: Simple interface to writer component..
        """
        #writer_name = writer_name or self.default_writer
        writer = comp.get_writer_class(writer_name)()
        output, pub = self.__publish(source, source_id, writer,
                self.overrides)
        self.parts = pub.writer.parts
        return ''.join([self.parts.get(part) for part in parts])

    def render_fragment(self, source, source_id='<render_fragment>', settings_overrides={}):
        """
        XXX: HTML only, return body fragment (without body container).
        """
        return self.render(source, source_id, writer_name='xhtml',
                parts=['html_title', 'body'])

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

    def __base(self):
        """ Walk inheritance chain top down, updating settings with found
        overrides. """
        c = self.__class__#klass
        bases = [c]
        while c != Builder:
            c = c.__bases__[0]
            bases.append(c)
        while bases:
            yield bases.pop()

    # Builder Du core
    def __publish(self, source, source_path, writer, settings_overrides={}):
        if isinstance(source, docutils.nodes.document):
            source_class = docutils.io.DocTreeInput
            parser = comp.get_parser_class('null')()
            reader = comp.get_reader_class('doctree')()
        else:
            source_class = docutils.io.StringInput 
            parser = self.Parser()
            reader = self.Reader(parser)
        if not writer:
            writer = comp.get_writer_class('null')()
        destination_class = docutils.io.StringOutput
        overrides = self.settings_overrides
        overrides.update(settings_overrides)
        logger.info("Publishing %s (%s, %s, %s)", 
                source_path, reader, parser, writer)
        output, pub = docutils.core.publish_programmatically(
            source_class, source, source_path, 
            destination_class, None, None,
            reader, None,
            parser, None,
            writer, None,
            None, self,
            overrides, None, None)
        return output, pub

