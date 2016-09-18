#!/usr/bin/env python
"""
A simple executable script to create new docutils publishers without coding new
files. Symlink this script, using a name that indicates the docutils Reader, Parser 
and Writer component to use.

E.g. use::

  [<source-format>2]<target-format>[-<tag>] [docutils publishing options]
  [<source-format>-]proc-<tag> [docutils processing options]

This uses the CLI functions from ``dotmpe.du.frontend``. 

Abstract
--------
Behind the scenes, docutils uses a component model with the primary elements
reader, parser and writer. Components have names and aliases, and also hold 
specifications of the settings they accept as parameters. 

This frontend supports two operations involving these: publish and process.

A publish operation involves a predefined reader and writer to convert a
document to a (target) format. 

The process invocation 

Name syntax
------------
More genericly the script name format is::

  [<source-format>[2<target-format>]-][<action>][-<tag>] [options]

.. XXX: should fix this, for now working with 
        tools/proc-dotmpe.du.builder.htdocs for publish

At least `target-format` or `tag` must be used.

The `tag` part specifies which components will be used, it defaults to 'mpe'
The output format defaults to 'pprint', which in practice will be set to 
something like 'latex' or 'html'. 

Action is the main mode which defaults to 'pub' for document-to-document
conversion, but may also be more generic 'proc'. Proc(essing) is used 
for anything on the document that analyses, extracts and/or transforms a
document. It does not make sense to have a target format for a document 
processing command. 

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

from dotmpe.du import util, frontend, comp
import dotmpe.du.ext # register extensions


description = ('')
actions = ('proc','pub','run')

# defaults
tag = 'mpe'
source_format = 'rst'
target_format = 'pseudoxml'
action = 'pub'

# parse script name
script_names = os.path.basename(sys.argv[0]).split('-')
# first part
if '2' in script_names[0]:
    source_format, target_format = script_names.pop(0).split('2')
elif script_names[0] in actions: # action- prefix
    action = script_names.pop(0)
elif script_names[0] == 'build.py': 
    pass
else:
    target_format = script_names.pop(0) # otherwise first part is target format
# second part: tag
if script_names: 
    tag = script_names.pop(0)
# second/third: action
if script_names:
    action = script_names.pop(0)

# only use tag-suffixed comp alias if available
reader_name = tag
if reader_name not in comp.readers:
    #print "Unknown reader '%s'" % reader_name, "Using default reader 'standalone'"
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
writer_name: %s,
builder_module: %s""" % (reader_name, parser_name, writer_name, module_name)

if source_format == 'mime':
    parser = comp.get_parser_class('rst')(rfc2822=1)
else:
    parser = comp.get_parser_class(parser_name)()

# Main

log = util.get_log(None, fout=False, stdout=True)

if action == 'proc':
    log.info("Starting Du processor: "+tag)
    assert target_format == 'pseudoxml'
    # TODO: use source_format
    #frontend.cli_process(
    #        sys.argv[1:], builder_name=module_name)
    frontend.cli_process(sys.argv[1:], None, 'dotmpe.du.builder.'+tag)
    #frontend.cli_process(
    #        sys.argv[1:], builder_name=module_name)

elif action == 'pub':
    log.info("Starting Du publish")
    frontend.cli_render(
            sys.argv[1:], builder_name=module_name)

elif action == 'run':
    log.info("Starting Du command")
    frontend.cli_run(
            sys.argv[1:], builder_name=module_name)

elif action == 'dupub':
    log.info("Starting standard publisher")
    frontend.cli_du_publisher(
            reader_name=reader_name,
            parser=parser,
            writer_name=writer_name,
            description=description)

