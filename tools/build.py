#!/usr/bin/env python
"""
A simple executable script to create new docutils publishers without coding new
files. Symlink this script, using a name that indicates the docutils Reader, Parser 
and Writer component to use.

E.g. use::

  [<source-format>2]<target-format>[-<tag>] [docutils publishing options]
  [<source-format>-]proc-<tag> [docutils processing options]

This uses the CLI functions from ``dotmpe.du.frontend``. 

More genericly the script name format is::

  [<source-format>[2<target-format>]-][<action>][-<tag>] [options]

As illustrated, at least `target-format` or `tag` must be used in the script name.

The `tag` part influences which components will be used, it defaults to 'mpe'.
The output format defaults to 'pprint', which in practice will be set to 
something like 'latex' or 'html'. 

Action defaults to 'pub', but may also be 'proc'. Note it does not make sense to 
have a target format for a document processing command.

The source and target format map to Parser and Writer aliases as expected,
with the addition that the '-<tag>' suffixed alias has priority. Ie. for
`target-format` 'xml' the 'xml-mpe' aliases Writer will be loaded if it
exists, else the 'xml' alias is used. Likewise for the Parser component.
The Reader component's alias is '<tag>' if that exists, but is otherwise set
to the standard Du 'standalone' Reader.

Additionally the source format 'mime' is available for RFC 2822 structured
rST files.

E.g. easily have a custom publisher for standard Du components::

    rst2xml-pep
    rst2rst
    rst2rst-mpe

XXX: not all parser/reader pairs will work. Likewise not all documents with every writer.
"""
import os
import sys

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
    locale.setlocale(locale.LC_CTYPE, '')
except:
    pass

from dotmpe.du import frontend, comp
import dotmpe.du.ext # register extensions


description = ('')
actions = ('proc','pub','render')

# defaults
tag = 'mpe'
source_format = 'rst'
target_format = 'pseudoxml'
action = 'pub'

# parse script name
script_names = os.path.basename(sys.argv[0]).split('-')
if '2' in script_names[0]:
    source_format, target_format = script_names.pop(0).split('2')
elif script_names[0] in actions:
    action = script_names.pop(0)
elif script_names[0] == 'build.py':
    pass
else:
    target_format = script_names.pop(0)
if script_names:
    tag = script_names.pop(0)
if script_names:
    action = script_names.pop(0)

# only use tag-suffixed comp alias if available
reader_name = tag
if reader_name not in comp.readers:
    print "Unknown", reader_name, "Using default reader 'standalone'"
    reader_name = 'standalone'
parser_name = "%s-%s" % (source_format, tag)
if parser_name not in comp.parsers:
    parser_name = source_format
writer_name = "%s-%s" % (target_format, tag)
if writer_name not in comp.writers:
    writer_name = target_format

module_name = tag
if not '.' in module_name:
    module_name = 'dotmpe.du.builder.'+tag


# print debug info
if '--debug-du-fe' in sys.argv:
    sys.argv.remove('--debug-du-fe')
    print >>sys.stderr, """source_format: %s
target_format: %s,
tag: %s,
action: %s""" % (source_format, target_format, tag, action)
    print >>sys.stderr, """reader_name: %s,
parser_name: %s,
writer_name: %s""" % (reader_name, parser_name, writer_name)

# Main
if source_format == 'mime':
    parser = comp.get_parser_class('rst')(rfc2822=1)
else:
    parser = comp.get_parser_class(parser_name)()

if action == 'proc':
    assert target_format == 'pseudoxml'
    # TODO: use source_format
    frontend.cli_process(sys.argv[1:], 'dotmpe.du.builder.'+tag)
    #frontend.cli_process(
    #        sys.argv[1:], builder_name=module_name)

elif action == 'pub':
    frontend.cli_render(
            sys.argv[1:], builder_name=module_name)

elif action == 'dupub':
    frontend.cli_du_publisher(
            reader_name=reader_name,
            parser=parser,
            writer_name=writer_name, 
            description=description)

