"""
A simple front end for dotmpe.du Builder configurations and extensions to the
standard Docutils publisher.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass
import os
import sys
import traceback

from docutils.core import publish_cmdline
from docutils.parsers.rst import Parser
from docutils import Component, core, SettingsSpec, frontend
#import nabu.server
#import nabu.process

from dotmpe.du import comp, util
import dotmpe.du.ext
from dotmpe.du.ext.parser import Inliner


logger = util.get_log(__name__, fout_level=logging.INFO, stdout=True)


def cli_process(argv, builder=None, builder_name='mpe', description=''):

    """
    - Load builder for given name or use provided instance.

    Make one or more invocations to process for given source files,
    process will run all extractors of the given builder.

    - CLI arguments for subsequent calls are separated by '--'.

    TODO:
        Extractors should be initialized only once (ie. using initial options only).
        Settings are updated from additional options if provided.
        Ofcourse all other components should be reusable and/or reset appropiately.
    FIXME: does not merge settings between invokations
    """

    if not builder:
        Builder = comp.get_builder_class(builder_name, class_name='Builder')
        builder = Builder()

    # raises exception if no argv
    argvs = split_argv(argv)
    print('argv', argv)

    builder.prepare_initial_components()
    logger.info('cli-process components', builder.components)

    # replace settings for initial components
    builder.process_command_line(argv=argvs.next())

    # Rest deals with argv handling and defers to run_process (tmp)
    for argv in argvs:
        logger.info('cli-process', argv)

        # replace settings for initial components
        builder.process_command_line(argv=argv)

        builder._do_process()

    else:
        # No further args (or break but not using that)
        builder._do_process()


def cli_render(argv, builder=None, builder_name='mpe'):

    """
    Accept invocations to render documents from source to dest or
    stdout. Subsequent invocations should be separated by '--'.
    The initial group of arguments
    TODO: see cli_process.

    Setup publisher chain from builder class, and run them converting document(s)
    from source to dest.
    """

    if not builder:
        Builder = comp.get_builder_class(builder_name, class_name='Builder')
        builder = Builder()

    #argvs = split_argv(argv)

    builder.prepare_initial_components()
    # replace settings for initial components
    builder.process_command_line(argv=argv)#s.next())
    #pub.set_components(reader_name, parser_name, writer_name)
    #pub.process_programmatic_settings(
    #    settings_spec, settings_overrides, config_section)
    #pub.set_source(source, source_path)
    #pub.set_destination(destination, destination_path)
    #output = pub.publish(enable_exit_status=enable_exit_status)

    assert builder.settings
    print builder.render(None, builder.settings._source)
    print builder.document.parse_messages
    print builder.document.transform_messages


def cli_run(argv, stdin=None, builder=None, builder_name='mpe'):

    """
    Enter extended batch mode; read commands from stdin or readline.

    Using argv, this resolve the initial argument to a callable method
    of the builder and delegates further (argv/stdin) handling to it.

    This defaults to 'interactive', if no arguments are given and the stdin is
    connected to a terminal. For no-terminal without arguments it will try to run
    'read_script'.
    """

    if not stdin:
        stdin = sys.stdin

    if not builder:
        Builder = comp.get_builder_class(builder_name, class_name='Builder')
        builder = Builder()

    # connected to TTY session or redirected descriptor?

    argvs = None
    if argv:
        argvs = split_argv(argv)

    elif not stdin.isatty():
        builder.read_script()

    # run commands from argv

    for argv in argvs:
        # XXX very naively..
        if argv:
            cmd = argv.pop(0)
        else:
            cmd = 'interactive'

        try:
            getattr(builder, cmd)(argv)
        except Exception, e:

            logger.error( "Error in command handler %r: %s" % (cmd, e) )
            traceback.print_exc(sys.stderr)
            if hasattr(e, 'info'):
                traceback.print_exception(*e.info)


def cli_du_publisher(reader_name='mpe', parser=None, parser_name='rst',
        writer=None, writer_name='pseudoxml', description=''):

    """
    Simple wrapper for ``docutils.core.publish_cmdline``.
    During development, this should still be working.

    Shortcomings are it cannot load settings-specs from transforms,
    or perform processing only (without rendering).
    It does not handle stores for transforms directly as Nabu does.
    But, given that transforms could handle storage
    initialization themselves, and that the Reader/Parser/Writer 'parent'
    component can hold the settings-specs, should make it fairly easy to port
    Builder code back to work with vanilla docutils.
    """

    # XXX: how far does inline customization go? parser = Parser(inliner=Inliner())
    reader_class = comp.get_reader_class(reader_name)
    parser_class = None
    if not parser:
        parser_class = comp.get_parser_class(parser_name)
        parser = parser_class()
    if not writer:
        writer_class = comp.get_writer_class(writer_name)
        writer = writer_class()

    publish_cmdline(
            parser=parser,
            parser_name=parser_name,
            reader=reader_class(parser),
            reader_name=reader_name,
            writer=writer,
            writer_name=writer_name,
            description=description)


def split_argv(argv):
    """
    Split argv at '--', yield subsequent groups.

    If what would be the first group does not contain options (-f --flag..)
    then take it to be a separate group and yield an initial empty group.

    No other processing.
    """
    if not argv:
        raise Exception("Arguments expected (use --help)")

    try:
        argv_idx = argv.index('--')
    except ValueError, e:
        argv_idx = len(argv)

    if argv_idx == 0:
        # no initial options
        argv = argv[1:]
        argv_idx = argv.index('--')

    first = True

    while argv_idx and argv_idx != -1:
        argv_cur, argv = argv[0:argv_idx], argv[argv_idx+1:]

        if first:
            initial_options = False
            for x in argv_cur:
                if x.startswith('-'):
                    initial_options = True
            if not initial_options:
                yield []

        yield argv_cur

        try:
            argv_idx = argv.index('--')
        except ValueError, e:
            argv_idx = -1

        first = False





### XXX:BVB: rewrite Du ext frontend for builder
# old code for what would be an interface for du to run an HTTP server
# main interface and should be reused for Builder
#from gate import content, comp

version = '0.1'
dates = '2009',

default_description =  "Gate - Host-wide hypertext (%s) [%s]" % ( version, ', '.join(dates))

default_resolver = ''
default_reader = 'standalone' #gate'
default_parser = 'rst'
default_writer = 'html4css1'

default_spec = (
        'Publisher',
        "Settings used in constructing the publisher.",
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

    option_parser = frontend.OptionParser( components=tuple(components) + (settings_spec,),
        defaults=defaults, read_config_files=1,
        usage=usage, description=description)
    return option_parser



default_usage = '%prog [options] [<source> [<destination>]]'

def main(argv=[], usage=default_usage, description=default_description):

    " Run the publisher. "
# TODO: frontend.main, offer adapted version of ``docutils.core.publish_cmdline``.

    #option_parser = get_option_parser((), usage=usage,
    #        description=description)
    #settings = None
    #if not argv:
    #    option_parser.error('No arguments')
    #settings = option_parser.parse_args(argv)

#def publish_programatically(src_ref='README.rst', src_class=content.DUDocTree,
#        src_adapter=None,
#        dest_ref='README.html', dest_class=content.DUDocTree, dest_adapter=None):
#    """
#    """


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


