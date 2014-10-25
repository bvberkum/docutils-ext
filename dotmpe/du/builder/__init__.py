# $Id$
"""
Builders are preconfigured sets of Reader, Parser, Extractor and Writer components.

The goal is to have a component interface for multiple input and output formats,
perhaps to experiment with content-negotiation later. Until then this serves as
as a thin wrapper to the Du publisher framework.
"""
import os
import logging
import types
import StringIO
import docutils.core
from docutils.core import Publisher
from docutils import SettingsSpec, frontend, utils, transforms

#import nabu
#import nabu.server
#import htdocs
#import dotmpe
from dotmpe.du import comp, util


logger = util.get_log(__name__)#, stdout=True, fout=False)

class Builder(SettingsSpec, Publisher):

    """
    Each builder is a configuration of Docutils and Nabu components.

    It is sort of a (to-be) facade to build document trees from source, and to render or process
    these. Behind it are Du Publisher and Nabu data extraction routines.
    """

    Reader = comp.get_reader_class('standalone')
    ReReader = comp.get_reader_class('doctree')
    Parser = comp.get_parser_class('restructuredtext')
    """
    Both Du Reader and Parser Component classes are set/described here and can
    be overridden in builder subclasses. 

    The writer is accessed directly by name for now.
    """
    default_writer = 'html-mpe'

    settings_spec = (
    )
    """
    Additional frontend settings-spec used *besides* those on Reader, Parser and
    Writer by Du Publisher. E.g. those used by extractors.
    """

    settings_defaults = {
    }

    settings_default_overrides = {
        # Within a server, we often would not want to read local files:
        '_disable_config': True,
        'file_insertion_enabled': False,
        #'embed_stylesheet': False,
        #'embed_script': False,
        #'template': os.path.join(DOC_ROOT, 'var', 'du-template.txt'),
    }

    relative_path_settings = ()
    " XXX: Some pair of keynames used to lookup paths? "

    def __init__(self):
        """
        Defer to Publisher init. 
        """
        Publisher.__init__(self)

        self.extractors = [] # list of (transform, storage) type pairs
        """
        Transforms that are run during `process`. See Nabu for their interface.
        The stores may be left uninitialized until `prepare_extractors`.
        """
        self.source_class = None

    def prepare_initial_components(self):
        #self.set_components(reader_name, parser_name, writer_name)
        self.parser = self.Parser()
        self.reader = self.Reader(parser=self.parser) 
        # FIXME: having initial writer component enables publisher src2trgt frontends 
        self.components = (self.parser, self.reader, self)

        # XXX: for now, all transforms are linked to the reader and the reader
        # gets its transforms from there. The extractors will similary depend on
        # the Reader transforms and settings_specs

    def setup_option_parser(self, usage=None, description=None,
                            settings_spec=None, config_section=None,
                            **defaults):
        if config_section:
            if not settings_spec:
                settings_spec = SettingsSpec()
            settings_spec.config_section = config_section
            parts = config_section.split()
            if len(parts) > 1 and parts[-1] == 'application':
                settings_spec.config_section_dependencies = ['applications']
        #@@@ Add self.source & self.destination to components in future?
        option_parser = frontend.OptionParser(
            components=self.components,
            defaults=defaults, read_config_files=1,
            usage=usage, description=description)
        return option_parser

    def update_components(self):
        """
        Reset components based on current settings.
        """
        pass

    def prepare(self, argv=None):
        self.prepare_extractors(**self.store_params)

    def build(self, source, source_id='<build>', overrides={}, cli=False):
        """
        Build document from source, returns the document.
        TODO: Use Reader, Parser, Transform and Builder for option spec.
        """
        logger.debug("Building %r.", source_id)
        self.source = source
        source_class, parser, reader, settings = self.prepare_source(source, source_id)
        if not self.writer:
            self.writer = comp.get_writer_class('null')()
        self.components = (self.parser, self.reader, self.writer, self)
        # FIXME: get defaults for components
        if not self.settings:\
            self.settings = frontend.Values({})
        if cli:
            self.process_command_line() # replace settings for initial components
        else:
        	self.build_doc()
        assert self.settings or isinstance(self.settings, frontend.Values), self.settings
        self.destination_class = docutils.io.StringOutput
        assert self.reader and self.parser and self.writer
        assert self.source
        self.settings.input_encoding = 'utf-8'
        self.settings.halt_level = 0
        self.settings.report_level = 6
        # XXX
        from dotmpe.du.frontend import get_option_parser
        option_parser = get_option_parser(
                self.components, usage='Builder testing: build [options] ..', 
                settings_spec=None, read_config_files = 0)
        self.settings = option_parser.get_default_values()
        source = self.source_class(
            source=self.source, source_path=self.source_id)
        # FIXME:  encoding=self.settings.input_encoding)
        self.document = self.reader.read(source, self.parser, self.settings)
        return self.document

    def build_doc(self):
        pass

    def init_extractors(self):
        """
        Load extractor and storage classes from modules.
        """
        import dotmpe.du.ext.extractor
        for spec in self.extractor_spec:
            if len(spec) > 1:
                extr_mod, store_mod = spec
            else:
                extr_mod = store_mod = spec[0]
            extr_clsss = comp.get_extractor_class(extr_mod)
            store_clss = comp.get_extractor_storage_class(store_mod)
            self.extractors.append((extr_clsss, store_clss))

    def prepare_extractors(self, **store_params):
        """
        Initialize or reset the extractors and storages. `store_params` provides
        arguments for constructing the storages by type. Note that storages per
        definition work on multiple documents. Only use this to reset in-memory
        stores or before calling `process` the first time.
        """
        if not self.extractors and self.extractor_spec:
            self.init_extractors()
        logger.debug("Builder prepare_extractors %s." % store_params)
        self.process_messages = u''
        for idx, (xcls, xstore) in enumerate(self.extractors):
            # initialize extractor
            #xcls.init_parser(xcls)
            # reinitialize store
            if type(xstore) != type:
                if type(xstore) == types.InstanceType:
                    xstore = xstore.__module__+'.'+xstore.__class__
#                assert isinstance(xstore, types.ClassType)                    
                args, kwds = store_params.get(unicode(xstore), ((),{}))
# XXX: would want to have merged options here, instead of # settings_default_overrides ref!
                try:
                    args, kwds = parse_params(args, kwds,
                            self.settings_default_overrides)
                except ValueError, e:
                    logger.error(e)
                    raise ValueError, "Error parsing storage params %r, %r" % (args, kwds)
                try:
                    xstore = xstore(*args, **kwds)
                except TypeError, e:
                    logger.error(e)
                    raise TypeError,  \
                            "Error instantiating storage %r with params %r %r"  % (
                                    xstore, args, kwds)
            self.extractors[idx] = (xcls, xstore)

    def process(self, document, source_id='<process>', overrides={},
            pickle_receiver=None):
        """
        If there are extractors for this builder, apply them to the document. 
        TODO: Return messages.

        `prepare_extractors` should have been run to initialize storages. 
        """
        if not self.extractors:
            logger.info("Process: no extractors to run. ")
            return u''
        logger.debug("Processing %r. ", source_id)
        document.transformer = transforms.Transformer(document)
        # before extract, remove existing msg.level < reporter.report_level from tree
        #document.transformer.add_transform(universal.FilterMessages, priority=1)
        # Sanity check
        assert not document.parse_messages, '\n'.join(map(str,
            document.parse_messages))
        assert not document.transform_messages, '\n'.join(map(str,
            document.transform_messages))
        # Populate with transforms.
        for tclass, storage in self.extractors:
            document.transformer.add_transform(
                tclass, unid=source_id, storage=storage,
                pickle_receiver=pickle_receiver)
        # Create an appropriate reporter.
        if overrides:
            #prsr = frontend.OptionParser(specs=(self, self.Reader, self.)
            # XXX: parser allows update of list attrs
            document.settings.update(overrides)#, prsr)
        document.reporter = utils.new_reporter('', document.settings)
        # Run extractor transforms on the document tree.
        document.transformer.apply_transforms()
        # clean doc
        if document.transform_messages:
            print 'document transformed', document.transform_messages
        document.transform = document.reporter = document.form_processor = None
        # FIXME: what about when FP needs run during process i.o. build?
        # what about values from FP then..
        #print 'Extractor messages:', map(str,document.transform_messages)

    def render(self, source, source_id='<render>', writer_name=None,
            overrides={}, parts=['whole']):
        """
        Invoke writer by name and return parts after publishing.        
        """
        writer_name = writer_name or self.default_writer
        assert writer_name
        self.writer = comp.get_writer_class(writer_name)()
        logger.info('Rendering %r as %r with parts %r.', source_id, writer_name, parts)
        assert not overrides
        #logger.info("source-length: %i", not source or len(source))
        document = self.build(source, source_id)
        #logging.info(overrides)
        #parts = ['html_title', 'script', 'stylesheet']
        #logger.info("output-length: %i", not output or len(output))
        #logger.info([(part, self.writer.parts.get(part)) for part in parts])
        logger.info("Deps for %s: %s", source_id, self.document.settings.record_dependencies)
        # XXX: right to the internal of the writer. Is this interface?
        assert parts
        results = [ p for p in [ 
            self.writer.parts.get(part) for part in parts ] if p ]
        if results:
            return ''.join(results)

    def render_fragment(self, source, source_id='<render_fragment>',
            overrides={}):
        """
        HTML only, return body fragment (without body container).
        """
        return self.render(source, source_id, writer_name=None,
                parts=['html_title', 'body'], overrides=overrides)

    # for reference, HTML-writer parts:
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

    def prepare_source(self, source, source_path=None):
        """
        This (re)sets self.source_class using some argument indpection.

        Source can be a string or a docutils document instance, 
        when source_path=None, the string is tested as filename too.

        The keyword source_path can set a path location explicitly to prepare
        for file input. 
        The source may be None or loaded already no matter in this case.
        Setting it to a string or False bypasses the filesystem check.
        source_path may be always provided to provide the global ID of the
        source.
        """
        reader, parser = None, None
        if isinstance(source, docutils.nodes.document):
            assert source_path, "Need an ID, not %r" % source_path
            logger.info("ReReading %s", source_path)
            # Reread document
            self.source_class = docutils.io.DocTreeInput
            parser = comp.get_parser_class('null')()
            reader = self.ReReader(self.parser)
            if source.parse_messages:
                map(lambda x:logger.info(x.astext()),
                    source.parse_messages)
            if source.transform_messages:
                map(lambda x:logger.info(x.astext()),
                    source.transform_messages)
            self.settings = source.settings
        # XXX: would be nicer to have some 'file' resolver here. this
        # introduces dep on os
        #  local paths are made up of max. 255 chararacter names usally
        # not sure about depth. Linux takes a conservative 4096, windows a
        # whopping 15bits to count the total length
        elif source and (
                 ( source_path and isinstance(source_path, bool) )
                 or not source_path
            ) and ( 
                source and len(source) < 4097 and os.path.exists(source)):
            self.source_class = docutils.io.FileInput
            self.source_id = source
        else: 
            if not source:
                assert source_path
                self.source_class = docutils.io.FileInput
            else:
                if source_path:
                    assert isinstance(source_path, basestring)
                self.source_class = docutils.io.StringInput 
        if source_path and not isinstance(source_path, bool):
            self.source_id = source_path
        else:
            assert source, "Need source to build, source is %r" % source
        if not parser:
            source_class = docutils.io.FileInput#StringInput 
            parser = self.Parser()
        if not reader:
            reader = self.Reader(parser=self.parser)
        self.reader = reader
        self.parser = parser
        return self.source_class, self.parser, self.reader, self.settings 

    def __str__(self):
        return type(self).__module__+'.'+type(self).__name__

    #def __keep_messages(self):
    #    " "
    #    # Errors from conversion to document tree.
    #    if 'warning_stream' not in self.overrides:
    #        self.overrides['warning_stream'] = self.build_warnings
    #    else:
    #        logger.info("TODO: open or keep filelike warning_stream %s",
    #                self.overrides['warning_stream'])

def parse_params(args, kwds, options):
    for i, a in enumerate(args):
        if callable(a):
            args[i] = a(options)
    for k, v in kwds.items():
        if callable(v):
            kwds[k] = v(options)
    return args, kwds

