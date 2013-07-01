# $Id$
"""
Builders are preconfigured sets of Reader, Parser, Extractor and Writer components.

The goal is to have a component interface for multiple input and output formats,
perhaps to experiment with content-negotiation later. Until then this serves as
as a thin wrapper to the Du publisher framework.
"""
import logging
import types
import StringIO
import docutils.core

from docutils import SettingsSpec, frontend, utils, transforms

#import nabu
#import nabu.server
import dotmpe
from dotmpe.du import comp, util


logger = logging.getLogger('dotmpe.du.builder')

class Builder(SettingsSpec):

    """
    Each builder is a configuration of Docutils and Nabu components.

    It is a facade to build document trees from source, and to render or process
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
    default_writer = 'dotmpe-html'

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

    extractors = [] # list of (transform, storage) type pairs
    """
    Transforms that are run during `process`. See Nabu for their interface.
    The stores may be left uninitialized until `prepare`.
    """

    def build(self, source, source_id='<build>', overrides={}):
        """
        Build document from source, returns the document.
        """
        logger.debug("Building %r.", source_id)
        output, self.publisher = self.__publish(source, source_id, None,
                overrides)
        return self.publisher.document

    def init_extractors(self):
        """
        Load extractor and storage classes from modules.
        """
        import dotmpe.du.ext.extractor
        for spec in self.extractor_spec:
            if len(spec) > 1:
                storage_module = spec[1]
            else:
                storage_module = spec[0]
            self.extractors.append(
                    (comp.get_extractor_class(spec[0]),
                        comp.get_extractor_storage_class(storage_module))
                )

    def prepare(self, **store_params):
        """
        Initialize or reset the extractors and storages. `store_params` provides
        arguments for constructing the storages by type. Note that storages per
        definition work on multiple documents. Only use this to reset in-memory
        stores or before calling `process` the first time.
        """
        if not self.extractors and self.extractor_spec:
            self.init_extractors()
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
                args, kwds = store_params.get(xstore.__name__, ((),{}))
                try:
                    xstore = xstore(*args, **kwds)
                except TypeError, e:
                    logger.error(e)
                    raise TypeError, "Error instantiating storage %r,  "  % xstore
            self.extractors[idx] = (xcls, xstore)

    def process(self, document, source_id='<process>', overrides={},
            pickle_receiver=None):
        """
        If there are extractors for this builder, apply them to the document. 
        TODO: Return messages.

        `prepare` should have been run to initialize storages. 
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
        writer = comp.get_writer_class(writer_name)()
        logger.info('Rendering %r as %r.', source_id, writer_name)
        #logger.info("source-length: %i", not source or len(source))
        output, pub = self.__publish(source, source_id, writer, overrides)
        self.parts = pub.writer.parts
        #logging.info(overrides)
        #parts = ['html_title', 'script', 'stylesheet']
        #logger.info("output-length: %i", not output or len(output))
        #logger.info([(part, self.parts.get(part)) for part in parts])
        logger.info("Deps for %s: %s", source_id, pub.document.settings.record_dependencies)
        return ''.join([self.parts.get(part) for part in parts])

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

    # Builder Du core
    def __publish(self, source, source_path, writer, overrides={}):
        assert source, "Need source to build, not %s" % source
        if isinstance(source, docutils.nodes.document):
            logger.info("ReReading %s", source_path)
            # Reread document
            source_class = docutils.io.DocTreeInput
            parser = comp.get_parser_class('null')()
            reader = self.ReReader(parser)
            if source.parse_messages:
                map(lambda x:logger.info(x.astext()),
                    source.parse_messages)
            if source.transform_messages:
                map(lambda x:logger.info(x.astext()),
                    source.transform_messages)
            settings = source.settings                
        else: # Read from source
            source_class = docutils.io.StringInput 
            parser = self.Parser()
            reader = self.Reader(parser=parser)
            settings = None
        if not writer:
            writer = comp.get_writer_class('null')()
        #settings = None # TODO: reuse (but needs full component (r/p/w) config!)
        assert not settings or isinstance(settings, frontend.Values)
        destination_class = docutils.io.StringOutput
        logger.info("Publishing %r (%s, %s, %s)", 
                source_path, *map(util.component_name, (reader, parser, writer)))
        output, pub = docutils.core.publish_programmatically(
            source_class, source, source_path, 
            destination_class, None, None,
            reader, str(self)+'.Reader',
            parser, str(self)+'.Parser',
            writer, str(self)+'.Writer',
            settings, self,
            overrides, config_section=None, enable_exit_status=False)
        return output, pub

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



