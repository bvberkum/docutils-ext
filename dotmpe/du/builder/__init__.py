# $Id$
"""
Builders are preconfigured sets of Reader, Parser, Extractor and Writer components.

The goal is to have a component interface for multiple input and output formats,
perhaps to experiment with content-negotiation later. Until then this serves as
as a thin wrapper to the Du publisher framework.
"""
import os
import sys
import traceback
import logging
import types
import StringIO

import docutils.core
from docutils.core import Publisher
from docutils import SettingsSpec, frontend, utils, transforms
import sqlite3

#import nabu
#import nabu.server
import dotmpe
from dotmpe.du.util import get_session, SqlBase
from dotmpe.du import comp, util


logger = util.get_log(__name__)#, stdout=True, fout=False)

class Builder(SettingsSpec, Publisher):

    """
    Each builder is a static configuration of Docutils and Nabu components.
    Usefull during development of new docutils publisher chains.

    Behind it are Du Publisher and Nabu data extraction routines.
    This implementation tries to stay close to the publisher, but adds
    the routines needed for process documents from the command line without
    rendering. It does not borrow much of Nabu except the Extractor
    interface/base-class.

    Like the du publisher, it retrieves settings from the commandline arguments
    using process_command_line.

    For further ease of development, there is a third exec mode besides
    rendering or processing: interactive. This aims to relieve the
    argv parser of schemes for switching between modes of operations (or
    vary chain configurations). TODO use the extra level of interpretation
    to try to
    reach Builders original goals (see Blue-Lines for unfinished prior art).

    See the frontend module for how to use the builder.
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

    extractor_spec = ()
    ""

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
        # XXX render initializes again, but we want to see the help too...
        self.writer = comp.get_writer_class(self.default_writer)()
        # FIXME: having initial writer component enables publisher src2trgt frontends
        self.components = (self.parser, self.reader, self.writer, self)

        # XXX: for now, all transforms are linked to the reader and the reader
        # gets its transforms from there.
        # The extractors could similary depend on the Builder to get its specs
        # into the parser. at least it makes it work, but it'll be nice to be
        # able to concatenate several groups


    # XXX docutils.core.Publisher override (no changes, just for ref.)
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

    def prepare(self, argv=None, **store_params):
        """
        After settings and components are determined, prepare extractors.
        XXX should prepare reader/parser/writer here too.
        Source is prepared later, it is reset upon every build.
        """
        self.prepare_extractors(**store_params)

    def build(self, source, source_id='<build>', overrides={}, cli=False):
        """
        Build document from source, returns the document.
        This is used before a process or render.

        TODO: Use Reader, Parser, Transform and Builder for option spec.
        """
        logger.debug("Building %r.", source_id)
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
        assert self.source or os.path.exists(self.source_id)
        if 'halt_level' not in self.settings_default_overrides:
            self.settings.halt_level = 0
        if 'report_level' not in self.settings_default_overrides:
            self.settings.report_level = 6

        # FIXME: check settingspec defaults
        #if 'warning_stream' not in self.settings_default_overrides:
        if not hasattr(self.settings, 'warning_stream'):
            self.settings.warning_stream = StringIO.StringIO()
        if not hasattr(self.settings, 'debug'):
            self.settings.debug = False
        for key in "input_encoding output_encoding error_encoding".split(' '):
            if not hasattr(self.settings, key):
                setattr(self.settings, key, 'utf-8')
        if not hasattr(self.settings, 'error_encoding_error_handler'):
            setattr(self.settings, 'error_encoding_error_handler', 'replace')

        # FIXME proper config init
        self.settings.output_encoding_error_handler = 'backslashreplace'
        self.settings.tab_width = 4
        self.settings.language_code = 'en_US'
        self.settings.pep_references = False
        self.settings.rfc_references = False
        self.settings.smart_quotes = ''
        self.settings.id_prefix = ''
        self.settings.character_level_inline_markup = ''

        # XXX
        #from dotmpe.du.frontend import get_option_parser
        #option_parser = get_option_parser(
        #        self.components, usage='Builder testing: build [options] ..',
        #        settings_spec=None, read_config_files = 0)
        #self.settings = option_parser.get_default_values()
        source = self.source_class(
            source=self.source, source_path=self.source_id)
        if not hasattr(self.settings, '_destination'):
            self.settings._destination = None
        self.set_destination()
        # FIXME:  encoding=self.settings.input_encoding)
        self.document = self.reader.read(source, self.parser, self.settings)
        self.document.transformer.populate_from_components(
            (source, self.reader, self.parser, self.writer, self.destination))
        self.document.transformer.apply_transforms()
        return self.document

    def build_doc(self):
        pass

    def init_extractors(self):
        """
        Load extractor and storage classes from modules.
        Populate self.extractors with pairs of extractor/storage classes
        from clss.extractor_spec
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

        #session = get_session(self.settings.dbref, True)
        #self.init_extractors()
        #SqlBase.metadata.reflect(SqlBase.metadata.bind)

        for idx, (xcls, xstore) in enumerate(self.extractors):
            # XXX initialize extractor
            #xcls.init_parser(xcls)
            # reinitialize store

            #try:
            #    self.extractors[i] = [ xcls , xstore(session=session) ]
            #except Exception, e:
            #    raise Exception("Failed initializing %s for %s" % (
            #        storage, extractor ), e)

            if type(xstore) != type and type(xstore) != types.InstanceType:
                assert isinstance(xstore, types.ClassType)
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
        # Sanity check assert not document.parse_messages, '\n'.join(map(str, document.parse_messages))
        if document.parse_messages:
# print 'Parser messages:', map(str,document.parse_messages)
            for msg in document.parse_messages:
                #if msg.get('level') > 2: # 3=ERROR
                if msg.get('level') > 3: # 4=
                    assert not msg, msg
        assert not document.transform_messages, '\n'.join(map(str,
            document.transform_messages))
        # Populate with transforms.
        print self, self.extractors
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
        # what about values from FP then.
        if document.transform_messages:
            print 'Transformation messages:', map(str,document.transform_messages)

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
        output = self.writer.write(document, self.destination)
        return output

        print output
        assert self.writer.parts
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
        This (re)sets self.source_class using some argument inspection.

        Source should be either a string or a docutils document instance,
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

        elif source_path:
            if isinstance(source_path, basestring) and os.path.exists(source_path):
                self.source_path = source_path
                self.source_class = docutils.io.FileInput
            self.source_id = source_path

        elif source and os.path.exists(source):
            self.source_class = docutils.io.FileInput
            self.source = None
            self.source_id = source

        elif source:
            if isinstance(source, str):
                source = unicode(source)
            assert isinstance(source, unicode), type(source)
            self.source = source
            self.source_class = docutils.io.StringInput

        else:
            assert source, "Need source to build"

        if not parser:
            parser = self.Parser()

            self.parser = parser

        if not reader:
            reader = self.Reader(parser=self.parser)

            self.reader = reader

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

    ###

    # XXX not sure yet of some interpreted Builder mode,
    #   but it should be a nice exercise in getting the publisher cycle right

    def interactive(self, argv):
        raise NotImplementedError

    def read_script(self, argv):
        raise NotImplementedError

    def reset_schema(self, argv):
        self.prepare_initial_components()
        self.process_command_line(argv=argv)
        # XXX self.prepare(None, **self.store_params)
        session = get_session(self.settings.dbref, True)
        conn = SqlBase.metadata.bind.raw_connection()
        self.init_extractors()

        for extractor, storage in self.extractors:
            store = storage(session=session)
            store.connection = conn
            try:
                store.reset_schema()
            except sqlite3.OperationalError, e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                e.info = sys.exc_info()
                logger.error( "Error in extractor SQL %r: %s" % (storage, e) )
                raise e


    ### XXX Builder frontend/programatic work in progress

# TODO need to relieve extractors of db connection layer.
#   current prepare() is not adequate

    def _do_process(self):
        # XXX Builder.process self.set_io()
        source_id = self.settings._source
        source = open(source_id)

        print '_do_process', source, source_id
        from pprint import pprint
        pprint(self.settings)

        logger.info("Loaded, building %s" % source_id)

        document = self.build(source, source_id, overrides={})

        logger.info("Built document")

        self.prepare(None, **self.store_params)

        logger.info("Prepared extractors")

        self.process(document, source_id, overrides={}, pickle_receiver=None)

        logger.info("Processed document")

        # TODO render messages as reST doc
        for msg_list in document.parse_messages, document.transform_messages:
            for msg in msg_list:
                #print type(msg), dir(msg)
                #print msg.asdom()
                print msg.astext()



# XXX: prep store-params
def parse_params(args, kwds, options):
    for i, a in enumerate(args):
        if callable(a):
            args[i] = a(options)
    for k, v in kwds.items():
        if callable(v):
            kwds[k] = v(options)
    return args, kwds

