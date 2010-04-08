import os
import sys
from docutils import Component, core, SettingsSpec
from docutils.frontend import OptionParser

from gate import content, comp


version = '0.1'
dates = '2009',

default_description =  "Gate - Host-wide hypertext (%s) [%s]" % ( version, ', '.join(dates))

default_reader = 'standalone' #gate'
default_parser = 'rst'
default_writer = 'html4css1'

default_spec = (
        'Paperlib main',
        "Settings used in constructing the docutils publisher.",
          (
           ('Reader',
            ['--reader'],
            {'dest': 'reader_name', 'default': default_reader }),
           ('Reader module',
            ['--reader-module'],
            {'dest': 'reader_module' }),
           ('Parser',
            ['--parser'],
            {'dest': 'parser_name', 'default': default_parser }),
           ('Parser module',
            ['--parser-module'],
            {'dest': 'parser_module' }),
           ('Writer',
            ['--writer'],
            {'dest': 'writer_name', 'default': default_writer }),
           ('Writer module',
            ['--writer-module'],
            {'dest': 'writer_module' }),

           ('Source ID',
            ['--source-id'],
            {'dest': 'source_id' }),
           ('Source mediatype',
            ['--source-media'],
            {'dest': 'source_media' }),
           ('Source language',
            ['--source-language'],
            {'dest': 'source_language' }),
           ('Destination ID',
            ['--destination-id'],
            {'dest': 'destination-id' }),
          )
        )


def get_option_parser(components,
        usage="Gate [options] [source [destination]]",
        description=default_description,
        settings_spec=None, options=default_spec,
        read_config_files=1, **defaults):

    if not settings_spec:
        settings_spec = SettingsSpec()
        settings_spec.settings_spec = options
    settings_spec.config_section = 'test-section'

    option_parser = OptionParser( components=tuple(components) + (settings_spec,),
        defaults=defaults, read_config_files=1,
        usage=usage, description=description)
    return option_parser


def publish(usage=None, description=default_description, argv=[],
        reader_name=default_reader, parser_name=default_parser,
        writer_name=default_writer, enable_exit_status=None):

    """
    Run DU Publisher with Gate extensions.
    """

    # XXX: source and destinations have no exposed settings
    components = [
            comp.get_reader(reader_name),
            comp.get_parser(parser_name),\
            comp.get_writer(writer_name)]

    option_parser = get_option_parser(components, usage=usage,
            description=description)

    # Pre-parse argv, override programmatic reader/parser/writer
    settings = None
    if argv:
        settings = option_parser.parse_args(argv)

        #settings._source, settings._destination

        #srcref = ref.resolve_local(settings._source, pwd)
        #or
        #ref.resolve_http()


        #src_descr = content.get_descriptor(FileSystem, srcref, *opts)

        #FileSystem.get_descriptor(srcref)
        #Host.get_descriptor(srcref)
        #Gate.get_descriptor(srcref)


    if settings:
        # Reload components
        reset = False
        if reader_name != settings.reader_name:
            reader_name = settings.reader_name
            components[0] = gate.get_reader(reader_name)
            reset = True
        if parser_name != settings.parser_name:
            parser_name = settings.parser_name
            components[1] = gate.get_parser(parser_name)
            reset = True
        if writer_name != settings.writer_name:
            writer_name = settings.writer_name
            components[2] = gate.get_writer(writer_name)
            reset = True
        if reset:
            settings = None

    if not settings:
        # Re-parse argv based on new component config
        option_parser = get_option_parser(components, usage=usage,
                description=description)
        settings = option_parser.parse_args(argv)

    if not settings.source_id:
        option_parser.error('Too few arguments, specify at least a source using '
                '"-" or locator. See --help.')

    # init DU Publisher
    reader_class, parser_class, writer_class = components
    parser = parser_class()
    publisher = core.Publisher(reader_class(parser), parser, writer_class())
    publisher.settings = settings

#    store = Paperstore.load()

    output = publisher.publish(enable_exit_status=enable_exit_status)


default_usage = '%prog [options] [<source> [<destination>]]'

def main(argv=[], usage=default_usage, description=default_description,
        adapter=None):

    "Run the publisher."

    option_parser = get_option_parser((), usage=usage,
            description=description)

    settings = None
    if not argv:
        option_parser.error('No arguments')

    settings = option_parser.parse_args(argv)

    src_ref = settings._source
    dest_ref = settings._destination

    # Get adapter and initialize source and destination

    if not adapter:
        adapter = content.Host.factory(os.getcwd())

    source = adapter.find(src_ref)
    destination = adapter.find(dest_ref)

    print source, destination

    # Publish from source to destination

    p


def publish_programatically(src_ref='README.rst', src_class=content.DUDocTree,
        src_adapter=None,
        dest_ref='README.html', dest_class=content.DUDocTree, dest_adapter=None):
    """
    """



def main_interactive(**kwds):
    try:
        main(**kwds)
    except KeyboardInterrupt, e:
        print >>sys.stderr, e.__class__.__name__


cli_description = ('Reads from <source> (default is stdin) and writes to '
                       '<destination> (default is stdout).  See '
                       '<http://docutils.sf.net/docs/user/config.html> for '
                       'the full reference.')

def cli_main(usage=default_usage, description=cli_description, argv=[]):

    "Invoke to run as command-line shell stdproc."

    if not argv:
        argv = sys.argv[1:]

    main_interactive(usage=usage, description=description, argv=argv)


cgi_usage = '%prog?spec=value"'
cgi_description = ''

def cgi_main(usage=cgi_usage, description=cgi_description, argv=[]):

    "Invoke to run as HTTP resource in CGI envorionment."

    main(usage=usage, description=description, argv=[])





