"""
Offers an variant on the DU publisher?
"""

#import sys
#import pprint
#from types import StringType
#from docutils import __version__, __version_details__, SettingsSpec
#from docutils import frontend, io, utils, readers, writers
#from docutils.frontend import OptionParser
#from docutils.transforms import Transformer
#import docutils.readers.doctree


class Publisher:

    """
    Like docutils.core.Publisher, a facade encapsulating the high-level logic of
    the Docutils publication system.

    """

    def __init__(self, reader=None, parser=None, writer=None,
                 source=None, source_class=io.FileInput,
                 destination=None, destination_class=io.FileOutput,
                 settings=None):
        """
        Initial setup.  If any of `reader`, `parser`, or `writer` are not
        specified, the corresponding ``set_...`` method should be called with
        a component name (`set_reader` sets the parser as well).
        """

        self.document = None
        """The document tree (`docutils.nodes` objects)."""

        self.reader = reader
        """A `docutils.readers.Reader` instance."""

        self.parser = parser
        """A `docutils.parsers.Parser` instance."""

        self.writer = writer
        """A `docutils.writers.Writer` instance."""

        for component in 'reader', 'parser', 'writer':
            assert not isinstance(getattr(self, component), StringType), (
                'passed string "%s" as "%s" parameter; pass an instance, '
                'or use the "%s_name" parameter instead (in '
                'docutils.core.publish_* convenience functions).'
                % (getattr(self, component), component, component))

        self.source = source
        """The source of input data, a `docutils.io.Input` instance."""

        self.source_class = source_class
        """The class for dynamically created source objects."""

        self.destination = destination
        """The destination for docutils output, a `docutils.io.Output`
        instance."""

        self.destination_class = destination_class
        """The class for dynamically created destination objects."""

        self.settings = settings
        """An object containing Docutils settings as instance attributes.
        Set by `self.process_command_line()` or `self.get_settings()`."""

    def set_reader(self, reader_name, parser, parser_name):
        """Set `self.reader` by name."""
        reader_class = readers.get_reader_class(reader_name)
        self.reader = reader_class(parser, parser_name)
        self.parser = self.reader.parser

    def set_writer(self, writer_name):
        """Set `self.writer` by name."""
        writer_class = writers.get_writer_class(writer_name)
        self.writer = writer_class()

    def set_components(self, reader_name, parser_name, writer_name):
        if self.reader is None:
            self.set_reader(reader_name, self.parser, parser_name)
        if self.parser is None:
            if self.reader.parser is None:
                self.reader.set_parser(parser_name)
            self.parser = self.reader.parser
        if self.writer is None:
            self.set_writer(writer_name)

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
        option_parser = OptionParser(
            components=(self.parser, self.reader, self.writer, settings_spec),
            defaults=defaults, read_config_files=1,
            usage=usage, description=description)
        return option_parser

    def get_settings(self, usage=None, description=None,
                     settings_spec=None, config_section=None, **defaults):
        """
        Set and return default settings (overrides in `defaults` dict).

        Set components first (`self.set_reader` & `self.set_writer`).
        Explicitly setting `self.settings` disables command line option
        processing from `self.publish()`.
        """
        option_parser = self.setup_option_parser(
            usage, description, settings_spec, config_section, **defaults)
        self.settings = option_parser.get_default_values()
        return self.settings

    def process_programmatic_settings(self, settings_spec,
                                      settings_overrides,
                                      config_section):
        if self.settings is None:
            defaults = (settings_overrides or {}).copy()
            # Propagate exceptions by default when used programmatically:
            defaults.setdefault('traceback', 1)
            self.get_settings(settings_spec=settings_spec,
                              config_section=config_section,
                              **defaults)

    def process_command_line(self, argv=None, usage=None, description=None,
                             settings_spec=None, config_section=None,
                             **defaults):
        """
        Pass an empty list to `argv` to avoid reading `sys.argv` (the
        default).

        Set components first (`self.set_reader` & `self.set_writer`).
        """
        option_parser = self.setup_option_parser(
            usage, description, settings_spec, config_section, **defaults)
        if argv is None:
            argv = sys.argv[1:]
        self.settings = option_parser.parse_args(argv)

    def set_io(self, source_path=None, destination_path=None):
        if self.source is None:
            self.set_source(source_path=source_path)
        if self.destination is None:
            self.set_destination(destination_path=destination_path)

    def set_source(self, source=None, source_path=None):
        if source_path is None:
            source_path = self.settings._source
        else:
            self.settings._source = source_path
        self.source = self.source_class(
            source=source, source_path=source_path,
            encoding=self.settings.input_encoding)

    def set_destination(self, destination=None, destination_path=None):
        if destination_path is None:
            destination_path = self.settings._destination
        else:
            self.settings._destination = destination_path
        self.destination = self.destination_class(
            destination=destination, destination_path=destination_path,
            encoding=self.settings.output_encoding,
            error_handler=self.settings.output_encoding_error_handler)

    def apply_transforms(self):
        self.document.transformer.populate_from_components(
            (self.source, self.reader, self.reader.parser, self.writer,
             self.destination))
        self.document.transformer.apply_transforms()

    def publish(self, argv=None, usage=None, description=None,
                settings_spec=None, settings_overrides=None,
                config_section=None, enable_exit_status=None):
        """
        Process command line options and arguments (if `self.settings` not
        already set), run `self.reader` and then `self.writer`.  Return
        `self.writer`'s output.
        """
        exit = None
        try:
            if self.settings is None:
                self.process_command_line(
                    argv, usage, description, settings_spec, config_section,
                    **(settings_overrides or {}))
            self.set_io()
            self.document = self.reader.read(self.source, self.parser,
                                             self.settings)
            self.apply_transforms()
            output = self.writer.write(self.document, self.destination)
            self.writer.assemble_parts()
        except SystemExit, error:
            exit = 1
            exit_status = error.code
        except Exception, error:
            if not self.settings:       # exception too early to report nicely
                raise
            if self.settings.traceback: # Propagate exceptions?
                self.debugging_dumps()
                raise
            self.report_Exception(error)
            exit = 1
            exit_status = 1
        self.debugging_dumps()
        if (enable_exit_status and self.document
            and (self.document.reporter.max_level
                 >= self.settings.exit_status_level)):
            sys.exit(self.document.reporter.max_level + 10)
        elif exit:
            sys.exit(exit_status)
        return output

    def debugging_dumps(self):
        if not self.document:
            return
        if self.settings.dump_settings:
            print >>sys.stderr, '\n::: Runtime settings:'
            print >>sys.stderr, pprint.pformat(self.settings.__dict__)
        if self.settings.dump_internals:
            print >>sys.stderr, '\n::: Document internals:'
            print >>sys.stderr, pprint.pformat(self.document.__dict__)
        if self.settings.dump_transforms:
            print >>sys.stderr, '\n::: Transforms applied:'
            print >>sys.stderr, (' (priority, transform class, '
                                 'pending node details, keyword args)')
            print >>sys.stderr, pprint.pformat(
                [(priority, '%s.%s' % (xclass.__module__, xclass.__name__),
                  pending and pending.details, kwargs)
                 for priority, xclass, pending, kwargs
                 in self.document.transformer.applied])
        if self.settings.dump_pseudo_xml:
            print >>sys.stderr, '\n::: Pseudo-XML:'
            print >>sys.stderr, self.document.pformat().encode(
                'raw_unicode_escape')

    def report_Exception(self, error):
        if isinstance(error, utils.SystemMessage):
            self.report_SystemMessage(error)
        elif isinstance(error, UnicodeError):
            self.report_UnicodeError(error)
        else:
            print >>sys.stderr, '%s: %s' % (error.__class__.__name__, error)
            print >>sys.stderr, ("""\
Exiting due to error.  Use "--traceback" to diagnose.
Please report errors to <docutils-users@lists.sf.net>.
Include "--traceback" output, Docutils version (%s [%s]),
Python version (%s), your OS type & version, and the
command line used.""" % (__version__, __version_details__,
                         sys.version.split()[0]))

    def report_SystemMessage(self, error):
        print >>sys.stderr, ('Exiting due to level-%s (%s) system message.'
                             % (error.level,
                                utils.Reporter.levels[error.level]))

    def report_UnicodeError(self, error):
        sys.stderr.write(
            '%s: %s\n'
            '\n'
            'The specified output encoding (%s) cannot\n'
            'handle all of the output.\n'
            'Try setting "--output-encoding-error-handler" to\n'
            '\n'
            '* "xmlcharrefreplace" (for HTML & XML output);\n'
            % (error.__class__.__name__, error,
               self.settings.output_encoding))
        try:
            data = error.object[error.start:error.end]
            sys.stderr.write(
                '  the output will contain "%s" and should be usable.\n'
                '* "backslashreplace" (for other output formats, Python 2.3+);\n'
                '  look for "%s" in the output.\n'
                % (data.encode('ascii', 'xmlcharrefreplace'),
                   data.encode('ascii', 'backslashreplace')))
        except AttributeError:
            sys.stderr.write('  the output should be usable as-is.\n')
        sys.stderr.write(
            '* "replace"; look for "?" in the output.\n'
            '\n'
            '"--output-encoding-error-handler" is currently set to "%s".\n'
            '\n'
            'Exiting due to error.  Use "--traceback" to diagnose.\n'
            'If the advice above doesn\'t eliminate the error,\n'
            'please report it to <docutils-users@lists.sf.net>.\n'
            'Include "--traceback" output, Docutils version (%s),\n'
            'Python version (%s), your OS type & version, and the\n'
            'command line used.\n'
            % (self.settings.output_encoding_error_handler,
               __version__, sys.version.split()[0]))



